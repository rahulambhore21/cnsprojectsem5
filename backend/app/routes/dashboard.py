from datetime import datetime, timezone
from fastapi import APIRouter
from app.database import get_database

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats():
    """
    Computes real-time SOC metrics directly from MongoDB collections.
    Zero hardcoded values.
    """
    db = get_database()
    events_col = db["events"]

    total_events = events_col.count_documents({})
    
    # Blocked count (DENY, DROP, BLOCK)
    blocked_events = events_col.count_documents({
        "event.action": {"$in": ["DENY", "BLOCK", "DROP"]}
    })

    # High and critical threats
    threat_events = events_col.count_documents({
        "event.severity": {"$in": ["high", "critical"]}
    })

    # Distinct vendors
    vendors = events_col.distinct("source.vendor")
    active_sources = len([v for v in vendors if v])

    # AI / Custom onboarded count
    unknown_onboarded = events_col.count_documents({
        "processing.is_ai_assisted": True
    })

    return {
        "total_events": total_events,
        "processed_events": total_events,
        "blocked_events": blocked_events,
        "threat_events": threat_events,
        "active_sources": active_sources,
        "unknown_sources": unknown_onboarded,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/recent-events")
def get_recent_events():
    """Fetches the 10 most recently ingested events."""
    db = get_database()
    cursor = db["events"].find({}, {"_id": 0}).sort("timestamp", -1).limit(10)
    return {"events": list(cursor)}

@router.get("/event-distribution")
def get_event_distribution():
    """
    Aggregates distributions for Recharts charts:
    - Actions (ALLOW, DENY, CLOSE, ALERT)
    - Severities (low, medium, high, critical)
    - Timeline (events grouped by hour/time bucket)
    """
    db = get_database()
    events_col = db["events"]

    action_counts = {"ALLOW": 0, "DENY": 0, "CLOSE": 0, "ALERT": 0}
    for r in events_col.aggregate([{"$group": {"_id": "$event.action", "count": {"$sum": 1}}}]):
        # Unknown / missing actions are reported as ALERT
        key = r["_id"] if r["_id"] in action_counts else "ALERT"
        action_counts[key] += r["count"]

    severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for r in events_col.aggregate([{"$group": {"_id": "$event.severity", "count": {"$sum": 1}}}]):
        key = r["_id"] if r["_id"] in severity_counts else "low"
        severity_counts[key] += r["count"]

    # Timeline: hourly buckets keyed on "YYYY-MM-DDTHH" so different days never merge
    timeline_rows = events_col.aggregate([
        {"$match": {"timestamp": {"$type": "string"}}},
        {"$group": {"_id": {"$substrBytes": ["$timestamp", 0, 13]}, "count": {"$sum": 1}}},
        {"$sort": {"_id": -1}},
        {"$limit": 48},
        {"$sort": {"_id": 1}},
    ])
    timeline_data = [
        {"time": f"{r['_id'][5:10]} {r['_id'][11:13]}:00", "count": r["count"]}
        for r in timeline_rows if len(r["_id"]) == 13
    ]
    if not timeline_data:
        timeline_data = [
            {"time": "08:00", "count": 0},
            {"time": "10:00", "count": 0},
            {"time": "12:00", "count": 0}
        ]

    # Format action data for Pie/Donut
    action_data = [
        {"name": "Allow / Permit", "action": "ALLOW", "count": action_counts["ALLOW"], "color": "#10b981"},
        {"name": "Deny / Block", "action": "DENY", "count": action_counts["DENY"], "color": "#ef4444"},
        {"name": "Teardown / Close", "action": "CLOSE", "count": action_counts["CLOSE"], "color": "#6366f1"},
        {"name": "Alert / Notice", "action": "ALERT", "count": action_counts["ALERT"], "color": "#f59e0b"}
    ]

    # Format severity data for Bar chart
    severity_data = [
        {"severity": "Low", "count": severity_counts["low"], "fill": "#3b82f6"},
        {"severity": "Medium", "count": severity_counts["medium"], "fill": "#f59e0b"},
        {"severity": "High", "count": severity_counts["high"], "fill": "#f97316"},
        {"severity": "Critical", "count": severity_counts["critical"], "fill": "#ef4444"}
    ]

    return {
        "actions": action_data,
        "severities": severity_data,
        "timeline": timeline_data
    }

@router.get("/top-sources")
def get_top_sources():
    """Aggregates log count per vendor for the sources bar chart."""
    db = get_database()
    pipeline = [
        {"$group": {"_id": "$source.vendor", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 8}
    ]
    results = list(db["events"].aggregate(pipeline))
    top_sources = [
        {"vendor": r["_id"] or "Unknown", "count": r["count"]}
        for r in results
    ]
    return {"sources": top_sources}
