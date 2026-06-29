import React from 'react'

import { Badge, Button, Card, Spinner } from '@/components/ui'
import {
  useApproveRemediation,
  useIncident,
  useRejectRemediation,
} from '@/hooks/useApi'
import { useAuthStore } from '@/store'
import type { Remediation } from '@/types'

const canOperate = (role: string | null) => role === 'operator' || role === 'admin'

const RemediationRow: React.FC<{
  rem: Remediation
  incidentId: string
}> = ({ rem, incidentId }) => {
  const role = useAuthStore((s) => s.role)
  const approve = useApproveRemediation(incidentId)
  const reject = useRejectRemediation(incidentId)
  const pending = rem.status === 'pending_approval' || rem.status === 'proposed'

  return (
    <div className="border border-gray-100 rounded p-3 space-y-2">
      <div className="flex items-center justify-between">
        <div className="font-medium text-gray-800">
          {rem.action_type} → {rem.target}
        </div>
        <Badge value={rem.status} />
      </div>
      {rem.rationale && <p className="text-sm text-gray-600">{rem.rationale}</p>}
      <div className="text-xs text-gray-500">
        proposed by {rem.proposed_by}
        {rem.approved_by && ` · approved by ${rem.approved_by}`}
        {rem.rejected_by && ` · rejected by ${rem.rejected_by}`}
      </div>
      {pending && canOperate(role) && (
        <div className="flex gap-2 pt-1">
          <Button
            onClick={() => approve.mutate(rem.remediation_id)}
            disabled={approve.isPending}
          >
            {approve.isPending ? 'Executing…' : 'Approve & execute'}
          </Button>
          <Button
            variant="danger"
            onClick={() =>
              reject.mutate({ id: rem.remediation_id, reason: 'Rejected from dashboard' })
            }
            disabled={reject.isPending}
          >
            Reject
          </Button>
        </div>
      )}
    </div>
  )
}

const IncidentDetailPage: React.FC<{ incidentId: string; onBack: () => void }> = ({
  incidentId,
  onBack,
}) => {
  const { data: incident, isLoading } = useIncident(incidentId)

  if (isLoading || !incident) return <Spinner />

  const evidence = (incident.rca_summary?.evidence as string[] | undefined) ?? []

  return (
    <div className="space-y-4">
      <button className="text-sm text-blue-600" onClick={onBack}>
        ← Back
      </button>

      <Card>
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{incident.title}</h2>
            <p className="text-sm text-gray-500">
              {incident.service} · {incident.incident_type}
            </p>
          </div>
          <div className="flex gap-2">
            <Badge value={incident.severity} />
            <Badge value={incident.status} />
          </div>
        </div>
      </Card>

      <Card title="Root cause analysis">
        {incident.root_cause ? (
          <div className="space-y-3">
            <p className="text-gray-800">{incident.root_cause}</p>
            {incident.confidence != null && (
              <div className="text-sm text-gray-500">
                Confidence: {Math.round(incident.confidence * 100)}%
              </div>
            )}
            {evidence.length > 0 && (
              <ul className="list-disc list-inside text-sm text-gray-600">
                {evidence.map((e, i) => (
                  <li key={i}>{e}</li>
                ))}
              </ul>
            )}
            {incident.recommended_action && (
              <div className="bg-blue-50 border border-blue-100 rounded p-3 text-sm">
                <span className="font-medium">Recommended action:</span>{' '}
                {incident.recommended_action.action_type} → {incident.recommended_action.target}
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-500">Analysis pending…</p>
        )}
      </Card>

      <Card title="Remediations (human-in-the-loop)">
        {incident.remediations.length > 0 ? (
          <div className="space-y-3">
            {incident.remediations.map((rem) => (
              <RemediationRow key={rem.remediation_id} rem={rem} incidentId={incidentId} />
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">No remediations proposed.</p>
        )}
      </Card>

      <Card title="Triggering alerts">
        <ul className="text-sm text-gray-700 space-y-1">
          {incident.alerts.map((a) => (
            <li key={a.alert_id}>
              <Badge value={a.severity} /> {a.metric} = {a.value} (threshold {a.threshold})
            </li>
          ))}
        </ul>
      </Card>
    </div>
  )
}

export default IncidentDetailPage
