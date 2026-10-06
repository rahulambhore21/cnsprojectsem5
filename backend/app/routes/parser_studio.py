import uuid
import re
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.database import get_database
from app.services.ai_service import AIService
from app.schemas.ai import AIAnalysisRequest, AIAnalysisResponse
from app.schemas.parser import ParserApprovalRequest

router = APIRouter(prefix="/parser-studio", tags=["AI Parser Studio"])

@router.post("/analyze", response_model=AIAnalysisResponse)
def analyze_unknown_log(req: AIAnalysisRequest):
    """
    Submits an unknown or custom log line to the AI service.
    Returns detected format, vendor, classification, confidence, and field mappings.
    """
    if not req.raw_log.strip():
        raise HTTPException(status_code=400, detail="Log content cannot be empty.")
    
    return AIService.analyze_log(req.raw_log.strip(), req.context_hint)

@router.post("/approve")
def approve_and_save_parser(req: ParserApprovalRequest):
    """
    Saves an approved custom parser mapping into MongoDB.
    Enables future logs matching this format/signature to be parsed dynamically.
    """
    db = get_database()
    parser_id = f"parser_{uuid.uuid4().hex[:8]}"

    # Build signature pattern if not provided
    signature = req.extraction_regex
    if not signature:
        # Match significant keys in sample log
        keys = list(req.mapping.keys())
        if keys:
            pattern_parts = [re.escape(k) for k in keys[:3]]
            signature = "|".join(pattern_parts)

    parser_doc = {
        "parser_id": parser_id,
        "name": req.name,
        "vendor": req.vendor,
        "format": req.format,
        "mapping": req.mapping,
        "signature_pattern": signature,
        "delimiter": req.delimiter or "=",
        "sample_log": req.sample_log,
        "event_type": req.event_type or "firewall",
        "version": "1.0.0",
        "is_builtin": False,
        "is_active": True,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat()
    }

    db["parsers"].insert_one(parser_doc)

    # Register/update in sources collection
    db["sources"].update_one(
        {"vendor": req.vendor},
        {
            "$set": {
                "format": req.format,
                "status": "active",
                "last_seen": datetime.now(timezone.utc).isoformat()
            },
            "$setOnInsert": {
                "source_id": f"src_{uuid.uuid4().hex[:8]}",
                "name": req.name,
                "vendor": req.vendor,
                "event_count": 0,
                "createdAt": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )

    # Record audit log
    db["audit_logs"].insert_one({
        "action": "PARSER_ONBOARDED",
        "user": "analyst",
        "resource": parser_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": {"name": req.name, "vendor": req.vendor, "mapped_fields": len(req.mapping)}
    })

    return {
        "success": True,
        "parser_id": parser_id,
        "message": f"Custom parser '{req.name}' successfully approved and added to ULPF registry."
    }
