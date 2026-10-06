from fastapi import APIRouter
from app.services.demo_seeder import DemoSeeder

router = APIRouter(prefix="/demo", tags=["Demo Mode"])

@router.post("/seed")
def seed_demo_data():
    """
    Seeds realistic logs across all vendors (Cisco, Fortinet, Palo Alto,
    Syslog, JSON, CEF) into MongoDB.
    """
    return DemoSeeder.seed_database()

@router.get("/samples")
def get_sample_logs():
    """
    Returns realistic sample logs for rapid one-click testing in UI.
    """
    return DemoSeeder.get_sample_library()
