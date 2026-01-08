# Post-Mortem: Checkout Service Outage - January 2024

## Incident Summary

**Date:** January 15, 2024  
**Duration:** 2 hours 15 minutes  
**Impact:** Complete checkout service unavailability  
**Severity:** Critical (P0)

## Timeline

- **10:30 AM** - Deployment of v2.3.0 to production
- **10:35 AM** - First alerts for high error rate
- **10:40 AM** - Checkout service becomes unresponsive
- **10:45 AM** - Incident declared, on-call team paged
- **11:00 AM** - Root cause identified: database connection pool exhaustion
- **11:15 AM** - Rollback initiated
- **12:00 PM** - Rollback completed, service restored
- **12:45 PM** - Incident resolved, post-mortem scheduled

## Root Cause

The deployment of v2.3.0 introduced a bug in the database connection handling code. The new code path failed to properly release database connections, leading to connection pool exhaustion within 5 minutes of deployment.

**Technical Details:**
- Connection pool size: 20 connections
- Leak rate: ~4 connections per minute
- Pool exhausted after: ~5 minutes
- Affected endpoints: All checkout-related APIs

## Impact

- **Users Affected:** ~50,000 active users during incident
- **Revenue Impact:** ~$25,000 in lost transactions
- **SLA Impact:** 99.9% uptime target missed for the month

## Resolution

1. **Immediate:** Rolled back to v2.2.9
2. **Short-term:** Increased connection pool size to 50
3. **Long-term:** Fixed connection leak bug in v2.3.1

## Lessons Learned

### What Went Well
- Fast incident detection (5 minutes)
- Quick rollback execution (15 minutes)
- Good communication with stakeholders

### What Went Wrong
- Insufficient testing of connection handling code
- No canary deployment for high-risk changes
- Missing connection pool monitoring alerts

### Action Items

1. **Immediate (Week 1)**
   - [ ] Add connection pool monitoring alerts
   - [ ] Implement canary deployment process
   - [ ] Review all connection handling code

2. **Short-term (Month 1)**
   - [ ] Add integration tests for connection handling
   - [ ] Implement automated connection leak detection
   - [ ] Update deployment checklist

3. **Long-term (Quarter 1)**
   - [ ] Implement circuit breakers for database
   - [ ] Add chaos engineering tests
   - [ ] Improve observability for connection pools

## Prevention

- All database connection code changes require:
  - Code review by senior engineer
  - Integration tests
  - Canary deployment
  - Connection pool monitoring

## Related Incidents

- Similar issue in payment service (December 2023) - resolved with connection pool increase
