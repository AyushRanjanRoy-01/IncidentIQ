/**
 * Incidents page component.
 * 
 * Displays list of incidents with filtering and details.
 */

import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card } from '../components/common/Card'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { RCAViewer } from '../components/incidents/RCAViewer'
import { RemediationCard } from '../components/incidents/RemediationCard'
import { api } from '../services/api'

interface Incident {
  incident_id: string
  title: string
  status: string
  severity: string
  service: string
  created_at: string
}

const IncidentsPage: React.FC = () => {
  const [selectedIncident, setSelectedIncident] = useState<string | null>(null)

  const { data: incidents, isLoading, error } = useQuery<Incident[]>({
    queryKey: ['incidents'],
    queryFn: async () => {
      try {
        const response = await api.get('/api/v1/incidents')
        return response.data
      } catch (error) {
        // Return mock data if API is not available
        console.warn('API not available, using mock data', error)
        return [
          {
            incident_id: 'incident-001',
            title: 'High API Latency',
            status: 'open',
            severity: 'critical',
            service: 'checkout-api',
            created_at: new Date().toISOString()
          },
          {
            incident_id: 'incident-002',
            title: 'Payment API Errors',
            status: 'investigating',
            severity: 'warning',
            service: 'payment-api',
            created_at: new Date(Date.now() - 3600000).toISOString()
          }
        ]
      }
    },
  })

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (error) {
    return <div className="text-red-600">Error loading incidents</div>
  }

  return (
    <div className="p-8">
      <h1 className="text-4xl font-bold mb-8">Incidents</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <Card title="Incident List">
            <div className="space-y-2">
              {incidents?.map((incident) => (
                <div
                  key={incident.incident_id}
                  className={`p-4 border rounded-md cursor-pointer hover:bg-gray-50 ${
                    selectedIncident === incident.incident_id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200'
                  }`}
                  onClick={() => setSelectedIncident(incident.incident_id)}
                >
                  <h3 className="font-medium">{incident.title}</h3>
                  <p className="text-sm text-gray-600">{incident.service}</p>
                  <span
                    className={`inline-block mt-2 px-2 py-1 rounded text-xs ${
                      incident.severity === 'critical'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                  >
                    {incident.severity}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="lg:col-span-2 space-y-6">
          {selectedIncident ? (
            <>
              <RCAViewer incidentId={selectedIncident} />
              <RemediationCard incidentId={selectedIncident} />
            </>
          ) : (
            <Card>
              <p className="text-gray-500">Select an incident to view details</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

export default IncidentsPage
