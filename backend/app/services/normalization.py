import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from app.schemas.event import (
    UniversalEvent,
    SourceDetails,
    NetworkDetails,
    EventClassification,
    UserDetails,
    RawDetails,
    ProcessingDetails,
    IntegrityDetails
)
from app.services.integrity import calculate_sha256

class NormalizationService:
    @staticmethod
    def normalize_timestamp(ts_str: Optional[str]) -> str:
        """Converts diverse log timestamp formats into a clean ISO-8601 UTC string."""
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if not ts_str:
            return now_iso

        ts_clean = ts_str.strip()
        # ISO-8601 check (e.g. 2026-10-06T10:31:22Z or with offset)
        if re.match(r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}', ts_clean):
            clean_iso = ts_clean.replace(" ", "T")
            if not clean_iso.endswith("Z") and "+" not in clean_iso and "-" not in clean_iso[-6:]:
                clean_iso += "Z"
            return clean_iso

        # Syslog month day time check (e.g. Oct 06 10:31:22 or Oct  6 10:31:22)
        month_match = re.match(r'^([A-Za-z]{3})\s+(\d+)\s+(\d{2}:\d{2}:\d{2})', ts_clean)
        if month_match:
            month = month_match.group(1)
            day = int(month_match.group(2))
            hms = month_match.group(3)
            current_year = datetime.now(timezone.utc).year
            try:
                parsed_dt = datetime.strptime(f"{current_year} {month} {day:02d} {hms}", "%Y %b %d %H:%M:%S")
                return parsed_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                return now_iso

        return now_iso

    @staticmethod
    def normalize_action(action_str: Optional[str]) -> str:
        """Standardizes action verbs to ALLOW, DENY, CLOSE, ALERT."""
        if not action_str:
            return "ALLOW"
        act = action_str.upper().strip()
        if any(term in act for term in ["DENY", "BLOCK", "DROP", "REJECT", "STOP", "FORBID"]):
            return "DENY"
        if any(term in act for term in ["ALLOW", "PERMIT", "ACCEPT", "PASS", "SUCCESS", "OK", "OPEN", "BUILT"]):
            return "ALLOW"
        if any(term in act for term in ["CLOSE", "TEARDOWN", "FIN", "RST", "TERMINATED"]):
            return "CLOSE"
        return act

    @staticmethod
    def normalize_severity(sev_str: Optional[str], action: str) -> str:
        """Standardizes severity levels to low, medium, high, critical."""
        if sev_str:
            sev = sev_str.lower().strip()
            if sev in ["emerg", "emergency", "alert", "critical", "crit", "severe"]:
                return "critical"
            if sev in ["err", "error", "high"]:
                return "high"
            if sev in ["warn", "warning", "med", "medium"]:
                return "medium"
            if sev in ["info", "information", "notice", "debug", "low"]:
                return "low"
        # Infer default from action
        if action == "DENY":
            return "high"
        return "low"

    @classmethod
    def to_universal_event(
        cls,
        raw_log: str,
        parsed_data: Dict[str, Any],
        parser_name: str,
        parser_version: str = "1.0.0",
        confidence: float = 1.0,
        is_ai_assisted: bool = False
    ) -> UniversalEvent:
        """
        Transforms intermediate parsed key-values into a validated UniversalEvent.
        Preserves raw message lossless and creates cryptographic hash.
        """
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        timestamp = cls.normalize_timestamp(parsed_data.get("timestamp_str"))
        action = cls.normalize_action(parsed_data.get("action"))
        severity = cls.normalize_severity(parsed_data.get("severity"), action)
        outcome = parsed_data.get("outcome") or ("blocked" if action == "DENY" else "success")

        source = SourceDetails(
            vendor=parsed_data.get("vendor"),
            product=parsed_data.get("product"),
            device_name=parsed_data.get("device_name"),
            device_ip=parsed_data.get("device_ip"),
            format=parsed_data.get("format")
        )

        network = NetworkDetails(
            source_ip=parsed_data.get("source_ip"),
            source_port=parsed_data.get("source_port"),
            destination_ip=parsed_data.get("destination_ip"),
            destination_port=parsed_data.get("destination_port"),
            protocol=parsed_data.get("protocol")
        )

        event = EventClassification(
            category=parsed_data.get("category", "network"),
            type=parsed_data.get("type", "firewall"),
            action=action,
            severity=severity,
            outcome=outcome
        )

        user = UserDetails(
            username=parsed_data.get("username"),
            domain=parsed_data.get("domain")
        )

        raw = RawDetails(
            message=raw_log
        )

        processing = ProcessingDetails(
            parser=parser_name,
            parser_version=parser_version,
            confidence=confidence,
            is_ai_assisted=is_ai_assisted
        )

        sha256_hash = calculate_sha256(raw_log)
        integrity = IntegrityDetails(
            sha256=sha256_hash,
            verified=True
        )

        return UniversalEvent(
            event_id=event_id,
            timestamp=timestamp,
            source=source,
            network=network,
            event=event,
            user=user,
            raw=raw,
            processing=processing,
            integrity=integrity,
            createdAt=datetime.now(timezone.utc).isoformat()
        )
