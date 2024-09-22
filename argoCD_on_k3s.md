## How to deploy Argo CD on k3s cluster

## Pre-Requisites
Install helm
```
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

Add helm repo for jetstack (cert-manager)
```
helm repo add jetstack https://charts.jetstack.io
helm repo update
```

Next install **cert-manager** with
```
kubectl create namespace cert-manager
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --version v1.14.1 \
  --set installCRDs=true
```

Add your DigitalOcean API token first for auto DNS verification
```
kubectl create secret generic digitalocean-dns-token \
  --from-literal=access-token=$DOKEYK8S \
  --namespace cert-manager
```
_Either insert the key above or use the env var $DOKEYK8S_

Create and deploy clusterIssuer.yaml
```
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-digitalocean
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: EMAIL@EXAMPLE.COM  # CHANGE THIS
    privateKeySecretRef:
      name: letsencrypt-digitalocean-key
    solvers:
    - dns01:
        digitalocean:
          tokenSecretRef:
            name: digitalocean-dns-token  #CHANGE THIS IF DIFFERENT
            key: access-token
```
---

## Instructions for ArgoCD
1. Install ArgoCD
```
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

2. Create and deploy an `argocd-ingress.yaml`
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: argocd-ingress
  namespace: argocd
  annotations:
    kubernetes.io/ingress.class: traefik  # Change this to your Ingress controller
spec:
  rules:
  - host: argocd.example.com # Change to your desired hostname
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: argocd-server
            port:
              number: 80
  tls:
  - hosts:
    - argocd.example.com # Use your domain name
    secretName: argocd-tls # Create a TLS secret using cert-manager if required
```
3. Fix Redirect Issue
Nginx may only be listening on 443 by default at the pod level, which breaks things.
Fix it this way
- First edit the config maps for argocd
```
kubectl edit configmaps -n argocd argocd-cmd-params-cm
```
- Next add the line to the bottom of the file
```
data:
  server.insecure: "true"
```
It should look like this afterwards
```
apiVersion: v1
data:
  server.insecure: "true"
kind: ConfigMap
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"ConfigMap","metadata":{"annotations":{},"labels":{"app.kubernetes.io/name":"argocd-cmd-params-cm","app.kubernetes.io/part-of":"argocd>  creationTimestamp: "2024-09-22T13:11:57Z"
  labels:
    app.kubernetes.io/name: argocd-cmd-params-cm
    app.kubernetes.io/part-of: argocd
  name: argocd-cmd-params-cm
  namespace: argocd
  resourceVersion: "88925"
  uid: ffada842-69d4-461c-b268-a00f8d7f5bb0
```

---

## ArgoCD CLI and configuration

1. Install Argo CLI
```
sudo curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
sudo chmod +x /usr/local/bin/argocd
```
2. Get initial **admin** password for argo
```
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d
```
username is _admin_
