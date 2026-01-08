/**
 * Remediation card component.
 * 
 * Displays remediation actions and approval status.
 */

import React from 'react'
import { Card } from '../common/Card'
import { Button } from '../common/Button'
import { ApprovalButton } from './ApprovalButton'

interface RemediationAction {
  remediation_id: string
  action_type: string
  description: string
  status: 'pending' | 'approved' | 'rejected' | 'executed' | 'completed'
  confidence: number
  requires_approval: boolean
}

interface RemediationCardProps {
  incidentId: string
  remediation?: RemediationAction
}

export const RemediationCard: React.FC<RemediationCardProps> = ({
  incidentId,
  remediation,
}) => {
  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-blue-100 text-blue-800',
    rejected: 'bg-red-100 text-red-800',
    executed: 'bg-green-100 text-green-800',
    completed: 'bg-gray-100 text-gray-800',
  }

  // Mock data for preview
  const mockRemediation: RemediationAction = remediation || {
    remediation_id: 'remediation-001',
    action_type: 'Rollback Deployment',
    description: 'Rollback checkout-api deployment to v2.2.9 to resolve connection pool issue',
    status: 'pending',
    confidence: 0.9,
    requires_approval: true
  }

  const displayRemediation = remediation || mockRemediation

  return (
    <Card title="Remediation Action">
      <div className="space-y-4">
        <div>
          <h3 className="font-semibold mb-1">Action Type</h3>
          <p className="text-gray-700">{displayRemediation.action_type}</p>
        </div>

        <div>
          <h3 className="font-semibold mb-1">Description</h3>
          <p className="text-gray-700">{displayRemediation.description}</p>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <span className="text-sm text-gray-600">Status: </span>
            <span
              className={`px-2 py-1 rounded text-xs font-medium ${
                statusColors[displayRemediation.status]
              }`}
            >
              {displayRemediation.status}
            </span>
          </div>
          <div>
            <span className="text-sm text-gray-600">Confidence: </span>
            <span className="font-medium">
              {(displayRemediation.confidence * 100).toFixed(1)}%
            </span>
          </div>
        </div>

        {displayRemediation.requires_approval && displayRemediation.status === 'pending' && (
          <div className="flex gap-2">
            <ApprovalButton
              remediationId={displayRemediation.remediation_id}
              onApprove={() => {
                console.log('Approved remediation')
              }}
              onReject={() => {
                console.log('Rejected remediation')
              }}
            />
          </div>
        )}
      </div>
    </Card>
  )
}
