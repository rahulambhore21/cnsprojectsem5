# ULPF System Architecture

**Universal Log Pre-processing Framework (ULPF)**  
*Smart India Hackathon 2026 — Problem Statement SIH26156*  
*National Technical Research Organisation (NTRO)*

---

## 1. High-Level Architecture

ULPF is designed as a modular, high-throughput log pre-processing pipeline for heterogeneous enterprise and tactical network security environments. It converts fragmented, vendor-proprietary log syntax into an open, validated Universal Event Schema while preserving lossless raw log fidelity and cryptographic integrity.

```
                      +-----------------------------+
                      |   Heterogeneous Log Feeds   |
                      |  Cisco, Fortinet, Palo Alto |
                      |  Syslog, JSON, CEF, Custom  |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |    Format & Vendor Engine   |
                      |    (Regex Signature Match)  |
                      +--------------+--------------+
                                     |
               +---------------------+---------------------+
               |                                           |
      (Signature Matched)                         (Signature Unknown)
               |                                           |
               v                                           v
    +----------------------+                    +----------------------+
    | Deterministic Parser |                    |   AI Parser Studio   |
    | - CiscoParser        |                    |  - OpenAI Structure  |
    | - FortinetParser     |                    |  - Heuristic Fallback|
    | - PaloAltoParser     |                    |  - Schema Mapping    |
    | - CEFParser          |                    +----------+-----------+
    | - JsonParser         |                               |
    | - SyslogParser       |                    [ Human In The Loop ]
    +----------+-----------+                    [ Approve & Save to DB]
               |                                           |
               +---------------------+---------------------+
                                     |
                                     v
                      +-----------------------------+
                      | Universal Schema Normalizer |
                      | - Pydantic Field Extraction |
                      | - ISO-8601 Timestamp Normal |
                      | - Outcome & Action Mapping  |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      | Cryptographic Hash Engine   |
                      | SHA-256(raw_log) Fingerprint|
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |      MongoDB Database       |
                      | events | parsers | sources  |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |      Next.js SOC Client     |
                      | - Analytics Dashboard       |
                      | - High-Density Log Explorer |
                      | - Side-by-Side Inspector    |
                      | - AI Onboarding Studio      |
                      +-----------------------------+
```

---

## 2. Core Architectural Principles

1. **Lossless Log Preservation**:
   Every log message processed through ULPF preserves the original string byte-for-byte in the `raw.message` field. No redaction or irreversible truncation occurs without explicit policy configuration.

2. **Cryptographic Proof of Integrity**:
   Every log payload receives a SHA-256 hash at ingestion. When reviewing normalized events in the SOC console, the hash is validated against the raw message to guarantee non-repudiation.

3. **Deterministic First, AI Assisted Second**:
   Standard formats (Cisco ASA, FortiOS, PAN-OS, Syslog, JSON, CEF) are parsed via compiled Python regular expressions and structural scanners with sub-millisecond latency. The OpenAI LLM is engaged only when onboarding previously unsupported log types.

4. **Dynamic Parser Reification**:
   When an unknown log format is onboarded via the AI Parser Studio, its approved mapping is stored in the database. Subsequent logs matching that signature are parsed immediately without further AI API calls.
