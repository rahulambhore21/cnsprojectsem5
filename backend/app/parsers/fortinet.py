import re
from typing import Any, Dict, List
from app.parsers.base import BaseParser

class FortinetParser(BaseParser):
    name: str = "FortinetParser"
    vendor: str = "Fortinet"
    supported_formats: List[str] = ["kv", "fortigate", "syslog"]
    version: str = "1.0.0"
    is_builtin: bool = True

    # Regex for Fortinet key-value pairs: key="val with spaces" or key=val
    KV_REGEX = re.compile(r'([a-zA-Z0-9_]+)=(?:"([^"]*)"|([^\s]+))')

    def can_parse(self, raw_log: str) -> bool:
        if not raw_log or not isinstance(raw_log, str):
            return False
        # Fortinet logs contain devname= or devid= or (type="traffic" / type=traffic) or fortigate
        lower = raw_log.lower()
        if "devname=" in lower or "devid=" in lower or "type=\"traffic\"" in lower or "type=traffic" in lower:
            return True
        if "srcip=" in lower and "dstip=" in lower and ("proto=" in lower or "service=" in lower):
            return True
        return False

    def parse(self, raw_log: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "vendor": "Fortinet",
            "product": "FortiGate",
            "format": "kv",
            "confidence": 0.99,
            "category": "network",
            "type": "firewall"
        }

        # Extract all key-value pairs
        kv_pairs: Dict[str, str] = {}
        for match in self.KV_REGEX.finditer(raw_log):
            k = match.group(1).lower()
            v = match.group(2) if match.group(2) is not None else match.group(3)
            kv_pairs[k] = v

        # Device info
        if "devname" in kv_pairs:
            result["device_name"] = kv_pairs["devname"]
        elif "devid" in kv_pairs:
            result["device_name"] = kv_pairs["devid"]

        # Timestamp
        date_val = kv_pairs.get("date")
        time_val = kv_pairs.get("time")
        if date_val and time_val:
            result["timestamp_str"] = f"{date_val}T{time_val}Z"

        # Network IPs and Ports
        if "srcip" in kv_pairs:
            result["source_ip"] = kv_pairs["srcip"]
        if "dstip" in kv_pairs:
            result["destination_ip"] = kv_pairs["dstip"]
        if "srcport" in kv_pairs and kv_pairs["srcport"].isdigit():
            result["source_port"] = int(kv_pairs["srcport"])
        if "dstport" in kv_pairs and kv_pairs["dstport"].isdigit():
            result["destination_port"] = int(kv_pairs["dstport"])

        # Protocol mapping
        proto_val = kv_pairs.get("proto")
        if proto_val:
            proto_map = {"6": "TCP", "17": "UDP", "1": "ICMP", "47": "GRE"}
            result["protocol"] = proto_map.get(proto_val, proto_val.upper())
        elif "service" in kv_pairs:
            service = kv_pairs["service"].upper()
            if service in ["HTTP", "HTTPS", "SSH", "FTP", "TELNET"]:
                result["protocol"] = "TCP"
            elif service in ["DNS", "NTP", "SNMP", "DHCP"]:
                result["protocol"] = "UDP"

        # Action mapping
        action_val = kv_pairs.get("action", "").lower()
        if action_val in ["deny", "drop", "block", "client-rst", "server-rst"]:
            result["action"] = "DENY"
            result["outcome"] = "blocked"
        elif action_val in ["accept", "allow", "pass"]:
            result["action"] = "ALLOW"
            result["outcome"] = "success"
        elif action_val in ["close", "timeout"]:
            result["action"] = "CLOSE"
            result["outcome"] = "success"
        else:
            result["action"] = action_val.upper() if action_val else "ALERT"
            result["outcome"] = "unknown"

        # Severity mapping
        level_val = kv_pairs.get("level", "").lower()
        severity_map = {
            "emergency": "critical",
            "alert": "critical",
            "critical": "critical",
            "error": "high",
            "warning": "medium",
            "notice": "low",
            "information": "low",
            "debug": "low"
        }
        result["severity"] = severity_map.get(level_val, "medium")

        # User
        if "user" in kv_pairs and kv_pairs["user"]:
            result["username"] = kv_pairs["user"]

        return result
