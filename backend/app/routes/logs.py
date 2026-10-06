from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.database import get_database
from app.parsers.registry import parser_registry
from app.services.normalization import NormalizationService
from app.schemas.event import UniversalEvent

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.post("/upload")
async def upload_log_file(file: UploadFile = File(...)):
    """
    Accepts raw log files (.log, .txt, .json, .csv), splits lines,
    processes them through the ULPF pipeline, and records normalized events.
    """
    db = get_database()
    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    processed_events: List[dict] = []
    failed_lines: List[dict] = []

    for idx, raw_log in enumerate(lines[:500]): # Cap at 500 lines for prototype safety
        parser, parsed_data = parser_registry.detect_and_parse(raw_log, db=db)
        if parser and parsed_data:
            event = NormalizationService.to_universal_event(
                raw_log=raw_log,
                parsed_data=parsed_data,
                parser_name=parser.name,
                parser_version=getattr(parser, "version", "1.0.0"),
                confidence=getattr(parser, "confidence", 0.98),
                is_ai_assisted=not getattr(parser, "is_builtin", True)
            )
            event_dict = event.model_dump()
            db["events"].insert_one(event_dict)
            processed_events.append(event_dict)

            # Update source stats
            vendor = event.source.vendor or "Generic"
            db["sources"].update_one(
                {"vendor": vendor},
                {
                    "$inc": {"event_count": 1},
                    "$setOnInsert": {
                        "source_id": f"src_{vendor.lower().replace(' ', '_')}",
                        "name": f"{vendor} Ingest",
                        "format": event.source.format or "file",
                        "status": "active"
                    }
                },
                upsert=True
            )
        else:
            failed_lines.append({"line_number": idx + 1, "raw": raw_log[:150]})

    return {
        "success": True,
        "filename": file.filename,
        "total_lines": len(lines),
        "processed_count": len(processed_events),
        "failed_count": len(failed_lines),
        "processed_events": processed_events[:10], # Return preview of first 10
        "failed_samples": failed_lines[:5]
    }

@router.post("/analyze")
def analyze_log_preview(raw_log: str = Form(...)):
    """Previews format detection and normalization without database storage."""
    db = get_database()
    parser, parsed_data = parser_registry.detect_and_parse(raw_log.strip(), db=db)
    if not parser or not parsed_data:
        return {
            "detected": False,
            "message": "Unsupported format. Use AI Parser Studio to onboard.",
            "parser": None
        }

    preview_event = NormalizationService.to_universal_event(
        raw_log=raw_log.strip(),
        parsed_data=parsed_data,
        parser_name=parser.name,
        confidence=getattr(parser, "confidence", 0.98),
        is_ai_assisted=not getattr(parser, "is_builtin", True)
    )

    return {
        "detected": True,
        "parser": parser.name,
        "vendor": parser.vendor,
        "format": parsed_data.get("format"),
        "confidence": getattr(parser, "confidence", 0.98),
        "normalized_event": preview_event.model_dump()
    }
