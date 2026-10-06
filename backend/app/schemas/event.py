from datetime import datetime, timezone
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field

class SourceDetails(BaseModel):
    vendor: Optional[str] = Field(default=None, description="Vendor name, e.g. Cisco, Fortinet, Palo Alto")
    product: Optional[str] = Field(default=None, description="Product line, e.g. ASA, FortiGate, PAN-OS")
    device_name: Optional[str] = Field(default=None, description="Host name or device identifier")
    device_ip: Optional[str] = Field(default=None, description="IP address of generating device")
    format: Optional[str] = Field(default=None, description="Format detected: syslog, json, cef, custom")

class NetworkDetails(BaseModel):
    source_ip: Optional[str] = Field(default=None, description="Originating IPv4 or IPv6 address")
    source_port: Optional[int] = Field(default=None, description="Source port number")
    destination_ip: Optional[str] = Field(default=None, description="Destination IPv4 or IPv6 address")
    destination_port: Optional[int] = Field(default=None, description="Destination port number")
    protocol: Optional[str] = Field(default=None, description="Network protocol: TCP, UDP, ICMP, etc.")

class EventClassification(BaseModel):
    category: Optional[str] = Field(default="network", description="Category: network, authentication, system")
    type: Optional[str] = Field(default="firewall", description="Type: firewall, vpn, dns, ssh, login")
    action: Optional[str] = Field(default="ALLOW", description="Action: ALLOW, DENY, BLOCK, DROP, ALERT")
    severity: Optional[str] = Field(default="low", description="Severity: low, medium, high, critical")
    outcome: Optional[str] = Field(default=None, description="Outcome: success, failure, blocked")

class UserDetails(BaseModel):
    username: Optional[str] = Field(default=None, description="Account or user identifier")
    domain: Optional[str] = Field(default=None, description="Domain name")

class RawDetails(BaseModel):
    message: str = Field(..., description="Original raw event log string without modification")

class ProcessingDetails(BaseModel):
    parser: str = Field(..., description="Name of parser responsible for extraction")
    parser_version: str = Field(default="1.0.0", description="Parser version")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence score")
    is_ai_assisted: bool = Field(default=False, description="Flag indicating if parser was AI generated")

class IntegrityDetails(BaseModel):
    sha256: str = Field(..., description="Cryptographic SHA-256 fingerprint of the raw message")
    verified: bool = Field(default=True, description="Integrity check status against raw log")

class UniversalEvent(BaseModel):
    event_id: str = Field(..., description="Unique event identifier (e.g. evt_xxxxxx)")
    timestamp: str = Field(..., description="ISO 8601 formatted event occurrence timestamp")
    source: SourceDetails = Field(default_factory=SourceDetails)
    network: NetworkDetails = Field(default_factory=NetworkDetails)
    event: EventClassification = Field(default_factory=EventClassification)
    user: UserDetails = Field(default_factory=UserDetails)
    raw: RawDetails = Field(..., description="Preserved original raw event")
    processing: ProcessingDetails = Field(..., description="Parser execution metadata")
    integrity: IntegrityDetails = Field(..., description="Cryptographic hash integrity")
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EventProcessRequest(BaseModel):
    raw_log: str = Field(..., min_length=1, description="Raw log text to parse and normalize")
    source_hint: Optional[str] = Field(default=None, description="Optional vendor/format hint")

class EventProcessResponse(BaseModel):
    success: bool
    event: Optional[UniversalEvent] = None
    message: str
    error: Optional[str] = None

class BatchProcessRequest(BaseModel):
    logs: list[str] = Field(..., min_length=1, description="List of raw log strings")

class BatchProcessResponse(BaseModel):
    processed_count: int
    success_count: int
    failure_count: int
    events: list[UniversalEvent]
    errors: list[dict[str, Any]] = []
