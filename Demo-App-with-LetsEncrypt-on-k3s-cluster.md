# Demo App with LetsEncrypt on k3s cluster

We will use **cert-manager** here with the digitalocean dns plugin which validates domain ownership by automatically creating a DNS record on a digitalocean domain. An API key must be generated and added to the cluster

### Notes
- k3s comes with traefik as the default ingress instead of nginx
- nginx web app will be deployed
- ingress will be deployed for the app
- certificate yaml will be deployed

### Pre-Requisites
Install helm
```
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Instructions

1. Install cert manager with helm

First add and update helm repo
```
helm repo add jetstack https://charts.jetstack.io
helm repo update
```

Next install with
```
kubectl create namespace cert-manager
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --version v1.14.1 \
  --set installCRDs=true
```

Lastly verify with
```
kubectl get pods --namespace cert-manager
```
1b. (Alternate) Install without helm
```
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.15.3/cert-manager.crds.yaml
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.15.3/cert-manager.yaml
kubectl get pods --namespace cert-manager
```

2. Add your DigitalOcean API token first for auto DNS verification
```
kubectl create secret generic digitalocean-dns-token \
  --from-literal=access-token=YOUR_DIGITALOCEAN_API_TOKEN \
  --namespace cert-manager
```

3. Deploy this nginx web app `nginx-hello-deployment.yaml`
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-hello
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx-hello
  template:
    metadata:
      labels:
        app: nginx-hello
    spec:
      containers:
      - name: nginx-hello
        image: nginxdemos/hello:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-hello
spec:
  selector:
    app: nginx-hello
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP
```

4. Deploy the ingress `nginx-hello-ingress.yaml` for the same app
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-hello
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-digitalocean
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
spec:
  tls:
  - hosts:
    - HOSTNAME     #change this
    secretName: hello-world-tls-secret
  rules:
  - host: HOSTNAME    #change this
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-hello
            port:
              number: 80
```

5. Finally, `deploy certificate.yaml` to request the cert
```
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: hello-world-tls
  namespace: default # Ensure it matches your app's namespace
spec:
  secretName: hello-world-tls-secret
  duration: 2160h # 90 days
  renewBefore: 720h # 30 days in hours
  issuerRef:
    name: letsencrypt-digitalocean
    kind: ClusterIssuer
  commonName: HOSTNAME   #change this
  dnsNames:
    - HOSTNAME   #change this
```
