import uuid
import re
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.database import get_database
from app.services.ai_service import AIService
from app.schemas.ai import AIAnalysisRequest, AIAnalysisResponse
from app.schemas.parser import ParserApprovalRequest
from app.services.regex_safety import validate_user_regex
from app.routes.parser_studio_targets import ALLOWED_TARGETS

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

def _build_signature(mapping_keys):
    """Signature requiring ALL of the first few mapped keys to appear as key=… / key:… tokens."""
    keys = [k for k in mapping_keys if k][:3]
    if not keys:
        return None
    return "".join(rf"(?=.*\b{re.escape(k)}\s*[=:])" for k in keys)


@router.post("/approve")
def approve_and_save_parser(req: ParserApprovalRequest):
    """
    Saves an approved custom parser mapping into MongoDB.
    Enables future logs matching this format/signature to be parsed dynamically.
    """
    db = get_database()

    mapping = {k.strip(): v.strip() for k, v in req.mapping.items() if k.strip()}
    if not mapping:
        raise HTTPException(status_code=422, detail="At least one field mapping is required.")
    bad = sorted({v for v in mapping.values() if v not in ALLOWED_TARGETS})
    if bad:
        raise HTTPException(status_code=422, detail=f"Unsupported target field(s): {', '.join(bad)}")

    try:
        extraction = validate_user_regex(req.extraction_regex)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # The signature is always derived from the mapping keys (and must never match everything).
    signature = _build_signature(mapping.keys())
    now = datetime.now(timezone.utc).isoformat()

    fields = {
        "name": req.name,
        "vendor": req.vendor,
        "format": req.format,
        "mapping": mapping,
        "signature_pattern": signature,
        "extraction_pattern": extraction,
        "delimiter": req.delimiter or "=",
        "sample_log": req.sample_log,
        "event_type": req.event_type or "firewall",
        "is_builtin": False,
        "is_active": True,
        "updatedAt": now,
    }

    # Re-approving the same name+vendor updates the parser (and bumps its patch version) instead of duplicating it
    existing = db["parsers"].find_one({"name": req.name, "vendor": req.vendor, "is_builtin": False})
    if existing:
        parser_id = existing["parser_id"]
        major, minor, patch = (list(map(int, existing.get("version", "1.0.0").split("."))) + [0, 0, 0])[:3]
        fields["version"] = f"{major}.{minor}.{patch + 1}"
        db["parsers"].update_one({"parser_id": parser_id}, {"$set": fields})
    else:
        parser_id = f"parser_{uuid.uuid4().hex[:8]}"
        db["parsers"].insert_one({"parser_id": parser_id, "version": "1.0.0", "createdAt": now, **fields})

    # Register/update in sources collection
    db["sources"].update_one(
        {"vendor": req.vendor},
        {
            "$set": {"format": req.format, "status": "active", "last_seen": now},
            "$setOnInsert": {
                "source_id": f"src_{req.vendor.lower().replace(' ', '_')}",
                "name": req.name,
                "event_count": 0,
                "createdAt": now,
            },
        },
        upsert=True
    )

    db["audit_logs"].insert_one({
        "action": "PARSER_UPDATED" if existing else "PARSER_ONBOARDED",
        "user": "analyst",
        "resource": parser_id,
        "timestamp": now,
        "metadata": {"name": req.name, "vendor": req.vendor, "mapped_fields": len(mapping)}
    })

    return {
        "success": True,
        "parser_id": parser_id,
        "message": f"Custom parser '{req.name}' successfully approved and added to ULPF registry."
    }
