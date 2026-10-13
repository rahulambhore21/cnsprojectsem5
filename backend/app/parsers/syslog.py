import re
from typing import Any, Dict, List
from app.parsers.base import BaseParser

class SyslogParser(BaseParser):
    name: str = "SyslogParser"
    vendor: str = "Generic Syslog"
    supported_formats: List[str] = ["syslog", "rfc3164", "rfc5424"]
    version: str = "1.0.0"
    is_builtin: bool = True

    # Regex for standard syslog headers: optional <PRI>, timestamp, host/device, tag/app
    RFC3164_REGEX = re.compile(r'^(?:<(\d{1,3})>)?([A-Za-z]{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+([a-zA-Z0-9_.-]+)\s*(?:([a-zA-Z0-9_.-]+)(?:\[(\d+)\])?:\s*)?(.*)$')
    RFC5424_REGEX = re.compile(r'^<(\d{1,3})>1\s+(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+([a-zA-Z0-9_.-]+)\s+([a-zA-Z0-9_.-]+)\s+([a-zA-Z0-9_.-]+)\s+([a-zA-Z0-9_.-]+)\s+(?:\[.*?\]\s*)?(.*)$')

    def can_parse(self, raw_log: str) -> bool:
        if not raw_log or not isinstance(raw_log, str):
            return False
        # Matches RFC3164, RFC5424 or basic Syslog pattern: "Month Day HH:MM:SS" or "<PRI>"
        if re.match(r'^(?:<\d+>)?([A-Za-z]{3}\s+\d+\s+\d{2}:\d{2}:\d{2})', raw_log):
            return True
        if re.match(r'^<\d+>1\s+\d{4}-\d{2}-\d{2}', raw_log):
            return True
        # Also handle typical syslog key-value strings e.g. "SRC=... DST=..."
        if "SRC=" in raw_log and "DST=" in raw_log:
            return True
        return False

    def parse(self, raw_log: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "vendor": "Generic",
            "product": "Syslog",
            "format": "syslog",
            "confidence": 0.90,
            "category": "system",
            "type": "syslog"
        }

        pri = None
        timestamp = None
        device_name = None
        tag = None
        msg = raw_log

        m5424 = self.RFC5424_REGEX.match(raw_log)
        if m5424:
            pri = m5424.group(1)
            timestamp = m5424.group(2)
            device_name = m5424.group(3)
            tag = m5424.group(4)
            msg = m5424.group(7)
        else:
            m3164 = self.RFC3164_REGEX.match(raw_log)
            if m3164:
                pri = m3164.group(1)
                timestamp = m3164.group(2)
                device_name = m3164.group(3)
                tag = m3164.group(4)
                msg = m3164.group(6)

        if pri and pri.isdigit():
            pri_num = int(pri)
            severity_code = pri_num % 8
            sev_map = {0: "critical", 1: "critical", 2: "critical", 3: "high", 4: "medium", 5: "medium", 6: "low", 7: "low"}
            result["severity"] = sev_map.get(severity_code, "medium")

        if "severity" not in result:
            result["severity"] = "low"

        if timestamp:
            result["timestamp_str"] = timestamp
        if device_name:
            result["device_name"] = device_name
        if tag:
            result["type"] = tag.lower()

        # Parse key=value pairs within the message
        raw_kv = re.findall(r'\b([a-zA-Z0-9_]+)=(?:"([^"]*)"|([^\s]+))', msg)
        kv_pairs = {m[0]: (m[1] if m[1] else m[2]) for m in raw_kv}
        # Handle uppercase keys e.g. SRC=, DST=, PROTO=, DPT=, SPT=, ACTION=
        for k, v in list(kv_pairs.items()):
            upper_k = k.upper()
            if upper_k == "SRC" or upper_k == "SOURCE_IP":
                result["source_ip"] = v
            elif upper_k == "DST" or upper_k == "DEST_IP":
                result["destination_ip"] = v
            elif upper_k in ["SPT", "SRC_PORT", "SPORT"] and v.isdigit():
                result["source_port"] = int(v)
            elif upper_k in ["DPT", "DST_PORT", "DPORT"] and v.isdigit():
                result["destination_port"] = int(v)
            elif upper_k in ["PROTO", "PROTOCOL"]:
                result["protocol"] = v.upper()
            elif upper_k in ["ACTION", "ACT"]:
                result["action"] = v.upper()
                if v.upper() in ["DENY", "DROP", "BLOCK", "REJECT"]:
                    result["outcome"] = "blocked"
                    result["severity"] = "high"
                elif v.upper() in ["ALLOW", "ACCEPT", "PASS"]:
                    result["outcome"] = "success"

        # If IPs were not in key-value form, scan for regex IP patterns
        if "source_ip" not in result:
            ips = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', msg)
            if len(ips) >= 1:
                result["source_ip"] = ips[0]
            if len(ips) >= 2:
                result["destination_ip"] = ips[1]

        # Scan for user if present
        user_match = re.search(r'\buser(?:name)?[\s=:]+([a-zA-Z0-9_.-]+)', msg, re.IGNORECASE)
        if user_match:
            result["username"] = user_match.group(1)

        # Detect action keywords if still missing
        if "action" not in result:
            msg_lower = msg.lower()
            if any(w in msg_lower for w in ["denied", "deny", "block", "drop", "failed"]):
                result["action"] = "DENY"
                result["outcome"] = "blocked"
                result["severity"] = "high"
            elif any(w in msg_lower for w in ["accepted", "allow", "permitted", "success"]):
                result["action"] = "ALLOW"
                result["outcome"] = "success"
            else:
                result["action"] = "ALERT"

        return result
