from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class FieldMappingRule(BaseModel):
    source_field: str = Field(..., description="Field extracted from raw log (e.g. SRC, srcip, client)")
    target_field: str = Field(..., description="Dot notation target path in Universal Schema, e.g. network.source_ip")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    transform: Optional[str] = Field(default=None, description="Optional transformation rule, e.g. upper, lower, int")

class ParserDefinition(BaseModel):
    parser_id: str = Field(..., description="Unique parser ID, e.g. parser_cisco_asa or parser_custom_xxxx")
    name: str = Field(..., description="Human-readable parser name")
    vendor: str = Field(..., description="Vendor/Source name")
    format: str = Field(..., description="Format family: syslog, kv, json, cef, regex, custom")
    mapping: Dict[str, str] = Field(default_factory=dict, description="Dictionary of source_field -> target_schema_field")
    signature_pattern: Optional[str] = Field(default=None, description="Regex pattern or keyword identifying this log type")
    extraction_pattern: Optional[str] = Field(default=None, description="Regex pattern with named groups for extraction")
    delimiter: Optional[str] = Field(default=None, description="Delimiter for key-value or delimited formats")
    version: str = Field(default="1.0.0")
    is_active: bool = Field(default=True)
    is_builtin: bool = Field(default=False)
    created_by: str = Field(default="system")
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updatedAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ParserApprovalRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Name for the newly created parser")
    vendor: str = Field(..., min_length=2, max_length=100, description="Detected or custom vendor name")
    format: str = Field(default="custom", description="Log format")
    sample_log: str = Field(..., description="Sample log line used to build parser")
    mapping: Dict[str, str] = Field(..., description="Mapping of source fields to universal schema dot paths")
    extraction_regex: Optional[str] = Field(default=None, description="Regex used for field extraction")
    delimiter: Optional[str] = Field(default=None, description="Key-value delimiter if applicable")
    event_type: Optional[str] = Field(default="firewall", description="Identified event type")

class ParserUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2)
    is_active: Optional[bool] = None
