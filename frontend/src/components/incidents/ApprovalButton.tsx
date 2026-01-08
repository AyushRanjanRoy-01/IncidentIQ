/**
 * Approval button component.
 * 
 * Handles remediation action approval/rejection.
 */

import React, { useState } from 'react'
import { Button } from '../common/Button'

interface ApprovalButtonProps {
  remediationId: string
  onApprove: () => void
  onReject: () => void
}

export const ApprovalButton: React.FC<ApprovalButtonProps> = ({
  remediationId,
  onApprove,
  onReject,
}) => {
  const [isLoading, setIsLoading] = useState(false)

  const handleApprove = async () => {
    setIsLoading(true)
    try {
      // TODO: Call API to approve remediation
      await onApprove()
    } finally {
      setIsLoading(false)
    }
  }

  const handleReject = async () => {
    setIsLoading(true)
    try {
      // TODO: Call API to reject remediation
      await onReject()
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex gap-2">
      <Button
        variant="primary"
        onClick={handleApprove}
        isLoading={isLoading}
        disabled={isLoading}
      >
        Approve
      </Button>
      <Button
        variant="danger"
        onClick={handleReject}
        isLoading={isLoading}
        disabled={isLoading}
      >
        Reject
      </Button>
    </div>
  )
}
