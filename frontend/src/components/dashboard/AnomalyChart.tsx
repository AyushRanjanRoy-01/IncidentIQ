/**
 * Anomaly chart component.
 * 
 * Displays time-series chart of anomaly detection results.
 */

import React from 'react'
import { Card } from '../common/Card'

interface AnomalyDataPoint {
  timestamp: string
  value: number
  isAnomaly: boolean
}

interface AnomalyChartProps {
  data?: AnomalyDataPoint[]
  metricName?: string
}

export const AnomalyChart: React.FC<AnomalyChartProps> = ({
  data = [],
  metricName = 'Metric',
}) => {
  // TODO: Integrate with charting library (recharts, chart.js, etc.)
  // TODO: Implement time-series visualization
  // TODO: Highlight anomaly points

  return (
    <Card title={`${metricName} - Anomaly Detection`}>
      <div className="h-64 flex items-center justify-center text-gray-500">
        {/* Placeholder for chart */}
        <p>Chart visualization will be implemented here</p>
        <p className="text-sm mt-2">
          {data.length} data points available
        </p>
      </div>
    </Card>
  )
}
