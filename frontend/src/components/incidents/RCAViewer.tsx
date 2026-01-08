/**
 * Root Cause Analysis viewer component.
 * 
 * Displays AI-generated root cause analysis for incidents.
 */

import React from 'react'
import { Card } from '../common/Card'

interface RCAData {
  incident_id: string
  root_cause: string
  confidence: number
  contributing_factors: string[]
  evidence: string[]
  recommended_actions: string[]
}

interface RCAViewerProps {
  incidentId: string
  rcaData?: RCAData
}

export const RCAViewer: React.FC<RCAViewerProps> = ({
  incidentId,
  rcaData,
}) => {
  // Mock data for preview
  const mockRcaData: RCAData = rcaData || {
    incident_id: incidentId,
    root_cause: 'Database connection pool exhaustion due to connection leak in v2.3.0 deployment',
    confidence: 0.9,
    contributing_factors: [
      'Recent deployment of v2.3.0',
      'Connection pool size set to 20 (too low)',
      'Missing connection cleanup in error paths'
    ],
    evidence: [
      'Database connection count reached 20/20',
      'Deployment occurred 5 minutes before incident',
      'Error logs show connection timeout errors'
    ],
    recommended_actions: [
      'Rollback deployment to v2.2.9',
      'Increase connection pool size to 50',
      'Fix connection leak in v2.3.1'
    ]
  }

  // Always use mock data for preview (will be replaced with API call later)
  const displayData = rcaData || mockRcaData

  return (
    <Card title="Root Cause Analysis">
      <div className="space-y-6">
        <div>
          <h3 className="font-semibold mb-2">Root Cause</h3>
          <p className="text-gray-700">{displayData.root_cause}</p>
        </div>

        <div>
          <h3 className="font-semibold mb-2">Confidence Score</h3>
          <div className="flex items-center">
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${displayData.confidence * 100}%` }}
              />
            </div>
            <span className="ml-2 text-sm font-medium">
              {(displayData.confidence * 100).toFixed(1)}%
            </span>
          </div>
        </div>

        <div>
          <h3 className="font-semibold mb-2">Contributing Factors</h3>
          <ul className="list-disc list-inside space-y-1">
            {displayData.contributing_factors.map((factor, index) => (
              <li key={index} className="text-gray-700">
                {factor}
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="font-semibold mb-2">Evidence</h3>
          <ul className="list-disc list-inside space-y-1">
            {displayData.evidence.map((item, index) => (
              <li key={index} className="text-gray-700">
                {item}
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="font-semibold mb-2">Recommended Actions</h3>
          <ul className="list-disc list-inside space-y-1">
            {displayData.recommended_actions.map((action, index) => (
              <li key={index} className="text-gray-700">
                {action}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Card>
  )
}
