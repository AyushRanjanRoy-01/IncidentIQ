/**
 * TypeScript type definitions.
 * 
 * Centralized type definitions for the application.
 */

export interface Alert {
  alert_id: string
  severity: 'critical' | 'warning' | 'info'
  service: string
  metric: string
  value: number
  threshold: number
  timestamp: string
  labels?: Record<string, string>
}

export interface Incident {
  incident_id: string
  title: string
  description?: string
  status: 'open' | 'investigating' | 'resolved' | 'closed'
  severity: 'critical' | 'high' | 'medium' | 'low'
  service: string
  created_at: string
  updated_at: string
  resolved_at?: string
}

export interface Remediation {
  remediation_id: string
  incident_id: string
  action_type: string
  description: string
  status: 'pending' | 'approved' | 'rejected' | 'executed' | 'completed' | 'failed'
  confidence: number
  requires_approval: boolean
  created_at: string
  executed_at?: string
}

export interface RCA {
  incident_id: string
  root_cause: string
  confidence: number
  contributing_factors: string[]
  evidence: string[]
  recommended_actions: string[]
  generated_at: string
}

export interface KnowledgeDoc {
  doc_id: string
  title: string
  type: 'runbook' | 'postmortem' | 'article'
  content: string
  tags: string[]
  created_at: string
  updated_at: string
}

export interface User {
  id: string
  name: string
  email: string
  roles: string[]
}
