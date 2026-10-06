from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class SourceMetadata(BaseModel):
    source_id: str = Field(..., description="Unique source identifier")
    name: str = Field(..., description="Device or source name")
    vendor: str = Field(..., description="Vendor name: Cisco, Fortinet, Palo Alto, Generic, etc.")
    format: str = Field(..., description="Format: syslog, json, cef, custom")
    status: str = Field(default="active", description="Status: active, inactive, degraded")
    event_count: int = Field(default=0, ge=0, description="Total events ingested from this source")
    last_seen: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
