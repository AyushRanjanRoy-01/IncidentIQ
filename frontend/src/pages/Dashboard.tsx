import React from 'react'
import { AlertsDashboard } from '../components/dashboard/AlertsDashboard'
import { AnomalyChart } from '../components/dashboard/AnomalyChart'
import { IncidentTimeline } from '../components/dashboard/IncidentTimeline'

/**
 * Dashboard page component
 * Main view showing alerts, incidents, and anomalies
 */
export const Dashboard: React.FC = () => {
  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <h1 className="text-4xl font-bold mb-8 text-gray-900">SRE Dashboard</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="lg:col-span-2">
          <AlertsDashboard />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <AnomalyChart 
          metricName="API Latency (p95)"
          data={[
            { timestamp: '2024-01-09T10:00:00Z', value: 500, isAnomaly: false },
            { timestamp: '2024-01-09T10:05:00Z', value: 520, isAnomaly: false },
            { timestamp: '2024-01-09T10:10:00Z', value: 2500, isAnomaly: true },
            { timestamp: '2024-01-09T10:15:00Z', value: 2400, isAnomaly: true },
          ]}
        />
        <IncidentTimeline 
          incidentId="incident-001"
          events={[
            {
              timestamp: '2024-01-09T10:30:00Z',
              type: 'Incident Created',
              description: 'High API latency detected in checkout-api',
              user: 'system'
            },
            {
              timestamp: '2024-01-09T10:35:00Z',
              type: 'RCA Generated',
              description: 'Root cause: Database connection pool exhaustion',
              user: 'ai-agent'
            },
            {
              timestamp: '2024-01-09T10:40:00Z',
              type: 'Remediation Suggested',
              description: 'Rollback deployment to v2.2.9',
              user: 'ai-agent'
            }
          ]}
        />
      </div>
    </div>
  )
}

export default Dashboard
