/**
 * Alerts dashboard component.
 * 
 * Displays active alerts with filtering and sorting capabilities.
 */

import React, { useState } from 'react'
import { useAlerts } from '../../hooks/useAlerts'
import { Card } from '../common/Card'
import { LoadingSpinner } from '../common/LoadingSpinner'

export const AlertsDashboard: React.FC = () => {
  const { data: alerts, isLoading, error } = useAlerts()
  const [filter, setFilter] = useState<string>('all')

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (error) {
    return <div className="text-red-600">Error loading alerts</div>
  }

  // Mock data for preview (remove when API is connected)
  const mockAlerts = alerts || [
    {
      alert_id: 'alert-001',
      severity: 'critical' as const,
      service: 'checkout-api',
      metric: 'api_latency_p95',
      value: 2500,
      threshold: 1000,
      timestamp: new Date().toISOString()
    },
    {
      alert_id: 'alert-002',
      severity: 'warning' as const,
      service: 'payment-api',
      metric: 'error_rate',
      value: 0.025,
      threshold: 0.01,
      timestamp: new Date().toISOString()
    }
  ]

  const filteredAlerts = mockAlerts.filter((alert) => {
    if (filter === 'all') return true
    return alert.severity === filter
  })

  return (
    <Card title="Active Alerts">
      <div className="mb-4">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md"
        >
          <option value="all">All Severities</option>
          <option value="critical">Critical</option>
          <option value="warning">Warning</option>
          <option value="info">Info</option>
        </select>
      </div>

      <div className="space-y-2">
        {filteredAlerts.length === 0 ? (
          <p className="text-gray-500">No alerts found</p>
        ) : (
          filteredAlerts.map((alert) => (
            <div
              key={alert.alert_id}
              className="p-4 border border-gray-200 rounded-md hover:bg-gray-50"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium">{alert.service}</h3>
                  <p className="text-sm text-gray-600">{alert.metric}</p>
                </div>
                <span
                  className={`px-2 py-1 rounded text-xs font-medium ${
                    alert.severity === 'critical'
                      ? 'bg-red-100 text-red-800'
                      : alert.severity === 'warning'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-blue-100 text-blue-800'
                  }`}
                >
                  {alert.severity}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  )
}
