import React from 'react'

import { Badge, Card, Spinner } from '@/components/ui'
import { useIncidents } from '@/hooks/useApi'
import type { Incident } from '@/types'

const IncidentsPage: React.FC<{ onSelect: (id: string) => void }> = ({ onSelect }) => {
  const { data, isLoading } = useIncidents()

  return (
    <Card title="Incidents">
      {isLoading ? (
        <Spinner />
      ) : data && data.length > 0 ? (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b border-gray-100">
              <th className="py-2">Incident</th>
              <th>Service</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {data.map((inc: Incident) => (
              <tr
                key={inc.incident_id}
                className="border-b border-gray-50 hover:bg-gray-50 cursor-pointer"
                onClick={() => onSelect(inc.incident_id)}
              >
                <td className="py-2 font-medium text-gray-800">{inc.title}</td>
                <td>{inc.service}</td>
                <td>
                  <Badge value={inc.severity} />
                </td>
                <td>
                  <Badge value={inc.status} />
                </td>
                <td>{inc.confidence != null ? `${Math.round(inc.confidence * 100)}%` : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="text-sm text-gray-500">No incidents yet.</p>
      )}
    </Card>
  )
}

export default IncidentsPage
