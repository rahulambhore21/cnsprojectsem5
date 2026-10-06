# 2-Minute SIH Demonstration Walkthrough

**Problem Statement SIH26156 (NTRO)**  
*Universal Log Pre-processing Framework (ULPF)*

Use this concise, high-impact script during evaluation presentations:

---

### Step 1: Open SOC Dashboard (`/dashboard`)
1. Point to top metric cards:
   - **Total Events**: 55+ stored events.
   - **Blocked Events**: Denied/dropped security occurrences.
   - **Threats**: High and critical severity incidents.
   - **Active Sources**: Multi-vendor distribution.
2. Note that numbers are computed dynamically from MongoDB (not hardcoded).
3. Point out the interactive charts: Ingestion Timeline, Policy Action Breakdown, Sources Volume, and Severity Classification.

---

### Step 2: Log Explorer & Multi-Format Ingestion (`/logs`)
1. Show the high-density table displaying heterogeneous logs (Cisco ASA, Fortinet, Palo Alto PAN-OS, Syslog, JSON, CEF).
2. Filter by Vendor (e.g. "Cisco") and Action ("DENY").
3. Notice that all vendors conform to the same column structure (Source IP, Destination IP, Action, Severity, Protocol).

---

### Step 3: Lossless Preservation & Cryptographic Integrity (`/logs/[id]`)
1. Click **Inspect** on any event.
2. Highlight the two side-by-side columns:
   - **Left**: Normalized Universal Schema in clean UI cards + raw JSON viewer.
   - **Right**: Original Raw Event preserved byte-for-byte.
3. Show the **Integrity Verified ✓** badge and the 64-character SHA-256 hash digest.
4. Click **Re-verify Hash** to demonstrate cryptographic proof that the original log was never lost, corrupted, or fabricated.

---

### Step 4: AI Parser Studio — Onboard Unsupported Formats (`/parser-studio`)
1. Navigate to **AI Parser Studio**.
2. Select a preloaded unsupported log (e.g., `FW01 source=10.10.1.20 destination=172.16.0.10 protocol=tcp port=443 decision=blocked`).
3. Click **Analyze with AI**.
4. Show the AI detection cards:
   - Detected Vendor & Format
   - Event Classification
   - Confidence score
   - Interactive Field Mapping table (source field -> Universal Schema target path).

---

### Step 5: Approve & Dynamic Parsing Sandbox
1. Click **Approve & Register Parser**.
2. Show confirmation: `Parser approved and registered! Stored in MongoDB.`
3. In the sandbox below, click **Test Log** on a second log line.
4. Notice that it immediately processes through the newly created custom parser with zero latency.

---

### Step 6: Return to Dashboard
1. Return to `/dashboard` to show the newly onboarded event counted in real-time under **AI Onboarded** and the updated statistics.
