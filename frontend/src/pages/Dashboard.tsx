import React from 'react'

import { Badge, Card, Spinner } from '@/components/ui'
import { useIncidents, useStats } from '@/hooks/useApi'
import type { Incident } from '@/types'

const Stat: React.FC<{ label: string; value: number | string; accent?: string }> = ({
  label,
  value,
  accent = 'text-gray-900',
}) => (
  <Card>
    <div className="text-sm text-gray-500">{label}</div>
    <div className={`text-3xl font-bold ${accent}`}>{value}</div>
  </Card>
)

const Dashboard: React.FC<{ onSelect: (id: string) => void }> = ({ onSelect }) => {
  const stats = useStats()
  const incidents = useIncidents()

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.isLoading || !stats.data ? (
          <div className="col-span-4">
            <Spinner />
          </div>
        ) : (
          <>
            <Stat label="Open incidents" value={stats.data.incidents.open} accent="text-amber-600" />
            <Stat label="Total incidents" value={stats.data.incidents.total} />
            <Stat label="Alerts ingested" value={stats.data.alerts.total} />
            <Stat
              label="Auto-remediations"
              value={stats.data.remediations.succeeded}
              accent="text-green-600"
            />
          </>
        )}
      </div>

      <Card title="Recent incidents">
        {incidents.isLoading ? (
          <Spinner />
        ) : incidents.data && incidents.data.length > 0 ? (
          <ul className="divide-y divide-gray-100">
            {incidents.data.slice(0, 8).map((inc: Incident) => (
              <li
                key={inc.incident_id}
                className="py-3 flex items-center justify-between cursor-pointer hover:bg-gray-50 -mx-2 px-2 rounded"
                onClick={() => onSelect(inc.incident_id)}
              >
                <div>
                  <div className="font-medium text-gray-800">{inc.title}</div>
                  <div className="text-xs text-gray-500">
                    {inc.service} ·{' '}
                    {inc.confidence != null ? `confidence ${Math.round(inc.confidence * 100)}%` : 'analyzing'}
                  </div>
                </div>
                <div className="flex gap-2">
                  <Badge value={inc.severity} />
                  <Badge value={inc.status} />
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-500">No incidents yet. Ingest an alert to get started.</p>
        )}
      </Card>
    </div>
  )
}

export default Dashboard
