import re
import uuid
from datetime import datetime, timedelta, timezone
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
        """Converts diverse log timestamp formats into a clean ISO-8601 UTC string (…Z)."""
        now = datetime.now(timezone.utc)
        now_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        if not ts_str:
            return now_iso

        ts_clean = str(ts_str).strip()
        # ISO-8601 (optionally with fractional seconds and Z / +hh:mm / +hhmm offset)
        iso = re.match(
            r'^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})(?:[.,]\d+)?\s*(Z|[+-]\d{2}:?\d{2})?$',
            ts_clean, re.IGNORECASE
        )
        if iso:
            y, mo, d, h, mi, sec = (int(iso.group(i)) for i in range(1, 7))
            tz_str = iso.group(7)
            try:
                tz = timezone.utc
                if tz_str and tz_str.upper() != "Z":
                    sign = 1 if tz_str[0] == "+" else -1
                    digits = tz_str[1:].replace(":", "")
                    tz = timezone(sign * timedelta(hours=int(digits[:2]), minutes=int(digits[2:])))
                dt = datetime(y, mo, d, h, mi, sec, tzinfo=tz)
                return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            except (ValueError, OverflowError):
                return now_iso

        # Syslog "Mon DD HH:MM:SS" has no year: assume current year, roll back if that lands in the future
        month_match = re.match(r'^([A-Za-z]{3})\s+(\d+)\s+(\d{2}:\d{2}:\d{2})', ts_clean)
        if month_match:
            month, day, hms = month_match.group(1), int(month_match.group(2)), month_match.group(3)
            for year in (now.year, now.year - 1):
                try:
                    dt = datetime.strptime(f"{year} {month} {day:02d} {hms}", "%Y %b %d %H:%M:%S").replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
                if dt <= now + timedelta(days=1):
                    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            return now_iso

        return now_iso

    @staticmethod
    def normalize_action(action_str: Optional[str]) -> str:
        """Standardizes action verbs to ALLOW, DENY, CLOSE, ALERT using whole-word token matching."""
        if not action_str:
            return "ALLOW"
        act = str(action_str).upper().strip()
        tokens = set(re.split(r'[^A-Z0-9]+', act)) - {""}
        if tokens & {"DENY", "DENIED", "BLOCK", "BLOCKED", "DROP", "DROPPED", "REJECT", "REJECTED", "STOP", "FORBID", "FORBIDDEN"}:
            return "DENY"
        if tokens & {"ALLOW", "ALLOWED", "PERMIT", "PERMITTED", "ACCEPT", "ACCEPTED", "PASS", "PASSED", "SUCCESS", "OK", "OPEN", "BUILT"}:
            return "ALLOW"
        if tokens & {"CLOSE", "CLOSED", "TEARDOWN", "FIN", "RST", "TERMINATED", "TIMEOUT"}:
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
        confidence: Optional[float] = None,
        is_ai_assisted: bool = False
    ) -> UniversalEvent:
        """
        Transforms intermediate parsed key-values into a validated UniversalEvent.
        Preserves raw message lossless and creates cryptographic hash.
        """
        if confidence is None:
            try:
                confidence = float(parsed_data.get("confidence", 1.0))
            except (TypeError, ValueError):
                confidence = 1.0
        confidence = max(0.0, min(1.0, confidence))
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
