# Runbook: Out of Memory (OOM) Errors

## Symptoms

- Pods being killed with OOMKilled status
- Application crashes with memory errors
- High memory usage metrics
- System instability

## Common Causes

1. **Memory leaks**
   - Unclosed connections
   - Growing caches without limits
   - Unbounded data structures

2. **Insufficient memory limits**
   - Memory requests/limits too low
   - Sudden traffic spikes
   - Large data processing

3. **Resource contention**
   - Multiple services competing for memory
   - Node memory exhaustion
   - Memory fragmentation

## Resolution Steps

### 1. Immediate Actions

1. **Check pod status**
   ```bash
   kubectl get pods -n production | grep OOMKilled
   kubectl describe pod <pod-name> -n production
   ```

2. **Review memory metrics**
   ```bash
   kubectl top pods -n production
   ```

3. **Check application logs**
   ```bash
   kubectl logs <pod-name> -n production --previous
   ```

### 2. Diagnostic Commands

```bash
# Check memory usage by pod
kubectl top pods -n production --sort-by=memory

# Check node memory
kubectl top nodes

# Check memory limits
kubectl get deployment <deployment-name> -n production -o yaml | grep -A 5 resources
```

### 3. Remediation Actions

**Temporary fix:**
- Restart affected pods
- Scale up replicas to distribute load
- Increase memory limits (if headroom available)

**Permanent fix:**
- Identify and fix memory leaks
- Optimize memory usage in code
- Set appropriate memory requests/limits
- Implement memory monitoring and alerting

### 4. Prevention

- Set memory limits based on actual usage
- Implement memory profiling
- Regular memory leak detection
- Monitor memory trends
- Set up alerts for high memory usage

## Related Runbooks

- [High Latency](./high_latency.md)
- [Pod Restart](./pod_restart.md)
