# Harvester Setup TLS and Certs
This guide sets up SUSE Harvester on bare metal with a proper TLS certificate that includes the SAN, as well as ClusterIssuer via Cert Manager with DigitalOcean DNS for challenge.


## Fixing TLS Cert
1. SSH into Harvester as ssh rancher@harvester-fqdn
2. Switch to root with sudo bash
3. Edit the file /etc/rancher/rke2/config.yaml.d/90-harvester-server.yaml
4. Under 'tls-san' section add your DNS names. Example :
```
cni: multus,canal
cluster-cidr: 10.52.0.0/16
service-cidr: 10.53.0.0/16
cluster-dns: 10.53.0.10
tls-san:
  - 192.168.152.205
  - harvester.example.com      <--- ADD FQDN HERE
kubelet-arg:
- "max-pods=200"
audit-policy-file: /etc/rancher/rke2/config.yaml.d/92-harvester-kube-audit-policy.yaml
```
5. Restart the rke2 service
```
systemctl restart rke2-server
```
6. If that doesn't work, you might have to delete these files and restart the service again
```
sudo rm -f /var/lib/rancher/rke2/server/tls/serving-kube-apiserver.crt
sudo rm -f /var/lib/rancher/rke2/server/tls/serving-kube-apiserver.key
```
7. Grab a copy of kubeconfig from `/etc/rancher/rke2/rke2.yaml`
8. Fix permissions of the kubeconfig on your machine with `chmod 600 ./kubeconfig.yaml`

## Adding Cert Manager
1. Install cert manager

```
kubectl create namespace cert-manager
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --version v1.5.4 \
  --set installCRDs=true
```

[INCOMPLETE FROM THIS POINT IN. WORK IN PROGRESS]

2. Encrypt your DigitalOcean token
```
echo -n 'your-digitalocean-api-token' | base64
```
3. Save it in a secret with this file **dosecret.yaml**
```
apiVersion: v1
kind: Secret
metadata:
  name: digitalocean-dns-token
  namespace: cert-manager
data:
  access-token: BASE64_ENCODED_TOKEN
```
_Apply with `kubectl apply -f dosecret.yaml`_

4. Deploy this **clusterissuer.yaml**
```
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-dodns
spec:
  acme:
    email: certs@jixi.ca
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: letsencrypt-issuer-account-key
    solvers:
      - dns01:
          digitalocean:
            tokenSecretRef:
              name: digitalocean-dns-token
              key: access-token
```

5. Edit your Harvester ingress with

```
kubectl get ingress -n cattle-system rancher-expose -o yaml > ingress.original.yaml
cp ingress.original.yaml ingress.modified.yaml
nano ingress.modified.yaml
```

  

Add these two lines in the annotation section

```
    cert-manager.io/acme-challenge-type: dns01
    cert-manager.io/cluster-issuer: letsencrypt-azuredns
```

Add a host line above 'http' so it looks like this

```
    rules:
    - host: harvester.tux42.au
      http:
        paths:
        - backend:
            service:
              name: rancher
              port:
                number: 80
          path: /
          pathType: Prefix
```

And add a tls section right under that, nested in spec

```
  tls:
  - hosts:
    - harvester.tux42.au
    secretName: tls-rancher-ingress
```

5. Apply with

```bash
kubectl apply -f ingress.modified.yaml
```

  
6. Verify with

```
kubectl get certificates -A
kubectl logs -n cert-manager deploy/cert-manager -f
```
