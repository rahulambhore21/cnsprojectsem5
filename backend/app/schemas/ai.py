from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field

class AIFieldMapping(BaseModel):
    source_field: str = Field(..., description="Original raw field name or parameter extracted")
    target_field: str = Field(..., description="Target universal schema dot path (e.g. network.source_ip)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    sample_value: Optional[str] = Field(default=None, description="Sample extracted value from log")
    description: Optional[str] = Field(default=None, description="Contextual explanation of field purpose")

class AIAnalysisRequest(BaseModel):
    raw_log: str = Field(..., min_length=1, description="Raw unparsed log to analyze with AI")
    context_hint: Optional[str] = Field(default=None, description="Optional vendor/source hint provided by user")

class AIAnalysisResponse(BaseModel):
    detected_vendor: str = Field(..., description="Detected vendor name or 'Unknown'")
    detected_format: str = Field(..., description="Detected log structure: Key-Value, Syslog, Delimited, JSON, Custom")
    event_type: str = Field(..., description="Identified event type: firewall, vpn, auth, system, proxy, web")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall detection confidence score")
    mappings: List[AIFieldMapping] = Field(default_factory=list, description="Array of suggested field mappings")
    extracted_fields: Dict[str, Any] = Field(default_factory=dict, description="Raw key-value pairs extracted from sample log")
    suggested_delimiter: Optional[str] = Field(default=None, description="Suggested delimiter if key-value or delimited")
    suggested_regex: Optional[str] = Field(default=None, description="Suggested extraction regex if positional format")
    reasoning: str = Field(default="", description="Explanation of how the AI identified the structure and mappings")
    normalized_preview: Optional[Dict[str, Any]] = Field(default=None, description="Preview of normalized event using this mapping")
