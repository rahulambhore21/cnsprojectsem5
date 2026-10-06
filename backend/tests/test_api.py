from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert data["service"] == "ULPF — Universal Log Pre-processing Framework"

def test_demo_seed_and_stats():
    # Seed demo data
    seed_res = client.post("/api/demo/seed")
    assert seed_res.status_code == 200
    seed_data = seed_res.json()
    assert seed_data["success"] is True
    assert seed_data["seeded_count"] > 0

    # Verify dashboard stats calculate from real data
    stats_res = client.get("/api/dashboard/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_events"] >= seed_data["seeded_count"]
    assert stats["blocked_events"] > 0
    assert stats["active_sources"] >= 3

def test_events_list_and_filter():
    res = client.get("/api/events?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert "events" in data
    assert len(data["events"]) <= 5
    assert data["total"] > 0

    # Get one event ID
    event_id = data["events"][0]["event_id"]
    single_res = client.get(f"/api/events/{event_id}")
    assert single_res.status_code == 200
    event = single_res.json()
    assert event["event_id"] == event_id
    assert "integrity" in event
    assert len(event["integrity"]["sha256"]) == 64

def test_process_known_event():
    cisco_log = '%ASA-4-106023: Deny tcp src inside:192.168.1.99/49221 dst outside:8.8.8.8/443'
    res = client.post("/api/events/process", json={"raw_log": cisco_log})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["event"]["source"]["vendor"] == "Cisco"
    assert data["event"]["network"]["source_ip"] == "192.168.1.99"

def test_parser_studio_flow():
    custom_log = "2026-10-06 11:20:31 FW01 source=10.10.1.20 destination=172.16.0.10 protocol=tcp port=443 decision=blocked"
    
    # 1. Analyze
    analyze_res = client.post("/api/parser-studio/analyze", json={"raw_log": custom_log})
    assert analyze_res.status_code == 200
    analysis = analyze_res.json()
    assert analysis["confidence"] > 0.8
    assert len(analysis["mappings"]) > 0

    # 2. Approve
    mapping_dict = {m["source_field"]: m["target_field"] for m in analysis["mappings"]}
    approve_res = client.post("/api/parser-studio/approve", json={
        "name": "Integration Test Custom Parser",
        "vendor": "TestFW",
        "format": "custom",
        "sample_log": custom_log,
        "mapping": mapping_dict
    })
    assert approve_res.status_code == 200
    assert approve_res.json()["success"] is True
