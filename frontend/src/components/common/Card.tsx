/**
 * Card component.
 * 
 * Reusable card container component.
 */

import React from 'react'

interface CardProps {
  title?: string
  children: React.ReactNode
  className?: string
  headerActions?: React.ReactNode
}

export const Card: React.FC<CardProps> = ({
  title,
  children,
  className = '',
  headerActions,
}) => {
  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      {title && (
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
          {headerActions && <div>{headerActions}</div>}
        </div>
      )}
      <div>{children}</div>
    </div>
  )
}
