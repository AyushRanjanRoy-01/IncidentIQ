# Runbook: Deployment Rollback

## When to Rollback

- Critical bugs introduced in new deployment
- Performance degradation
- Service unavailability
- Data corruption risk
- Security vulnerabilities

## Rollback Procedures

### Kubernetes Deployment Rollback

1. **Check deployment history**
   ```bash
   kubectl rollout history deployment/<deployment-name> -n <namespace>
   ```

2. **Rollback to previous version**
   ```bash
   kubectl rollout undo deployment/<deployment-name> -n <namespace>
   ```

3. **Rollback to specific revision**
   ```bash
   kubectl rollout undo deployment/<deployment-name> -n <namespace> --to-revision=<revision-number>
   ```

4. **Monitor rollback status**
   ```bash
   kubectl rollout status deployment/<deployment-name> -n <namespace>
   ```

### Automated Rollback via Platform

1. **Via API**
   ```bash
   curl -X POST http://api/api/v1/remediations \
     -H "Content-Type: application/json" \
     -d '{
       "incident_id": "<incident-id>",
       "action_type": "rollback",
       "target": {
         "deployment": "<deployment-name>",
         "namespace": "<namespace>"
       }
     }'
   ```

2. **Via UI**
   - Navigate to incident details
   - Review suggested remediation
   - Approve rollback action
   - Monitor execution

### Post-Rollback Verification

1. **Check service health**
   - Verify endpoints responding
   - Check error rates
   - Review metrics dashboards

2. **Validate functionality**
   - Run smoke tests
   - Check critical user flows
   - Verify data integrity

3. **Monitor for stability**
   - Watch metrics for 15-30 minutes
   - Check for recurring issues
   - Review logs for errors

## Prevention

- Implement canary deployments
- Use feature flags for gradual rollouts
- Comprehensive testing before deployment
- Automated rollback triggers
- Monitoring and alerting

## Related Runbooks

- [High Latency](./high_latency.md)
- [Pod Restart](./pod_restart.md)
