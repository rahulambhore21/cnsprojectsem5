from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.schemas.parser import ParserUpdateRequest
from app.database import get_database
from app.parsers.registry import parser_registry

router = APIRouter(prefix="/parsers", tags=["Parsers"])

@router.get("")
def list_parsers():
    db = get_database()
    # 1. Built-in parsers list
    builtin_list = [
        {
            "parser_id": f"builtin_{p.name.lower()}",
            "name": p.name,
            "vendor": p.vendor,
            "format": p.supported_formats[0] if p.supported_formats else "syslog",
            "version": p.version,
            "is_builtin": True,
            "is_active": True,
            "description": f"Deterministic adapter for {p.vendor} format logs."
        }
        for p in parser_registry.builtin_parsers
    ]

    # 2. Custom parsers from DB
    custom_list = list(db["parsers"].find({"is_builtin": False}, {"_id": 0}).sort("createdAt", -1))

    return {
        "parsers": builtin_list + custom_list,
        "total": len(builtin_list) + len(custom_list),
        "builtin_count": len(builtin_list),
        "custom_count": len(custom_list)
    }

@router.patch("/{parser_id}")
def update_parser(parser_id: str, req: ParserUpdateRequest):
    """Activate/deactivate or rename a custom parser."""
    db = get_database()
    changes = {k: v for k, v in req.model_dump().items() if v is not None}
    if not changes:
        raise HTTPException(status_code=400, detail="No changes supplied.")
    changes["updatedAt"] = datetime.now(timezone.utc).isoformat()
    result = db["parsers"].update_one({"parser_id": parser_id, "is_builtin": False}, {"$set": changes})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Custom parser not found (built-in parsers are read-only).")
    return {"success": True, "parser_id": parser_id}

@router.delete("/{parser_id}")
def delete_parser(parser_id: str):
    db = get_database()
    result = db["parsers"].delete_one({"parser_id": parser_id, "is_builtin": False})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Custom parser not found (built-in parsers cannot be deleted).")
    db["audit_logs"].insert_one({
        "action": "PARSER_DELETED", "user": "analyst", "resource": parser_id,
        "timestamp": datetime.now(timezone.utc).isoformat(), "metadata": {}
    })
    return {"success": True, "message": f"Parser {parser_id} deleted."}

@router.get("/{parser_id}")
def get_parser(parser_id: str):
    db = get_database()
    parser = db["parsers"].find_one({"parser_id": parser_id}, {"_id": 0})
    if not parser:
        # Check builtins
        for p in parser_registry.builtin_parsers:
            if f"builtin_{p.name.lower()}" == parser_id or p.name.lower() == parser_id.lower():
                return {
                    "parser_id": f"builtin_{p.name.lower()}",
                    "name": p.name,
                    "vendor": p.vendor,
                    "format": p.supported_formats[0] if p.supported_formats else "syslog",
                    "version": p.version,
                    "is_builtin": True,
                    "is_active": True
                }
        raise HTTPException(status_code=404, detail="Parser not found.")
    return parser
