import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.parsers.base import BaseParser

class CiscoParser(BaseParser):
    name: str = "CiscoParser"
    vendor: str = "Cisco"
    supported_formats: List[str] = ["syslog", "asa", "ios"]
    version: str = "1.0.0"
    is_builtin: bool = True

    # Regex to detect Cisco ASA / IOS tags
    SIGNATURE_REGEX = re.compile(r'%(ASA|IOS|FTD|PIX)-(\d)-(\d+):', re.IGNORECASE)

    def can_parse(self, raw_log: str) -> bool:
        if not raw_log or not isinstance(raw_log, str):
            return False
        return bool(self.SIGNATURE_REGEX.search(raw_log)) or "ciscoasa" in raw_log.lower()

    def parse(self, raw_log: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "vendor": "Cisco",
            "product": "ASA",
            "format": "syslog",
            "confidence": 0.98,
            "category": "network",
            "type": "firewall"
        }

        # 1. Check for syslog timestamp & device name prefix e.g. "Oct 06 10:31:22 firewall01 %ASA..."
        header_match = re.match(r'^([A-Za-z]{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+([a-zA-Z0-9_.-]+)\s+', raw_log)
        if header_match:
            result["timestamp_str"] = header_match.group(1)
            result["device_name"] = header_match.group(2)
        else:
            # Check ISO timestamp e.g. "2026-10-06T10:31:22Z firewall01"
            iso_match = re.match(r'^(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+([a-zA-Z0-9_.-]+)?', raw_log)
            if iso_match:
                result["timestamp_str"] = iso_match.group(1)
                if iso_match.group(2):
                    result["device_name"] = iso_match.group(2)

        # 2. Extract Cisco Tag: %ASA-Severity-Code: Message
        tag_match = self.SIGNATURE_REGEX.search(raw_log)
        if tag_match:
            product_tag = tag_match.group(1).upper()
            severity_num = int(tag_match.group(2))
            msg_code = tag_match.group(3)
            result["product"] = product_tag
            result["event_code"] = f"{product_tag}-{severity_num}-{msg_code}"
            
            # Map severity
            severity_map = {
                0: "critical", 1: "critical", 2: "high", 3: "high",
                4: "medium", 5: "low", 6: "low", 7: "low"
            }
            result["severity"] = severity_map.get(severity_num, "medium")

        # 3. Detect Action
        log_lower = raw_log.lower()
        if "deny" in log_lower or "denied" in log_lower:
            result["action"] = "DENY"
            result["outcome"] = "blocked"
        elif "built" in log_lower or "permitted" in log_lower or "allow" in log_lower:
            result["action"] = "ALLOW"
            result["outcome"] = "success"
        elif "teardown" in log_lower or "closed" in log_lower:
            result["action"] = "CLOSE"
            result["outcome"] = "success"
        elif "drop" in log_lower:
            result["action"] = "DROP"
            result["outcome"] = "blocked"
        else:
            result["action"] = "ALERT"
            result["outcome"] = "unknown"

        # 4. Extract Protocol
        proto_match = re.search(r'\b(tcp|udp|icmp|gre|ip)\b', raw_log, re.IGNORECASE)
        if proto_match:
            result["protocol"] = proto_match.group(1).upper()

        # 5. Extract IP addresses and ports
        # Pattern A: "src inside:192.168.1.10/49221 dst outside:8.8.8.8/443"
        src_dst_a = re.search(r'src\s+(?:[a-zA-Z0-9_-]+:)?(\d{1,3}(?:\.\d{1,3}){3})(?:/(\d+))?\s+dst\s+(?:[a-zA-Z0-9_-]+:)?(\d{1,3}(?:\.\d{1,3}){3})(?:/(\d+))?', raw_log)
        if src_dst_a:
            result["source_ip"] = src_dst_a.group(1)
            if src_dst_a.group(2):
                result["source_port"] = int(src_dst_a.group(2))
            result["destination_ip"] = src_dst_a.group(3)
            if src_dst_a.group(4):
                result["destination_port"] = int(src_dst_a.group(4))
        else:
            # Pattern B: "from 192.168.1.10/49221 to 8.8.8.8/443"
            src_dst_b = re.search(r'from\s+(?:[a-zA-Z0-9_-]+:)?(\d{1,3}(?:\.\d{1,3}){3})(?:/(\d+))?\s+to\s+(?:[a-zA-Z0-9_-]+:)?(\d{1,3}(?:\.\d{1,3}){3})(?:/(\d+))?', raw_log)
            if src_dst_b:
                result["source_ip"] = src_dst_b.group(1)
                if src_dst_b.group(2):
                    result["source_port"] = int(src_dst_b.group(2))
                result["destination_ip"] = src_dst_b.group(3)
                if src_dst_b.group(4):
                    result["destination_port"] = int(src_dst_b.group(4))
            else:
                # Pattern C: "outside:8.8.8.8/443 to inside:192.168.1.10/49221"
                ip_pairs = re.findall(r'(?:[a-zA-Z0-9_-]+:)?(\d{1,3}(?:\.\d{1,3}){3})/(\d+)', raw_log)
                if len(ip_pairs) >= 2:
                    result["source_ip"] = ip_pairs[0][0]
                    result["source_port"] = int(ip_pairs[0][1])
                    result["destination_ip"] = ip_pairs[1][0]
                    result["destination_port"] = int(ip_pairs[1][1])

        # 6. Extract user if present (e.g. "user=admin" or "user admin")
        user_match = re.search(r'\buser[=:\s]+["\']?([a-zA-Z0-9_.-]+)["\']?', raw_log, re.IGNORECASE)
        if user_match:
            result["username"] = user_match.group(1)

        return result
