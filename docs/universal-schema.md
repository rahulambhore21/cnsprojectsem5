# Universal Event Schema Specification

**ULPF Data Contract Specification**  
*Document Version: 1.0.0*

---

## 1. Schema Overview

The Universal Event Schema guarantees that downstream SIEM collectors, correlation engines, and security dashboards receive consistent semantic fields regardless of originating device vendor, protocol, or log syntax.

### Design Invariants:
- All non-existent or unparseable fields remain `null` (never fabricated).
- Timestamps are strictly normalized into ISO-8601 UTC format (`YYYY-MM-DDTHH:MM:SSZ`).
- Action verbs are unified into `ALLOW`, `DENY`, `CLOSE`, or `ALERT`.
- Risk levels are normalized into `low`, `medium`, `high`, or `critical`.

---

## 2. JSON Schema Definition

```json
{
  "event_id": "evt_4b227777d4dd",
  "timestamp": "2026-10-06T10:31:22Z",

  "source": {
    "vendor": "Cisco",
    "product": "ASA",
    "device_name": "firewall01",
    "device_ip": "10.0.0.5",
    "format": "syslog"
  },

  "network": {
    "source_ip": "192.168.1.10",
    "source_port": 49221,
    "destination_ip": "8.8.8.8",
    "destination_port": 443,
    "protocol": "TCP"
  },

  "event": {
    "category": "network",
    "type": "firewall",
    "action": "DENY",
    "severity": "medium",
    "outcome": "blocked"
  },

  "user": {
    "username": null,
    "domain": null
  },

  "raw": {
    "message": "%ASA-4-106023: Deny tcp src inside:192.168.1.10/49221 dst outside:8.8.8.8/443 by access-group \"acl_out\""
  },

  "processing": {
    "parser": "CiscoParser",
    "parser_version": "1.0.0",
    "confidence": 0.98,
    "is_ai_assisted": false
  },

  "integrity": {
    "sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
    "verified": true
  },

  "createdAt": "2026-10-06T10:31:22.500Z"
}
```

---

## 3. Section Definitions

| Section | Purpose | Example Fields |
|---|---|---|
| `event_id` | Unique identifier generated at ingestion | `evt_123456789abc` |
| `timestamp` | UTC normalized event occurrence | `2026-10-06T10:31:22Z` |
| `source` | Originating hardware or telemetry generator | `vendor`, `product`, `device_name` |
| `network` | 5-tuple networking connection details | `source_ip`, `destination_ip`, `protocol` |
| `event` | Security categorization and enforcement outcome | `category`, `type`, `action`, `severity` |
| `user` | Authenticated account or subject identity | `username`, `domain` |
| `raw` | Untouched original message preserving exact bytes | `message` |
| `processing`| Metadata detailing parser engine execution | `parser`, `confidence`, `is_ai_assisted` |
| `integrity` | SHA-256 fingerprint verification | `sha256`, `verified` |
