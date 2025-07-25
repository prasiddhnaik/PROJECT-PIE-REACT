# Deploying the Backend with Helm

This repository ships a reusable Helm chart located at `charts/backend`.

## Prerequisites
1. Kubernetes cluster (KIND, k3d, AKS, EKS, GKE…)
2. [Helm v3](https://helm.sh/) installed locally
3. Container registry with the `fa-backend` image pushed (or use `docker build` & `kind load`).

## Quick start
```bash
# generate an override file with your secrets
cat > my-values.yaml <<EOF
image:
  repository: ghcr.io/<your-org>/fa-backend
  tag: v2.2.0

env:
  ALPHA_VANTAGE_API_KEY: "YOUR_KEY"
  FINNHUB_API_KEY: "..."
EOF

# install / upgrade release
helm upgrade --install backend charts/backend \
  --namespace fa --create-namespace \
  -f my-values.yaml
```

The service will be exposed internally on `backend.fa.svc.cluster.local:8000` (ClusterIP by default).

Enable an ingress controller by setting:
```yaml
ingress:
  enabled: true
  hosts:
    - host: api.your-domain.com
      paths:
        - path: /
          pathType: Prefix
```

## Development loop
```bash
# package chart (optional)
helm package charts/backend

# dry-run template with overrides
helm template backend charts/backend -f my-values.yaml | kubectl apply -f -
```

---
Feel free to duplicate the chart for the web app (`charts/web`) once the container image is available. 
 
 
 