import re
import csv
from io import StringIO
from typing import Any, Dict, List
from app.parsers.base import BaseParser

class PaloAltoParser(BaseParser):
    name: str = "PaloAltoParser"
    vendor: str = "Palo Alto"
    supported_formats: List[str] = ["csv", "syslog", "pan-os"]
    version: str = "1.0.0"
    is_builtin: bool = True

    def can_parse(self, raw_log: str) -> bool:
        if not raw_log or not isinstance(raw_log, str):
            return False
        lower = raw_log.lower()
        if "paloalto" in lower or "pan-os" in lower or "pa-fw" in lower:
            return True
        # Check standard PAN-OS CSV signature: starts with digits, timestamp, serial, (TRAFFIC|THREAT|SYSTEM|CONFIG)
        csv_pattern = re.search(r'(?:^|[A-Za-z0-9_.-]+\s+)(?:\d+,)?\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2},\d+,(?:TRAFFIC|THREAT|SYSTEM|CONFIG),', raw_log)
        if csv_pattern:
            return True
        return False

    def parse(self, raw_log: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "vendor": "Palo Alto",
            "product": "PAN-OS",
            "format": "csv",
            "confidence": 0.98,
            "category": "network",
            "type": "firewall"
        }

        # Check for syslog prefix before CSV
        device_name = None
        csv_content = raw_log
        prefix_match = re.match(r'^([A-Za-z]{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+([a-zA-Z0-9_.-]+)\s+(.*)$', raw_log)
        if prefix_match:
            device_name = prefix_match.group(2)
            csv_content = prefix_match.group(3)
            result["timestamp_str"] = prefix_match.group(1)
            result["device_name"] = device_name

        try:
            reader = csv.reader(StringIO(csv_content))
            fields = next(reader)
        except Exception:
            fields = csv_content.split(",")

        # If it's standard PAN-OS Traffic CSV
        if len(fields) >= 30:
            # Check if fields[0] is FUTURE_USE (usually 1) or timestamp
            offset = 0
            if fields[0].isdigit() and len(fields[0]) <= 2:
                offset = 1  # Standard PAN-OS format with FUTURE_USE at index 0

            # Time generated
            time_idx = offset
            if time_idx < len(fields) and "/" in fields[time_idx]:
                result["timestamp_str"] = fields[time_idx].replace("/", "-").replace(" ", "T") + "Z"

            # Serial number / Device Name
            serial_idx = offset + 1
            if serial_idx < len(fields) and not result.get("device_name"):
                result["device_name"] = f"PA-{fields[serial_idx]}"

            # Log Type & Subtype
            type_idx = offset + 2
            subtype_idx = offset + 3
            if type_idx < len(fields):
                result["category"] = fields[type_idx].lower()
            if subtype_idx < len(fields):
                result["type"] = fields[subtype_idx].lower()

            # Source IP and Destination IP
            src_idx = offset + 6
            dst_idx = offset + 7
            if src_idx < len(fields) and re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', fields[src_idx].strip()):
                result["source_ip"] = fields[src_idx].strip()
            if dst_idx < len(fields) and re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', fields[dst_idx].strip()):
                result["destination_ip"] = fields[dst_idx].strip()

            # Protocol
            proto_idx = offset + 28
            if proto_idx < len(fields) and fields[proto_idx].strip():
                result["protocol"] = fields[proto_idx].strip().upper()

            # Action
            act_idx = offset + 29
            if act_idx < len(fields) and fields[act_idx].strip():
                raw_act = fields[act_idx].strip().lower()
                if raw_act in ["allow", "alert"]:
                    result["action"] = raw_act.upper()
                    result["outcome"] = "success"
                elif raw_act in ["deny", "drop", "reset-client", "reset-server", "reset-both"]:
                    result["action"] = "DENY"
                    result["outcome"] = "blocked"
                else:
                    result["action"] = raw_act.upper()

            # Ports
            spt_idx = offset + 23
            dpt_idx = offset + 24
            if spt_idx < len(fields) and fields[spt_idx].strip().isdigit():
                result["source_port"] = int(fields[spt_idx].strip())
            if dpt_idx < len(fields) and fields[dpt_idx].strip().isdigit():
                result["destination_port"] = int(fields[dpt_idx].strip())

            # Severity
            if result.get("action") in ["DENY", "DROP"]:
                result["severity"] = "high"
            else:
                result["severity"] = "low"
        else:
            # Fallback regex extraction for Palo Alto logs
            ips = re.findall(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', raw_log)
            if len(ips) >= 2:
                result["source_ip"] = ips[0]
                result["destination_ip"] = ips[1]
            if "deny" in raw_log.lower() or "drop" in raw_log.lower():
                result["action"] = "DENY"
                result["outcome"] = "blocked"
                result["severity"] = "high"
            else:
                result["action"] = "ALLOW"
                result["outcome"] = "success"
                result["severity"] = "low"

        return result
