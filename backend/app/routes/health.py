from datetime import datetime, timezone
from fastapi import APIRouter
from app.config import settings
from app.database import get_database

router = APIRouter(tags=["Health"])

@router.get("/health")
def get_health():
    db_status = "connected"
    try:
        db = get_database()
        db.command("ping")
    except Exception as e:
        db_status = f"disconnected: {str(e)}"

    return {
        "status": "healthy" if "disconnected" not in db_status else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": {
            "status": db_status,
            "name": settings.DATABASE_NAME
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
