# Deployment Guide

## Prerequisites

- GCP account with billing enabled
- Terraform >= 1.6.0
- kubectl configured
- Helm >= 3.0
- Docker

## Infrastructure Deployment

### 1. Configure Terraform

```bash
cd infra/terraform/environments/dev
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Plan Deployment

```bash
terraform plan
```

### 4. Apply Infrastructure

```bash
terraform apply
```

## Application Deployment

### Using Helm

```bash
# Install/upgrade
helm upgrade --install ai-sre-platform ./infra/helm/ai-sre-platform \
  --namespace ai-sre-platform \
  --create-namespace \
  --values ./infra/helm/ai-sre-platform/values-prod.yaml

# Verify
kubectl get pods -n ai-sre-platform
```

### Using GitOps (ArgoCD)

1. Install ArgoCD in cluster
2. Create ArgoCD application from `infra/gitops/argocd/applications/`
3. ArgoCD will sync automatically

## Environment-Specific Configuration

### Development
- Lower resource limits
- Single replica
- Debug logging enabled

### Production
- Higher resource limits
- Multiple replicas
- Production logging
- Security hardening

## Monitoring Setup

1. Deploy Prometheus
2. Deploy Grafana
3. Import dashboards from `monitoring/grafana/dashboards/`
4. Configure alert rules

## Verification

```bash
# Check pods
kubectl get pods -n ai-sre-platform

# Check services
kubectl get svc -n ai-sre-platform

# Check ingress
kubectl get ingress -n ai-sre-platform

# View logs
kubectl logs -f deployment/backend -n ai-sre-platform
```

## Rollback

```bash
# Helm rollback
helm rollback ai-sre-platform -n ai-sre-platform

# Kubernetes rollback
kubectl rollout undo deployment/backend -n ai-sre-platform
```
