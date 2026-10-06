cd frontend
npm run dev

cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload



# ULPF — Universal Log Pre-processing Framework

[![SIH 2026](https://img.shields.io/badge/SIH-2026-blue.svg)](https://www.sih.gov.in/)
[![Theme](https://img.shields.io/badge/Theme-Blockchain%20%26%20Cybersecurity-indigo.svg)]()
[![Organization](https://img.shields.io/badge/Org-NTRO-red.svg)]()
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2016-black.svg)](https://nextjs.org)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB-47A248.svg)](https://www.mongodb.com)

**Problem Statement:** SIH26156  
**Title:** Universal Log Pre-processing Framework  
**Organization:** National Technical Research Organisation (NTRO)  
**Theme:** Blockchain & Cybersecurity  

---

## 1. Problem Statement & Motivation

Enterprise networks and military/defense backbones operate dozens of heterogeneous devices — perimeter firewalls (Cisco ASA, Fortinet, Palo Alto), unified threat management (UTM) appliances, DNS servers, and cloud workloads. Each vendor generates telemetry in proprietary syntax:
- Cisco: Syslog mnemonics (`%ASA-4-106023`)
- Fortinet: Key-Value strings (`srcip=... proto=6 action=deny`)
- Palo Alto: Positional PAN-OS CSV streams (`1,timestamp,serial,TRAFFIC,...`)
- Linux/Routers: RFC 3164 / RFC 5424 Syslog
- Application Services: JSON and ArcSight CEF

Traditional SIEMs struggle with:
1. High onboarding friction when encountering unfamiliar or custom log structures.
2. Accidental data loss or field truncation during normalization.
3. Lack of cryptographic integrity guarantees proving that original raw logs were not altered.

---

## 2. Solution: The ULPF Framework

**ULPF (Universal Log Pre-processing Framework)** solves these challenges through an intelligent, lossless pre-processing pipeline:

```text
Raw Log Stream
     ↓
Format & Vendor Detection
     ↓
Known Deterministic Parser  OR  AI-Assisted Analysis (OpenAI / Heuristic)
     ↓
Field Extraction
     ↓
Universal Schema Mapping
     ↓
Validation (Pydantic / TypeScript)
     ↓
Cryptographic Hash Generation (SHA-256)
     ↓
Store Raw + Normalized Event (MongoDB)
     ↓
SOC Dashboard / Log Explorer / Analytics
```

### Key Differentiating Capabilities
- **AI-Assisted Onboarding (`/parser-studio`)**: Instantly decomposes unknown log syntax using OpenAI structured output (with a resilient local fallback) and translates fields to the Universal Schema with human-in-the-loop approval.
- **Dynamic Parser Registry**: Once approved, newly onboarded custom parsers are cached in MongoDB and parse subsequent logs with deterministic speed.
- **Lossless Raw Event Preservation**: The untouched raw message is stored in `raw.message` along with its SHA-256 fingerprint (`Integrity Verified ✓`).
- **Real-Time SOC Dashboard**: Zero hardcoded metrics — charts, timelines, action breakdowns, and severities are aggregated live from MongoDB.

---

## 3. Architecture

```text
+-------------------------------------------------------------------------------+
|                                ULPF ARCHITECTURE                              |
+-------------------------------------------------------------------------------+
|                                                                               |
|   [ Cisco ASA ]    [ Fortinet ]    [ Palo Alto ]    [ CEF / JSON / Syslog ]   |
|         |               |               |                      |              |
|         +---------------+---------------+----------------------+              |
|                                 |                                             |
|                                 v                                             |
|                     [ FORMAT DETECTION ENGINE ]                               |
|                                 |                                             |
|                 +---------------+---------------+                             |
|                 |                               |                             |
|         (Known Signature)               (Unknown Format)                      |
|                 |                               |                             |
|                 v                               v                             |
|      +---------------------+        +-----------------------+                 |
|      |  DETERMINISTIC      |        |   AI PARSER STUDIO    |                 |
|      |  PARSER REGISTRY    |        |   (OpenAI / Heuristic)|                 |
|      |                     |        |                       |                 |
|      | - Cisco ASA/IOS     |        | - Field Extraction    |                 |
|      | - Fortinet FortiOS  |        | - Schema Mapping      |                 |
|      | - Palo Alto PAN-OS  |        | - Confidence Rating   |                 |
|      | - ArcSight CEF      |        +-----------+-----------+                 |
|      | - Generic JSON      |                    |                             |
|      | - Generic Syslog    |         [ Human Approval & Save]                 |
|      +----------+----------+                    |                             |
|                 |                               v                             |
|                 +--------------------> [ DYNAMIC DB PARSER ]                  |
|                                 |                                             |
|                                 v                                             |
|               [ UNIVERSAL SCHEMA NORMALIZER (Pydantic) ]                      |
|               - event_id, timestamp, source, network                          |
|               - event, user, processing metadata                              |
|                                 |                                             |
|                                 v                                             |
|               [ SHA-256 INTEGRITY FINGERPRINTING ]                            |
|                                 |                                             |
|                                 v                                             |
|                      [ MONGODB PERSISTENCE ]                                  |
|               collections: events | parsers | sources                         |
|                                 |                                             |
|                                 v                                             |
|                      [ NEXT.JS SOC INTERFACE ]                                |
|   - Real-time Visualizations (Recharts: Timeline, Actions, Severities)        |
|   - Multi-Filter Log Explorer & Search                                        |
|   - Side-by-Side Event Details with SHA-256 Verification                      |
|   - AI Parser Studio Custom Onboarding Wizard                                 |
+-------------------------------------------------------------------------------+
```

---

## 4. Universal Event Schema

All heterogeneous logs normalize into a standard Pydantic/TypeScript contract:

```json
{
  "event_id": "evt_9f81a7b03c21",
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
    "username": null
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

## 5. Technology Stack

- **Frontend**: Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS, Lucide Icons, Recharts
- **Backend**: Python 3.12, FastAPI, Pydantic v2, Uvicorn
- **Database**: MongoDB 7+, PyMongo, Motor
- **AI Engine**: OpenAI API (`gpt-4o-mini`) with intelligent local regex heuristic fallback (guarantees offline reliability during evaluations)
- **Security**: SHA-256 cryptographic hashing

---

## 6. Getting Started & Local Setup

### Prerequisites
- Node.js 18+ (or 22+)
- Python 3.11+
- MongoDB running locally on `localhost:27017`

### Backend Setup

```bash
cd backend

# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment (optional OpenAI key)
cp .env.example .env

# 3. Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Backend API will be accessible at: `http://localhost:8000` (Swagger docs: `http://localhost:8000/docs`).

### Frontend Setup

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Run the Next.js development server
npm run dev
```
Frontend SOC console will be accessible at: `http://localhost:3000`.

### Running Tests

```bash
# Run backend pytest suite (18 unit & integration tests)
pytest backend/tests/ -v

# Run frontend build check
npm run build --prefix frontend
```

---

## 7. SIH 2-Minute Demonstration Flow

1. **Step 1: Dashboard (`/dashboard`)**
   - Click **"Seed Demo Logs"** in the top bar.
   - Point out real-time MongoDB statistics: Total Events, Blocked, Threats, Active Sources.
   - Review Recharts graphs: Timeline, Policy Actions, Sources Breakdown, and Severities.

2. **Step 2: Log Explorer (`/logs`)**
   - Filter by vendor (e.g. Cisco) or action (e.g. DENY).
   - Show how heterogeneous formats are unified under standard 5-tuple columns.

3. **Step 3: Lossless Fidelity & SHA-256 (`/logs/[id]`)**
   - Click **Inspect** on any event.
   - Show side-by-side view: **Normalized Universal Event** (left) vs **Original Raw Log** (right).
   - Click **Re-verify Hash** to prove non-repudiation (`Integrity Verified ✓`).

4. **Step 4: AI Parser Studio (`/parser-studio`)**
   - Paste an unknown custom log (or select a preloaded sample).
   - Click **"Analyze with AI"**.
   - Show AI detection badges and the interactive field mapping table.
   - Click **"Approve & Register Parser"**.

5. **Step 5: Dynamic Testing**
   - Feed a second test log into the sandbox.
   - Observe that it is parsed deterministically by the newly saved custom parser without calling AI.
   - Return to dashboard to see the new event reflected in live metrics!

---

## 8. Directory Layout

```text
cns/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app factory
│   │   ├── config.py                # Pydantic Settings
│   │   ├── database.py              # MongoDB client & indexes
│   │   ├── schemas/                 # Universal Schema & AI models
│   │   ├── parsers/                 # Cisco, Fortinet, Palo Alto, Syslog, JSON, CEF, Dynamic
│   │   ├── services/                # Normalization, SHA-256 Integrity, AI Service, Demo Seeder
│   │   └── routes/                  # REST endpoints
│   ├── tests/                       # Pytest test suite (18 tests)
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── app/
│   │   ├── dashboard/page.tsx       # SOC Dashboard
│   │   ├── logs/page.tsx            # Log Explorer
│   │   ├── logs/[id]/page.tsx       # Event Inspector (Side-by-side)
│   │   ├── parser-studio/page.tsx   # AI Parser Studio
│   │   ├── sources/page.tsx         # Detected Sources
│   │   ├── parsers/page.tsx         # Parser Registry
│   │   └── settings/page.tsx        # Demo Seeder & SIH Walkthrough
│   ├── components/                  # Layout, Charts, Tables, Ingest Modal
│   ├── lib/api.ts                   # Typed API client
│   └── package.json
│
├── sample-data/                     # Realistic logs (Cisco, Fortinet, Palo Alto, Syslog, JSON, CEF, Custom)
├── docs/                            # Architecture, Universal Schema, Parser Engine, API, Demo Flow
├── docker-compose.yml
└── README.md
```

---

## 9. Contributors & License

Developed for the **Smart India Hackathon 2026 (SIH26156)** — National Technical Research Organisation (NTRO).  
License: MIT
