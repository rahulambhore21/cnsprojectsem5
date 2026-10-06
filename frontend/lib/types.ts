export interface SourceDetails {
  vendor: string | null;
  product: string | null;
  device_name: string | null;
  device_ip: string | null;
  format: string | null;
}

export interface NetworkDetails {
  source_ip: string | null;
  source_port: number | null;
  destination_ip: string | null;
  destination_port: number | null;
  protocol: string | null;
}

export interface EventClassification {
  category: string;
  type: string;
  action: string;
  severity: string;
  outcome: string | null;
}

export interface UserDetails {
  username: string | null;
  domain: string | null;
}

export interface RawDetails {
  message: string;
}

export interface ProcessingDetails {
  parser: string;
  parser_version: string;
  confidence: number;
  is_ai_assisted: boolean;
}

export interface IntegrityDetails {
  sha256: string;
  verified: boolean;
}

export interface UniversalEvent {
  event_id: string;
  timestamp: string;
  source: SourceDetails;
  network: NetworkDetails;
  event: EventClassification;
  user: UserDetails;
  raw: RawDetails;
  processing: ProcessingDetails;
  integrity: IntegrityDetails;
  createdAt: string;
}

export interface DashboardStats {
  total_events: number;
  processed_events: number;
  blocked_events: number;
  threat_events: number;
  active_sources: number;
  unknown_sources: number;
  timestamp: string;
}

export interface DistributionAction {
  name: string;
  action: string;
  count: number;
  color: string;
}

export interface DistributionSeverity {
  severity: string;
  count: number;
  fill: string;
}

export interface DistributionTimeline {
  time: string;
  count: number;
}

export interface EventDistribution {
  actions: DistributionAction[];
  severities: DistributionSeverity[];
  timeline: DistributionTimeline[];
}

export interface TopSource {
  vendor: string;
  count: number;
}

export interface AIFieldMapping {
  source_field: string;
  target_field: string;
  confidence: number;
  sample_value?: string;
  description?: string;
}

export interface AIAnalysisResponse {
  detected_vendor: string;
  detected_format: string;
  event_type: string;
  confidence: number;
  mappings: AIFieldMapping[];
  extracted_fields: Record<string, any>;
  suggested_delimiter?: string | null;
  suggested_regex?: string | null;
  reasoning: string;
  normalized_preview?: Record<string, any>;
}

export interface ParserItem {
  parser_id: string;
  name: string;
  vendor: string;
  format: string;
  version: string;
  is_builtin: boolean;
  is_active: boolean;
  description?: string;
  mapping?: Record<string, string>;
  createdAt?: string;
}

export interface SourceItem {
  source_id: string;
  name: string;
  vendor: string;
  format: string;
  status: string;
  event_count: number;
  last_seen: string;
  createdAt: string;
}
