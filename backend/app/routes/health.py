import logging
from datetime import datetime, timezone
from fastapi import APIRouter
from app.config import settings
from app.database import get_database

logger = logging.getLogger("ulpf.health")
router = APIRouter(tags=["Health"])

@router.get("/health")
def get_health():
    db_status = "connected"
    try:
        db = get_database()
        db.command("ping")
    except Exception as e:
        logger.warning("Health check DB ping failed: %s", e)
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": {
            "status": db_status,
            "name": settings.DATABASE_NAME
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
