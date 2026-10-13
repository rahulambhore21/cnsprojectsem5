from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from app.parsers.base import BaseParser
from app.parsers.registry import parser_registry
from app.schemas.event import UniversalEvent
from app.services.normalization import NormalizationService


def build_event(parser: BaseParser, raw_log: str, parsed_data: Dict[str, Any], source_hint: Optional[str] = None) -> UniversalEvent:
    """Normalizes parsed data using the parser's own metadata (version, confidence from parse result)."""
    if source_hint and (not parsed_data.get("vendor") or str(parsed_data["vendor"]).startswith("Generic")):
        parsed_data = {**parsed_data, "vendor": source_hint}
    return NormalizationService.to_universal_event(
        raw_log=raw_log,
        parsed_data=parsed_data,
        parser_name=parser.name,
        parser_version=getattr(parser, "version", "1.0.0"),
        is_ai_assisted=not getattr(parser, "is_builtin", True),
    )


def record_source_stats(db, event: UniversalEvent) -> None:
    """Upserts per-vendor source statistics for an ingested event."""
    vendor = event.source.vendor or "Generic"
    now = datetime.now(timezone.utc).isoformat()
    db["sources"].update_one(
        {"vendor": vendor},
        {
            "$set": {"last_seen": now, "status": "active"},
            "$inc": {"event_count": 1},
            "$setOnInsert": {
                "source_id": f"src_{vendor.lower().replace(' ', '_')}",
                "name": f"{vendor} Ingest",
                "format": event.source.format or "custom",
                "createdAt": now,
            },
        },
        upsert=True,
    )


def ingest_log(db, raw_log: str, source_hint: Optional[str] = None) -> Tuple[Optional[BaseParser], Optional[dict]]:
    """
    Detects, parses, normalizes and stores a single log.
    Returns (parser, event_dict) – event_dict is a clean copy without Mongo's _id. (None, None) when unparseable.
    """
    parser, parsed = parser_registry.detect_and_parse(raw_log, db=db)
    if not parser or not parsed:
        return parser, None
    event = build_event(parser, raw_log, parsed, source_hint)
    db["events"].insert_one(event.model_dump())  # insert_one mutates its argument with _id; we keep our own copy
    record_source_stats(db, event)
    return parser, event.model_dump()
