import io
import json
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_database
from app.parsers.dynamic import CustomDynamicParser
from app.parsers.registry import parser_registry
from app.routes.logs import split_log_text
from app.routes.parser_studio import _build_signature
from app.services.normalization import NormalizationService as N
from app.services.regex_safety import validate_user_regex
import pytest

client = TestClient(app)


# ---- normalization -------------------------------------------------------
@pytest.mark.parametrize("value,expected", [
    ("BROKEN", "BROKEN"), ("PASSWORD_CHANGE", "PASSWORD_CHANGE"), ("FINISHED", "FINISHED"),
    ("blocked", "DENY"), ("Permitted", "ALLOW"), ("session-teardown", "CLOSE"),
])
def test_action_uses_whole_words(value, expected):
    assert N.normalize_action(value) == expected


def test_timestamp_offset_converted_to_utc():
    assert N.normalize_timestamp("2026-10-06T10:31:22+05:30") == "2026-10-06T05:01:22Z"
    assert N.normalize_timestamp("2026-10-06 10:31:22.123Z") == "2026-10-06T10:31:22Z"


def test_syslog_december_not_in_future():
    ts = N.normalize_timestamp("Dec 31 23:59:59")
    assert ts <= N.normalize_timestamp(None)


def test_confidence_comes_from_parse_result():
    ev = N.to_universal_event("x", {"confidence": 0.5}, "P")
    assert ev.processing.confidence == 0.5


# ---- parser signatures ---------------------------------------------------
def test_generated_signature_requires_all_keys():
    sig = _build_signature(["src", "dst", "act"])
    p = CustomDynamicParser("p", "n", "v", "kv", {"src": "network.source_ip"}, signature_pattern=sig)
    assert p.can_parse("src=1.1.1.1 dst=2.2.2.2 act=allow")
    assert not p.can_parse("Oct 6 sshd: user lost the first transaction")


def test_custom_parser_does_not_hijack_builtin_formats():
    class FakeCol:
        def find(self, *_a, **_k):
            return [{"parser_id": "p", "name": "n", "vendor": "v", "mapping": {"src": "network.source_ip"},
                     "signature_pattern": "src", "is_active": True, "is_builtin": False}]
    class FakeDB(dict):
        def __getitem__(self, k): return FakeCol()
    cisco = "Oct 06 10:31:22 fw01 %ASA-6-302013: Built inbound TCP connection src inside:10.0.0.1/1 dst outside:8.8.8.8/443"
    parser, _ = parser_registry.detect_and_parse(cisco, db=FakeDB())
    assert parser.name == "CiscoParser"


# ---- regex safety --------------------------------------------------------
@pytest.mark.parametrize("bad", ["(a+)+$", "(.*)*x", "(", "a" * 600])
def test_unsafe_regex_rejected(bad):
    with pytest.raises(ValueError):
        validate_user_regex(bad)


def test_safe_regex_accepted():
    assert validate_user_regex(r"src=(?P<src>\d+\.\d+\.\d+\.\d+)")


# ---- upload --------------------------------------------------------------
def test_split_json_array_into_records():
    recs = split_log_text(json.dumps([{"a": 1}, {"a": 2}], indent=2))
    assert len(recs) == 2 and json.loads(recs[1]) == {"a": 2}


def test_upload_json_array_returns_serializable_response():
    payload = json.dumps([{"timestamp": "2026-10-06T10:34:00Z", "vendor": "RegTest", "src_ip": "1.2.3.4",
                           "dst_ip": "5.6.7.8", "action": "BLOCK"}], indent=2)
    res = client.post("/api/logs/upload", files={"file": ("t.json", io.BytesIO(payload.encode()), "application/json")})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["processed_count"] == 1 and "_id" not in body["processed_events"][0]
    db = get_database()
    db["events"].delete_many({"source.vendor": "RegTest"})
    db["sources"].delete_many({"vendor": "RegTest"})


def test_upload_too_large_rejected(monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "MAX_UPLOAD_BYTES", 10)
    res = client.post("/api/logs/upload", files={"file": ("t.log", io.BytesIO(b"x" * 50), "text/plain")})
    assert res.status_code == 413


# ---- parser approval -----------------------------------------------------
def test_approve_rejects_bad_regex_and_targets():
    base = {"name": "RegParser", "vendor": "RegVendor", "sample_log": "a=1 b=2", "mapping": {"a": "network.source_ip"}}
    assert client.post("/api/parser-studio/approve", json={**base, "extraction_regex": "(a+)+$"}).status_code == 422
    assert client.post("/api/parser-studio/approve", json={**base, "mapping": {"a": "evil.path"}}).status_code == 422


def test_approve_is_idempotent_and_matches_only_its_format():
    name = f"Reg{uuid.uuid4().hex[:6]}"
    body = {"name": name, "vendor": name, "sample_log": "foo=1 bar=2",
            "mapping": {"foo": "network.source_ip", "bar": "network.destination_ip"}}
    r1 = client.post("/api/parser-studio/approve", json=body).json()
    r2 = client.post("/api/parser-studio/approve", json=body).json()
    db = get_database()
    try:
        assert r1["parser_id"] == r2["parser_id"]
        assert db["parsers"].count_documents({"name": name}) == 1
        ok = client.post("/api/events/process", json={"raw_log": "foo=1.1.1.1 bar=2.2.2.2"}).json()
        assert ok["success"] and ok["event"]["source"]["vendor"] == name
        unrelated = client.post("/api/events/process", json={"raw_log": "completely unrelated text"}).json()
        assert unrelated["success"] is False
    finally:
        db["parsers"].delete_many({"name": name})
        db["events"].delete_many({"source.vendor": name})
        db["sources"].delete_many({"vendor": name})


# ---- misc endpoints ------------------------------------------------------
def test_batch_verify_and_dashboard():
    res = client.post("/api/events/batch", json={"logs": ["Oct 06 10:31:22 host sshd[1]: Failed password for root from 1.2.3.4"]})
    assert res.status_code == 200 and res.json()["success_count"] == 1
    eid = res.json()["events"][0]["event_id"]
    assert client.get(f"/api/events/{eid}/verify").json()["verified"] is True
    dist = client.get("/api/dashboard/event-distribution").json()
    assert {"actions", "severities", "timeline"} <= dist.keys()
    client.delete(f"/api/events/{eid}")


def test_source_lookup_escapes_regex():
    assert client.get("/api/sources/.*").status_code == 404


def test_api_key_guard(monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "API_KEY", "secret-key")
    assert client.get("/api/events").status_code == 401
    assert client.get("/api/events", headers={"X-API-Key": "secret-key"}).status_code == 200
    assert client.get("/api/health").status_code == 200
