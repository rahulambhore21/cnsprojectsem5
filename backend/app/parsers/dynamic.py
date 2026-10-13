import re
from typing import Any, Dict, List, Optional
from app.parsers.base import BaseParser

class CustomDynamicParser(BaseParser):
    """
    Parser created dynamically via AI Parser Studio and saved in MongoDB.
    Executes user-approved field mappings and extraction signatures.
    """
    def __init__(
        self,
        parser_id: str,
        name: str,
        vendor: str,
        format_type: str,
        mapping: Dict[str, str],
        signature_pattern: Optional[str] = None,
        extraction_pattern: Optional[str] = None,
        delimiter: Optional[str] = None,
        version: str = "1.0.0"
    ):
        self.parser_id = parser_id
        self.name = name
        self.vendor = vendor
        self.supported_formats = [format_type]
        self.mapping = mapping
        self.signature_pattern = signature_pattern
        self.extraction_pattern = extraction_pattern
        self.delimiter = delimiter
        self.version = version
        self.is_builtin = False

    def can_parse(self, raw_log: str) -> bool:
        if not raw_log or not isinstance(raw_log, str):
            return False
        # An explicit signature is authoritative.
        if self.signature_pattern:
            try:
                return bool(re.search(self.signature_pattern, raw_log, re.IGNORECASE | re.DOTALL))
            except re.error:
                return self.signature_pattern.lower() in raw_log.lower()
        # Otherwise require most mapped field keys to appear as key=… / key:… tokens
        if not self.mapping:
            return False
        matching_keys = sum(
            1 for k in self.mapping if re.search(rf"\b{re.escape(k)}\s*[=:]", raw_log, re.IGNORECASE)
        )
        return matching_keys >= max(2, (len(self.mapping) + 1) // 2)

    def parse(self, raw_log: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "vendor": self.vendor,
            "product": "Custom",
            "format": self.supported_formats[0] if self.supported_formats else "custom",
            "confidence": 0.95,
            "category": "security",
            "type": "custom_event"
        }

        extracted_pairs: Dict[str, str] = {}

        # 1. If extraction regex with named groups is defined
        if self.extraction_pattern:
            try:
                match = re.search(self.extraction_pattern, raw_log)
                if match:
                    extracted_pairs.update(match.groupdict())
            except Exception:
                pass

        # 2. Extract key=value or key:value pairs
        if not extracted_pairs:
            kv_found = re.findall(r'\b([a-zA-Z0-9_-]+)[=:]\s*(?:"([^"]*)"|([^\s,;]+))', raw_log)
            for k, q_val, u_val in kv_found:
                val = q_val if q_val else u_val
                extracted_pairs[k] = val

        # 3. Apply the stored mapping
        # Mapping maps original field -> universal schema dot path
        for source_key, target_path in self.mapping.items():
            # Find in extracted_pairs case-insensitively
            val = None
            for ek, ev in extracted_pairs.items():
                if ek.lower() == source_key.lower():
                    val = ev
                    break

            if val is not None:
                # Map into result based on target schema path
                if target_path == "network.source_ip":
                    result["source_ip"] = val
                elif target_path == "network.destination_ip":
                    result["destination_ip"] = val
                elif target_path == "network.source_port":
                    if str(val).isdigit():
                        result["source_port"] = int(val)
                elif target_path == "network.destination_port":
                    if str(val).isdigit():
                        result["destination_port"] = int(val)
                elif target_path == "network.protocol":
                    result["protocol"] = val.upper()
                elif target_path == "event.action":
                    v_upper = val.upper()
                    if v_upper in ["BLOCKED", "DENY", "DENIED", "DROP", "DROPPED"]:
                        result["action"] = "DENY"
                        result["outcome"] = "blocked"
                        result["severity"] = "high"
                    elif v_upper in ["ALLOW", "ALLOWED", "PERMIT", "PERMITTED", "ACCEPT"]:
                        result["action"] = "ALLOW"
                        result["outcome"] = "success"
                        result["severity"] = "low"
                    else:
                        result["action"] = v_upper
                elif target_path == "event.severity":
                    result["severity"] = val.lower()
                elif target_path == "user.username":
                    result["username"] = val
                elif target_path == "source.device_name":
                    result["device_name"] = val
                elif target_path == "source.vendor":
                    result["vendor"] = val
                elif target_path == "timestamp":
                    result["timestamp_str"] = val
                elif target_path == "user.domain":
                    result["domain"] = val
                elif target_path == "source.device_ip":
                    result["device_ip"] = val
                elif target_path == "event.type":
                    result["type"] = val.lower()
                elif target_path == "event.category":
                    result["category"] = val.lower()

        return result
