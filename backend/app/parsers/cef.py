import re
from typing import Any, Dict, List
from app.parsers.base import BaseParser

class CEFParser(BaseParser):
    name: str = "CEFParser"
    vendor: str = "Generic CEF"
    supported_formats: List[str] = ["cef"]
    version: str = "1.0.0"
    is_builtin: bool = True

    # Regex to detect CEF header
    CEF_HEADER_REGEX = re.compile(r'CEF:\s*(\d+)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|(.*)', re.DOTALL)
    # Regex for CEF key-value pairs
    KV_REGEX = re.compile(r'([a-zA-Z0-9_]+)=(?:"([^"]*)"|([^\s]+))')

    def can_parse(self, raw_log: str) -> bool:
        if not raw_log or not isinstance(raw_log, str):
            return False
        return "CEF:" in raw_log

    def parse(self, raw_log: str) -> Dict[str, Any]:
        match = self.CEF_HEADER_REGEX.search(raw_log)
        if not match:
            # Fallback simple split if regex fails
            pipe_parts = raw_log.split("|", 7)
            if len(pipe_parts) == 8:
                version = pipe_parts[0].replace("CEF:", "").strip()
                vendor = pipe_parts[1].strip() or "Generic"
                product = pipe_parts[2].strip() or "CEF Device"
                device_version = pipe_parts[3].strip()
                event_id = pipe_parts[4].strip()
                name = pipe_parts[5].strip()
                severity_str = pipe_parts[6].strip()
                extension_str = pipe_parts[7]
            else:
                return {"vendor": "Generic", "product": "CEF", "confidence": 0.5, "format": "cef"}
        else:
            version = match.group(1).strip()
            vendor = match.group(2).strip() or "Generic"
            product = match.group(3).strip() or "CEF Device"
            device_version = match.group(4).strip()
            event_id = match.group(5).strip()
            name = match.group(6).strip()
            severity_str = match.group(7).strip()
            extension_str = match.group(8)

        # Parse key-value extension
        extensions: Dict[str, str] = {}
        for kv in self.KV_REGEX.finditer(extension_str):
            key = kv.group(1).lower()
            val = kv.group(2) if kv.group(2) is not None else kv.group(3)
            extensions[key] = val

        result: Dict[str, Any] = {
            "vendor": vendor if vendor != "Vendor" else "Generic",
            "product": product,
            "format": "cef",
            "confidence": 0.99,
            "category": "security",
            "type": name.lower() if name else "event"
        }

        # IP and port extraction
        if "src" in extensions:
            result["source_ip"] = extensions["src"]
        if "dst" in extensions:
            result["destination_ip"] = extensions["dst"]
        if "spt" in extensions and extensions["spt"].isdigit():
            result["source_port"] = int(extensions["spt"])
        if "dpt" in extensions and extensions["dpt"].isdigit():
            result["destination_port"] = int(extensions["dpt"])

        # Protocol
        if "proto" in extensions:
            result["protocol"] = extensions["proto"].upper()

        # Action mapping
        raw_act = extensions.get("act", "").lower()
        if raw_act in ["blocked", "deny", "denied", "drop", "dropped", "block"]:
            result["action"] = "DENY"
            result["outcome"] = "blocked"
        elif raw_act in ["allow", "allowed", "permit", "permitted", "accept"]:
            result["action"] = "ALLOW"
            result["outcome"] = "success"
        else:
            result["action"] = raw_act.upper() if raw_act else "ALERT"

        # Severity mapping (CEF 0-10 or string)
        if severity_str.isdigit():
            sev_num = int(severity_str)
            if sev_num >= 8:
                result["severity"] = "critical"
            elif sev_num >= 6:
                result["severity"] = "high"
            elif sev_num >= 4:
                result["severity"] = "medium"
            else:
                result["severity"] = "low"
        else:
            result["severity"] = severity_str.lower() or "medium"

        # Device name / host
        if "dhost" in extensions:
            result["device_name"] = extensions["dhost"]
        elif "dvchost" in extensions:
            result["device_name"] = extensions["dvchost"]

        # User
        if "suser" in extensions:
            result["username"] = extensions["suser"]
        elif "duser" in extensions:
            result["username"] = extensions["duser"]

        return result
