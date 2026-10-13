import re
from fastapi import APIRouter, HTTPException
from app.database import get_database

router = APIRouter(prefix="/sources", tags=["Sources"])

@router.get("")
def list_sources():
    db = get_database()
    sources = list(db["sources"].find({}, {"_id": 0}).sort("event_count", -1))
    return {
        "sources": sources,
        "total": len(sources)
    }

@router.get("/{source_id}")
def get_source(source_id: str):
    db = get_database()
    source = db["sources"].find_one({"source_id": source_id}, {"_id": 0})
    if not source:
        # Fallback query by vendor name
        source = db["sources"].find_one({"vendor": {"$regex": f"^{re.escape(source_id)}$", "$options": "i"}}, {"_id": 0})
    if not source:
        raise HTTPException(status_code=404, detail="Source not found.")
    return source
