import logging
from typing import List, Optional, Tuple, Dict, Any
from app.parsers.base import BaseParser
from app.parsers.cisco import CiscoParser
from app.parsers.fortinet import FortinetParser
from app.parsers.paloalto import PaloAltoParser
from app.parsers.cef import CEFParser
from app.parsers.json_parser import JsonParser
from app.parsers.syslog import SyslogParser
from app.parsers.dynamic import CustomDynamicParser

logger = logging.getLogger("ulpf.registry")

class ParserRegistry:
    def __init__(self):
        # Order of precedence for built-in deterministic parsers:
        # Specific vendor signatures first, then structured (CEF, JSON), then generic syslog
        self.builtin_parsers: List[BaseParser] = [
            CiscoParser(),
            FortinetParser(),
            PaloAltoParser(),
            CEFParser(),
            JsonParser(),
            SyslogParser(),
        ]

    def get_all_parsers(self, db=None) -> List[BaseParser]:
        """Returns list of built-in and dynamic database parsers."""
        parsers = list(self.builtin_parsers)
        if db is not None:
            try:
                custom_defs = db["parsers"].find({"is_active": True})
                for doc in custom_defs:
                    if not doc.get("is_builtin", False):
                        parsers.append(
                            CustomDynamicParser(
                                parser_id=doc.get("parser_id", "custom"),
                                name=doc.get("name", "Custom Parser"),
                                vendor=doc.get("vendor", "Custom"),
                                format_type=doc.get("format", "custom"),
                                mapping=doc.get("mapping", {}),
                                signature_pattern=doc.get("signature_pattern"),
                                extraction_pattern=doc.get("extraction_pattern"),
                                delimiter=doc.get("delimiter"),
                                version=doc.get("version", "1.0.0")
                            )
                        )
            except Exception as e:
                logger.warning("Could not fetch custom parsers from DB: %s", e)
        return parsers

    def find_parser(self, raw_log: str, db=None) -> Optional[BaseParser]:
        """Finds the best matching parser for the raw log string."""
        if not raw_log or not isinstance(raw_log, str):
            return None

        # 1. First check custom parsers if any (prioritizes user onboarding)
        if db is not None:
            try:
                custom_defs = db["parsers"].find({"is_active": True, "is_builtin": False})
                for doc in custom_defs:
                    dyn_parser = CustomDynamicParser(
                        parser_id=doc.get("parser_id", "custom"),
                        name=doc.get("name", "Custom Parser"),
                        vendor=doc.get("vendor", "Custom"),
                        format_type=doc.get("format", "custom"),
                        mapping=doc.get("mapping", {}),
                        signature_pattern=doc.get("signature_pattern"),
                        extraction_pattern=doc.get("extraction_pattern"),
                        delimiter=doc.get("delimiter"),
                        version=doc.get("version", "1.0.0")
                    )
                    if dyn_parser.can_parse(raw_log):
                        return dyn_parser
            except Exception as e:
                logger.warning("Error evaluating dynamic parsers: %s", e)

        # 2. Check built-in parsers in precedence order
        for parser in self.builtin_parsers:
            try:
                if parser.can_parse(raw_log):
                    return parser
            except Exception as e:
                logger.debug("Parser %s check error: %s", parser.name, e)
                continue

        return None

    def detect_and_parse(self, raw_log: str, db=None) -> Tuple[Optional[BaseParser], Optional[Dict[str, Any]]]:
        """
        Executes format detection and extracts intermediate parsed fields.
        Returns (parser_instance, parsed_dict) or (None, None).
        """
        parser = self.find_parser(raw_log, db=db)
        if parser:
            try:
                parsed_data = parser.parse(raw_log)
                return parser, parsed_data
            except Exception as e:
                logger.error("Error executing parser %s: %s", parser.name, e)
                return parser, None
        return None, None

# Singleton instance
parser_registry = ParserRegistry()
