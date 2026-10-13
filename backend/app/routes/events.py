import re
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from app.database import get_database
from app.config import settings
from app.services.ingest import ingest_log
from app.services.integrity import calculate_sha256, verify_integrity
from app.schemas.event import (
    UniversalEvent, EventProcessRequest, EventProcessResponse,
    BatchProcessRequest, BatchProcessResponse
)

router = APIRouter(prefix="/events", tags=["Events"])

@router.get("")
def list_events(
    q: Optional[str] = Query(None, description="Free text search query"),
    vendor: Optional[str] = Query(None, description="Filter by source vendor"),
    format_type: Optional[str] = Query(None, alias="format", description="Filter by log format"),
    action: Optional[str] = Query(None, description="Filter by action (ALLOW, DENY, etc.)"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    source_ip: Optional[str] = Query(None, description="Filter by source IP"),
    destination_ip: Optional[str] = Query(None, description="Filter by destination IP"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    db = get_database()
    filter_query = {}

    if vendor and vendor != "all":
        filter_query["source.vendor"] = {"$regex": f"^{re.escape(vendor)}$", "$options": "i"}

    if format_type and format_type != "all":
        filter_query["source.format"] = {"$regex": f"^{re.escape(format_type)}$", "$options": "i"}

    if action and action != "all":
        filter_query["event.action"] = action.upper()

    if severity and severity != "all":
        filter_query["event.severity"] = severity.lower()

    if source_ip:
        filter_query["network.source_ip"] = {"$regex": re.escape(source_ip), "$options": "i"}

    if destination_ip:
        filter_query["network.destination_ip"] = {"$regex": re.escape(destination_ip), "$options": "i"}

    if q:
        safe_q = re.escape(q)
        filter_query["$or"] = [
            {"raw.message": {"$regex": safe_q, "$options": "i"}},
            {"event_id": {"$regex": safe_q, "$options": "i"}},
            {"network.source_ip": {"$regex": safe_q, "$options": "i"}},
            {"network.destination_ip": {"$regex": safe_q, "$options": "i"}},
            {"source.device_name": {"$regex": safe_q, "$options": "i"}},
            {"user.username": {"$regex": safe_q, "$options": "i"}}
        ]

    total = db["events"].count_documents(filter_query)
    skip = (page - 1) * limit

    cursor = db["events"].find(filter_query, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit)
    events = list(cursor)

    return {
        "events": events,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit if limit > 0 else 1
    }

@router.get("/{event_id}")
def get_event(event_id: str):
    db = get_database()
    event = db["events"].find_one({"event_id": event_id}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found.")
    return event

@router.post("/process", response_model=EventProcessResponse)
def process_event(req: EventProcessRequest):
    db = get_database()
    raw_log = req.raw_log.strip()
    if not raw_log:
        raise HTTPException(status_code=400, detail="Empty log input provided.")

    parser, event_dict = ingest_log(db, raw_log, req.source_hint)
    if not event_dict:
        return EventProcessResponse(
            success=False,
            message="No suitable parser detected for this log format. Use AI Parser Studio to onboard this format.",
            error="UNKNOWN_FORMAT"
        )

    return EventProcessResponse(
        success=True,
        event=UniversalEvent(**event_dict),
        message=f"Log successfully parsed using {parser.name} and normalized into Universal Event Schema."
    )

@router.post("/batch", response_model=BatchProcessResponse)
def process_batch(req: BatchProcessRequest):
    """Parses and stores up to MAX_BATCH_LOGS raw logs in one request."""
    if len(req.logs) > settings.MAX_BATCH_LOGS:
        raise HTTPException(status_code=413, detail=f"Batch exceeds {settings.MAX_BATCH_LOGS} logs.")
    db = get_database()
    events, errors = [], []
    for idx, raw in enumerate(req.logs):
        raw = (raw or "").strip()
        if not raw:
            errors.append({"index": idx, "error": "EMPTY"})
            continue
        _, event_dict = ingest_log(db, raw)
        if event_dict:
            events.append(UniversalEvent(**event_dict))
        else:
            errors.append({"index": idx, "error": "UNKNOWN_FORMAT", "raw": raw[:150]})
    return BatchProcessResponse(
        processed_count=len(req.logs),
        success_count=len(events),
        failure_count=len(errors),
        events=events,
        errors=errors
    )

@router.get("/{event_id}/verify")
def verify_event(event_id: str):
    """Recomputes the SHA-256 of the stored raw message and compares it with the stored fingerprint."""
    db = get_database()
    event = db["events"].find_one({"event_id": event_id}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found.")
    expected = (event.get("integrity") or {}).get("sha256", "")
    message = (event.get("raw") or {}).get("message", "")
    return {
        "event_id": event_id,
        "verified": verify_integrity(message, expected),
        "expected_sha256": expected,
        "computed_sha256": calculate_sha256(message),
    }

@router.delete("/{event_id}")
def delete_event(event_id: str):
    db = get_database()
    result = db["events"].delete_one({"event_id": event_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found.")
    return {"success": True, "message": f"Event {event_id} deleted."}
