# Runbook: High API Latency

## Symptoms

- API response time > 2s (p95)
- Increased error rates
- User complaints about slow performance
- Timeout errors in client applications

## Common Causes

1. **Database connection pool exhaustion**
   - Too many concurrent connections
   - Long-running queries blocking connections
   - Connection leaks in application code

2. **Recent deployment issues**
   - New code with performance regressions
   - Configuration changes affecting performance
   - Resource limits not properly configured

3. **External service degradation**
   - Third-party API slowdowns
   - Network latency issues
   - Dependency service outages

4. **Resource constraints**
   - CPU throttling
   - Memory pressure
   - Network bandwidth limits

## Resolution Steps

### 1. Immediate Actions

1. **Check recent deployments**
   ```bash
   kubectl get deployments -n production --sort-by=.metadata.creationTimestamp
   ```
   - Review deployments in last 24 hours
   - Check for configuration changes

2. **Review database connection metrics**
   ```sql
   SELECT count(*) FROM pg_stat_activity;
   SELECT max_conn, used, reserved_for_superuser 
   FROM pg_settings WHERE name = 'max_connections';
   ```

3. **Check external service status**
   - Review dependency health dashboards
   - Check for known outages
   - Verify network connectivity

### 2. Diagnostic Commands

```bash
# Check pod resource usage
kubectl top pods -n production

# Check database query performance
SELECT query, state, wait_event_type, wait_event 
FROM pg_stat_activity 
WHERE state != 'idle' 
ORDER BY query_start;

# Check application logs
kubectl logs -f deployment/checkout-api -n production --tail=100
```

### 3. Remediation Actions

**If recent deployment:**
- Consider rollback to previous version
- Review deployment changes for performance impact
- Check for new dependencies or resource requirements

**If database issues:**
- Increase connection pool size
- Optimize slow queries
- Add database read replicas if needed

**If resource constraints:**
- Scale up pods (increase replicas)
- Increase resource limits (CPU/memory)
- Check for resource leaks

**If external service:**
- Implement circuit breakers
- Add retry logic with backoff
- Use fallback mechanisms

### 4. Prevention

- Set up alerting for latency thresholds
- Implement canary deployments
- Regular performance testing
- Database query optimization reviews
- Monitor external service health

## Related Runbooks

- [Deployment Rollback](./deployment_rollback.md)
- [OOM Errors](./oom_errors.md)
- [Database Connection Issues](./database_connections.md)

## Escalation

If latency persists after remediation:
1. Escalate to on-call engineer
2. Create incident ticket
3. Notify service owner
4. Consider emergency rollback
