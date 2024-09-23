## Automated SSL certs on Harvester
Notes
- We will use digitalocean for DNS
- We use cert-manager and add digitalocean token for automatic TXT record creation


#### Notes
- Harvester gets installed as a cluster on namespace cattle-system
- Runs on an RKE2 cluster, with NGINX as the ingress
- Create environment variable $CERTS_EMAIL for the email address to use for certs
- Create environment variable $DOKEYK8S for the digitalocean API token for letsencrypt

  
1. Add your DigitalOcean API token first for auto DNS verification
```
kubectl create namespace cert-manager
kubectl create secret generic digitalocean-api-token \
  --from-literal=access-token=$DOKEYK8S \
  --namespace cert-manager
```

2. Install cert manager with helm

First add and update helm repo
```
helm repo add jetstack https://charts.jetstack.io
helm repo update
```

Next install with
```
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --version v1.14.1 \
  --set installCRDs=true
```

Lastly verify with
```
kubectl get pods --namespace cert-manager
```
2b. (Alternate) Install without helm
```
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.15.3/cert-manager.crds.yaml
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.15.3/cert-manager.yaml
kubectl get pods --namespace cert-manager
```

3. Create and deploy a ClusterIssuer `clusterissuer.yaml`
```
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"cert-manager.io/v1","kind":"ClusterIssuer","metadata":{"annotations":{},"name":"letsencrypt-digitalocean"},"spec":{"acme":{"email":"certs@jixi.ca","privateKeySecretRef":{"name":"letsencrypt-digitalocean-key"},"server":"https://acme-v02.api.letsencrypt.org/directory","solvers":[{"dns01":{"digitalocean":{"tokenSecretRef":{"key":"token","name":"digitalocean-secret"}}}}]}}}
  creationTimestamp: "2024-09-20T22:41:13Z"
  generation: 1
  name: letsencrypt-digitalocean-clusterissuer
  resourceVersion: "54873"
  uid: 5bebc608-2b51-453b-8c96-6de7ce87c6af
spec:
  acme:
    email: CERTS_EMAIL  #change this
    privateKeySecretRef:
      name: acme-private-key
    server: https://acme-v02.api.letsencrypt.org/directory
    solvers:
    - dns01:
        digitalocean:
          tokenSecretRef:
            key: token
            name: digitalocean-api-token  #THIS SHOULD MATCH YOUR TOKEN SECRET
```

4. Edit your rancher ingress with `kubectl edit ingress -n cattle-system`
Change it to look like this. Mostly just adding that TLS section
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"networking.k8s.io/v1","kind":"Ingress","metadata":{"annotations":{},"creationTimestamp":"2024-09-20T21:32:15Z","generation":2,"name":"rancher-expose","namespace":"cattle-system","resourceVersion":"216541","uid":"6ed3e3aa-2436-478b-944b-ec239829a2e2"},"spec":{"ingressClassName":"nginx","rules":[{"host":"harv-test.dnsif.ca"},{"http":{"paths":[{"backend":{"service":{"name":"rancher","port":{"number":80}}},"path":"/","pathType":"Prefix"}]}}],"tls":[{"hosts":["harv-test.dnsif.ca","cluster.harv-test.dnsif.ca"],"secretName":"harv-certbot-tls-secret"}]},"status":{"loadBalancer":{"ingress":[{"ip":"192.168.152.191"}]}}}
  creationTimestamp: "2024-09-20T21:32:15Z"
  generation: 3
  name: rancher-expose
  namespace: cattle-system
  resourceVersion: "221626"
  uid: 6ed3e3aa-2436-478b-944b-ec239829a2e2
spec:
  ingressClassName: nginx
  rules:
  - host: HOSTNAME   #change this
    http:
      paths:
      - backend:
          service:
            name: rancher
            port:
              number: 80
        path: /
        pathType: Prefix
  tls:
  - hosts:
    - HOSTNAME   #change this
    - ALT-HOSTNAME   #change this
    secretName: harv-certbot-tls-secret
status:
  loadBalancer:
    ingress:
    - ip: 192.168.152.191
```



5. (Maybe) Deploy a certificate with `deploy certificate.yaml`
```
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: harv-certificate
  namespace: default # Ensure it matches your app's namespace
spec:
  secretName: harv-certbot-tls-secret
  duration: 2160h # 90 days
  renewBefore: 720h # 30 days in hours
  issuerRef:
    name: letsencrypt-digitalocean-clusterissuer
    kind: ClusterIssuer
  commonName: HOSTNAME   #change this
  dnsNames:
    - HOSTNAME   #change this
    - ALT-HOSTNAME   #change this
```
