from app.services.normalization import NormalizationService
from app.schemas.event import UniversalEvent

def test_normalization_schema_output():
    raw_log = 'date=2026-10-06 time=10:31:22 devname=FG100D srcip=192.168.1.10 dstip=8.8.8.8 proto=6 action=deny'
    parsed = {
        "vendor": "Fortinet",
        "product": "FortiGate",
        "format": "kv",
        "device_name": "FG100D",
        "timestamp_str": "2026-10-06T10:31:22Z",
        "source_ip": "192.168.1.10",
        "destination_ip": "8.8.8.8",
        "protocol": "TCP",
        "action": "DENY",
        "severity": "high",
        "outcome": "blocked"
    }

    event = NormalizationService.to_universal_event(
        raw_log=raw_log,
        parsed_data=parsed,
        parser_name="FortinetParser",
        confidence=0.99
    )

    assert isinstance(event, UniversalEvent)
    assert event.event_id.startswith("evt_")
    assert event.source.vendor == "Fortinet"
    assert event.network.source_ip == "192.168.1.10"
    assert event.network.destination_ip == "8.8.8.8"
    assert event.event.action == "DENY"
    assert event.raw.message == raw_log
    assert event.integrity.verified is True
    assert len(event.integrity.sha256) == 64

def test_unknown_fields_not_fabricated():
    raw_log = "Minimal test log"
    parsed = {"vendor": "Generic"}
    event = NormalizationService.to_universal_event(raw_log, parsed, "MinimalParser")

    # Fields that were absent should be None, not fabricated strings
    assert event.network.source_ip is None
    assert event.network.destination_ip is None
    assert event.network.source_port is None
    assert event.user.username is None
