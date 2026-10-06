import json
from typing import Any, Dict, List
from app.parsers.base import BaseParser

class JsonParser(BaseParser):
    name: str = "JsonParser"
    vendor: str = "Generic JSON"
    supported_formats: List[str] = ["json"]
    version: str = "1.0.0"
    is_builtin: bool = True

    def can_parse(self, raw_log: str) -> bool:
        if not raw_log or not isinstance(raw_log, str):
            return False
        trimmed = raw_log.strip()
        if (trimmed.startswith("{") and trimmed.endswith("}")) or (trimmed.startswith("[") and trimmed.endswith("]")):
            try:
                json.loads(trimmed)
                return True
            except Exception:
                return False
        return False

    def parse(self, raw_log: str) -> Dict[str, Any]:
        try:
            data = json.loads(raw_log.strip())
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
        except Exception:
            return {"vendor": "Generic", "format": "json", "confidence": 0.5}

        result: Dict[str, Any] = {
            "vendor": data.get("vendor") or data.get("source_vendor") or "Generic",
            "product": data.get("product") or data.get("app") or "JSON Service",
            "format": "json",
            "confidence": 0.99,
            "category": data.get("category") or "application",
            "type": data.get("type") or data.get("event_type") or "log"
        }

        # Timestamp
        for k in ["timestamp", "time", "@timestamp", "datetime", "created_at"]:
            if k in data and data[k]:
                result["timestamp_str"] = str(data[k])
                break

        # Device
        for k in ["device_name", "host", "hostname", "server", "device"]:
            if k in data and data[k]:
                result["device_name"] = str(data[k])
                break

        # Source IP
        for k in ["src_ip", "source_ip", "src", "client_ip", "source", "s_ip"]:
            if k in data and data[k]:
                result["source_ip"] = str(data[k])
                break

        # Destination IP
        for k in ["dst_ip", "destination_ip", "dst", "dest_ip", "server_ip", "d_ip"]:
            if k in data and data[k]:
                result["destination_ip"] = str(data[k])
                break

        # Source Port
        for k in ["src_port", "source_port", "spt", "client_port", "sport"]:
            if k in data and str(data[k]).isdigit():
                result["source_port"] = int(data[k])
                break

        # Destination Port
        for k in ["dst_port", "destination_port", "dpt", "server_port", "dport"]:
            if k in data and str(data[k]).isdigit():
                result["destination_port"] = int(data[k])
                break

        # Protocol
        for k in ["protocol", "proto", "transport"]:
            if k in data and data[k]:
                result["protocol"] = str(data[k]).upper()
                break

        # Action
        for k in ["action", "act", "decision", "status", "result"]:
            if k in data and data[k]:
                val = str(data[k]).upper()
                if "DENY" in val or "BLOCK" in val or "DROP" in val or "REJECT" in val:
                    result["action"] = "DENY"
                    result["outcome"] = "blocked"
                elif "ALLOW" in val or "ACCEPT" in val or "PERMIT" in val or "OK" in val or "200" in val:
                    result["action"] = "ALLOW"
                    result["outcome"] = "success"
                else:
                    result["action"] = val
                break

        # Severity
        for k in ["severity", "level", "priority", "log_level"]:
            if k in data and data[k]:
                val = str(data[k]).lower()
                if "crit" in val or "emerg" in val or "fatal" in val:
                    result["severity"] = "critical"
                elif "err" in val or "high" in val:
                    result["severity"] = "high"
                elif "warn" in val or "med" in val:
                    result["severity"] = "medium"
                else:
                    result["severity"] = "low"
                break

        # User
        for k in ["username", "user", "user_name", "account"]:
            if k in data and data[k]:
                result["username"] = str(data[k])
                break

        return result
