/** Shared API types (mirror the backend Pydantic schemas). */

export type Severity = 'critical' | 'warning' | 'info'

export type IncidentStatus =
  | 'open'
  | 'analyzing'
  | 'awaiting_approval'
  | 'remediating'
  | 'resolved'
  | 'closed'

export type RemediationStatus =
  | 'proposed'
  | 'pending_approval'
  | 'approved'
  | 'rejected'
  | 'executing'
  | 'succeeded'
  | 'failed'
  | 'rolled_back'

export interface Token {
  access_token: string
  token_type: string
  expires_in: number
  username: string
  role: string
}

export interface User {
  username: string
  full_name: string
  email: string
  role: string
  disabled: boolean
}

export interface RecommendedAction {
  action_type: string
  target: string
  parameters: Record<string, unknown>
  rationale?: string
}

export interface Alert {
  alert_id: string
  service: string
  severity: Severity
  metric: string
  value: number
  threshold: number
  summary?: string
  labels: Record<string, unknown>
  status: string
  fingerprint: string
  fired_at: string
  incident_id?: string
  created_at: string
}

export interface Remediation {
  remediation_id: string
  incident_id: string
  action_type: string
  target: string
  parameters: Record<string, unknown>
  status: RemediationStatus
  confidence?: number
  rationale?: string
  requires_approval: boolean
  proposed_by: string
  approved_by?: string
  rejected_by?: string
  rejection_reason?: string
  result?: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface Incident {
  incident_id: string
  title: string
  service: string
  incident_type: string
  severity: Severity
  status: IncidentStatus
  root_cause?: string
  rca_summary?: Record<string, unknown>
  recommended_action?: RecommendedAction
  confidence?: number
  resolution?: string
  created_at: string
  updated_at: string
}

export interface IncidentDetail extends Incident {
  alerts: Alert[]
  remediations: Remediation[]
}

export interface KnowledgeResult {
  chunk_id: string
  doc_id: string
  title: string
  source_type: string
  content: string
  score: number
}

export interface DashboardSummary {
  incidents: {
    total: number
    open: number
    resolved: number
    by_status: Record<string, number>
  }
  alerts: { total: number }
  remediations: { total: number; succeeded: number; pending_approval: number }
}
