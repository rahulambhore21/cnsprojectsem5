from fastapi import APIRouter, HTTPException
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
    custom_list = list(db["parsers"].find({"is_builtin": False}, {"_id": 0}))

    return {
        "parsers": builtin_list + custom_list,
        "total": len(builtin_list) + len(custom_list),
        "builtin_count": len(builtin_list),
        "custom_count": len(custom_list)
    }

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
