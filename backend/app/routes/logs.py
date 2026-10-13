import json
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.config import settings
from app.database import get_database
from app.parsers.registry import parser_registry
from app.services.ingest import build_event, ingest_log

router = APIRouter(prefix="/logs", tags=["Logs"])


def split_log_text(text: str) -> List[str]:
    """
    Splits uploaded text into individual raw log records.
    A whole-file JSON array / object is expanded into one record per element;
    everything else (plain logs, JSON Lines) is split by line.
    """
    stripped = text.strip()
    if stripped[:1] in ("[", "{"):
        try:
            data = json.loads(stripped)
        except ValueError:
            data = None
        if isinstance(data, list):
            return [json.dumps(item, ensure_ascii=False) for item in data if item not in (None, "", {})]
        if isinstance(data, dict):
            return [json.dumps(data, ensure_ascii=False)]
    return [line.strip() for line in text.splitlines() if line.strip()]


@router.post("/upload")
async def upload_log_file(file: UploadFile = File(...)):
    """
    Accepts raw log files (.log, .txt, .json, .csv), splits records,
    processes them through the ULPF pipeline, and records normalized events.
    """
    db = get_database()
    content = await file.read(settings.MAX_UPLOAD_BYTES + 1)
    if len(content) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"File exceeds the {settings.MAX_UPLOAD_BYTES // (1024 * 1024)} MB upload limit.")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    lines = split_log_text(text)
    if not lines:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    skipped = max(0, len(lines) - settings.MAX_UPLOAD_LINES)
    processed_events: List[dict] = []
    failed_lines: List[dict] = []
    processed_count = 0

    for idx, raw_log in enumerate(lines[:settings.MAX_UPLOAD_LINES]):
        parser, event_dict = ingest_log(db, raw_log)
        if event_dict:
            processed_count += 1
            if len(processed_events) < 10:
                processed_events.append(event_dict)
        else:
            failed_lines.append({"line_number": idx + 1, "raw": raw_log[:150]})

    return {
        "success": True,
        "filename": file.filename,
        "total_lines": len(lines),
        "processed_count": processed_count,
        "failed_count": len(failed_lines),
        "skipped_count": skipped,
        "truncated": skipped > 0,
        "processed_events": processed_events,  # preview of first 10
        "failed_samples": failed_lines[:5],
    }


@router.post("/analyze")
def analyze_log_preview(raw_log: str = Form(...)):
    """Previews format detection and normalization without database storage."""
    db = get_database()
    raw_log = raw_log.strip()
    parser, parsed_data = parser_registry.detect_and_parse(raw_log, db=db)
    if not parser or not parsed_data:
        return {
            "detected": False,
            "message": "Unsupported format. Use AI Parser Studio to onboard.",
            "parser": None
        }

    preview_event = build_event(parser, raw_log, parsed_data)

    return {
        "detected": True,
        "parser": parser.name,
        "vendor": parser.vendor,
        "format": parsed_data.get("format"),
        "confidence": preview_event.processing.confidence,
        "normalized_event": preview_event.model_dump()
    }
