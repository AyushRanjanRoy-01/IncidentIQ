/**
 * Incident timeline component.
 * 
 * Displays chronological timeline of incidents.
 */

import React from 'react'
import { Card } from '../common/Card'

interface IncidentEvent {
  timestamp: string
  type: string
  description: string
  user?: string
}

interface IncidentTimelineProps {
  incidentId: string
  events?: IncidentEvent[]
}

export const IncidentTimeline: React.FC<IncidentTimelineProps> = ({
  incidentId,
  events = [],
}) => {
  // TODO: Fetch incident events from API
  // TODO: Implement timeline visualization

  return (
    <Card title="Incident Timeline">
      <div className="space-y-4">
        {events.length === 0 ? (
          <p className="text-gray-500">No events recorded</p>
        ) : (
          events.map((event, index) => (
            <div key={index} className="flex items-start">
              <div className="flex-shrink-0 w-2 h-2 bg-blue-600 rounded-full mt-2" />
              <div className="ml-4 flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{event.type}</span>
                  <span className="text-xs text-gray-500">{event.timestamp}</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{event.description}</p>
                {event.user && (
                  <p className="text-xs text-gray-500 mt-1">by {event.user}</p>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  )
}
