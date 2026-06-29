/** Small shared UI primitives (cards, badges, buttons, spinner). */

import React from 'react'

export const Card: React.FC<{ title?: string; children: React.ReactNode; className?: string }> = ({
  title,
  children,
  className = '',
}) => (
  <div className={`bg-white rounded-lg shadow-sm border border-gray-100 ${className}`}>
    {title && <div className="px-4 py-3 border-b border-gray-100 font-semibold text-gray-800">{title}</div>}
    <div className="p-4">{children}</div>
  </div>
)

const TONE: Record<string, string> = {
  critical: 'bg-red-100 text-red-700',
  warning: 'bg-amber-100 text-amber-700',
  info: 'bg-sky-100 text-sky-700',
  open: 'bg-gray-100 text-gray-700',
  analyzing: 'bg-indigo-100 text-indigo-700',
  awaiting_approval: 'bg-amber-100 text-amber-700',
  remediating: 'bg-blue-100 text-blue-700',
  resolved: 'bg-green-100 text-green-700',
  closed: 'bg-gray-100 text-gray-500',
  pending_approval: 'bg-amber-100 text-amber-700',
  succeeded: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
  rejected: 'bg-gray-200 text-gray-600',
}

export const Badge: React.FC<{ value: string }> = ({ value }) => (
  <span
    className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
      TONE[value] ?? 'bg-gray-100 text-gray-700'
    }`}
  >
    {value.replace(/_/g, ' ')}
  </span>
)

export const Button: React.FC<
  React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'danger' | 'ghost' }
> = ({ variant = 'primary', className = '', ...props }) => {
  const styles =
    variant === 'danger'
      ? 'bg-red-600 hover:bg-red-700 text-white'
      : variant === 'ghost'
        ? 'bg-gray-100 hover:bg-gray-200 text-gray-700'
        : 'bg-blue-600 hover:bg-blue-700 text-white'
  return (
    <button
      className={`px-3 py-1.5 rounded text-sm font-medium disabled:opacity-50 ${styles} ${className}`}
      {...props}
    />
  )
}

export const Spinner: React.FC = () => (
  <div className="flex justify-center py-8">
    <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600" />
  </div>
)
