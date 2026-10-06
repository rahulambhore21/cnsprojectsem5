# ULPF REST API Documentation

Base URL: `http://localhost:8000/api`

---

## 1. System Health

### `GET /api/health`
Returns connection status of FastAPI core and MongoDB instance.

**Response**:
```json
{
  "status": "healthy",
  "service": "ULPF — Universal Log Pre-processing Framework",
  "version": "1.0.0",
  "database": {
    "status": "connected",
    "name": "ulpf"
  },
  "timestamp": "2026-10-06T12:00:00Z"
}
```

---

## 2. Event Ingestion & Search

### `GET /api/events`
Query normalized events with filtering and pagination.
- **Parameters**: `q`, `vendor`, `format`, `action`, `severity`, `source_ip`, `destination_ip`, `page`, `limit`

### `GET /api/events/{event_id}`
Returns single event document with lossless raw log and SHA-256 hash.

### `POST /api/events/process`
Ingests and normalizes a single raw log string.
**Payload**:
```json
{
  "raw_log": "%ASA-4-106023: Deny tcp src inside:192.168.1.10/49221 dst outside:8.8.8.8/443",
  "source_hint": "Cisco"
}
```

### `POST /api/logs/upload`
Uploads a `.log`, `.txt`, `.json`, or `.csv` file for batch ingestion.

---

## 3. AI Parser Studio

### `POST /api/parser-studio/analyze`
Analyzes unknown or custom log using AI structured output or local heuristic fallback.
**Payload**:
```json
{
  "raw_log": "2026-10-06 11:20:31 FW01 source=10.10.1.20 destination=172.16.0.10 protocol=tcp port=443 decision=blocked",
  "context_hint": "Custom Firewall"
}
```

### `POST /api/parser-studio/approve`
Approves and stores custom parser mapping into MongoDB.
**Payload**:
```json
{
  "name": "Custom Firewall Parser",
  "vendor": "CustomFW",
  "format": "custom",
  "sample_log": "...",
  "mapping": {
    "source": "network.source_ip",
    "destination": "network.destination_ip",
    "decision": "event.action",
    "port": "network.destination_port",
    "protocol": "network.protocol"
  }
}
```

---

## 4. SOC Analytics

### `GET /api/dashboard/stats`
Returns live calculated metrics: total events, blocked, threats, active sources.

### `GET /api/dashboard/event-distribution`
Returns Recharts data structures for action pie chart, severity bar chart, and time series area chart.

### `GET /api/dashboard/top-sources`
Returns count breakdown by vendor.

---

## 5. Demonstration Endpoints

### `POST /api/demo/seed`
Populates MongoDB with 55+ realistic logs across all vendor formats.

### `GET /api/demo/samples`
Returns copy-paste ready sample payloads.
