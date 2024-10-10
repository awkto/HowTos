# Rancher with LetsEncrypt with Azure DNS API
These instructions help you deploy Rancher on either k3s or an rke2 cluster, and avoid some pitfalls that I spent a lot of time troubleshooting.

## Pre-Requisites
1. Deploy a Linux VM somewhere (I use Ubuntu24 on proxmox)
   
  _You might want to add a non-root user and allow sudo_

3. Install rke2 or k3s on the VM
  - rke2 install
```
curl -sfL https://get.rke2.io | sudo sh -
sudo systemctl enable rke2-server.service
sudo systemctl start rke2-server.service
```
  - k3s install
```
curl -sfL https://get.k3s.io | sh -
```


3. Add SAN to TLS config on **rke2**

`sudo nano /etc/rancher/rke2/config.yaml`
```
tls-san:
- rancher.demo.com   <---- add FQDN
- 192.168.152.206   <---- IP optional, use only if you connect via IP
```
  - Restart rke2 with `systemctl restart rke2-server`
  - Copy/update your kubeconfig from `/etc/rancher/rke2/rke2.yaml`
  - Disable `insecure-skip-tls-verify` option if you added it previously
  - Test with **kubectl get namespaces**

3b. Add SAN to TLS config on **k3s** `sudo nano /etc/rancher/k3s/config.yaml`
```
tls-san:
- rancher.demo.com   <---- add FQDN
- 192.168.152.206   <---- IP optional, only needed if you plan on connecting via IP
```
  - Important : If the file doesn't exist, CREATE IT
  - Restart k3s with `systemctl restart k3s`
  - Copy/update your kubeconfig from `/etc/rancher/k3s/k3s.yaml`
  - Disable `insecure-skip-tls-verify` option if you added it previously
  - Test with **kubectl get namespaces**

4. Add Azure SPN API token 
```
kubectl create namespace cert-manager
kubectl create secret generic azure-letsencrypt-spn-secret \
  --namespace cert-manager \
  --from-literal=client-secret='<app-password>' 
```

5. Install cert manager
```
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --version v1.5.4 \
  --set installCRDs=true
```

6. Deploy **cluster-issuer.yaml** with dns01 challenge (azure)
```
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-azuredns
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: CERTS_EMAIL
    privateKeySecretRef:
      name: acme-private-key
    solvers:
    - dns01:
        azureDNS:
          clientID: "<appId>"
          clientSecretSecretRef:
            name: azure-letsencrypt-spn-secret
            key: client-secret
          subscriptionID: "<subscription-id>"
          tenantID: "<tenant-id>"
          resourceGroupName: "<your-resource-group>"
          hostedZoneName: "<your-dns-zone>"
          environment: AzurePublicCloud 
```

6b. Alternately deploy a local Issuer instead of ClusterIssuer (works more easily with Rancher helm)
```
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: letsencrypt-azuredns
  namespace: cattle-system
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: CERTS_EMAIL
    privateKeySecretRef:
      name: acme-private-key
    solvers:
    - dns01:
        azureDNS:
          clientSecretSecretRef:
            name: azure-letsencrypt-spn-secret
            key: client-secret
          clientID: "AZURE-SPN-APP-ID"
          subscriptionID: "SUBSCRIPTION-ID-FOR-ZONE"
          tenantID: "AZURE-SPN-TENANT-ID"
          resourceGroupName: "RESOURCE-GROUP-NAME"
          hostedZoneName: "DNS-ZONE-NAME"
          environment: AzurePublicCloud 
```

## Install Rancher

1. Add the repos
```
helm repo add rancher-latest https://releases.rancher.com/server-charts/latest
helm repo update
```
2. Create the namespace
```
kubectl create namespace cattle-system
```

3. Install Rancher on **rke2** with **agentTLSMode** set to `system-store`
```
helm install rancher rancher-latest/rancher \
  --namespace cattle-system \
  --set hostname=HOSTNAME \
  --set ingress.tls.source=letsEncrypt \
  --set letsEncrypt.email=CERTS_EMAIL \
  --set letsEncrypt.ingress.class=nginx \
  --set agentTLSMode=system-store \
  --set ingress.extraAnnotations."cert-manager\.io/cluster-issuer"=letsencrypt-azuredns \
  --set ingress.extraAnnotations."cert-manager\.io/acme-challenge-type"=dns01

```
_We use ingress class nginx for rke2_
_Also agentTLSMode=system-store allows connection to Harvester later_

3b. Install Rancher on **k3s** with **agentTLSMode** set to `system-store`
```
helm install rancher rancher-latest/rancher \
  --namespace cattle-system \
  --set hostname=HOSTNAME \
  --set ingress.tls.source=letsEncrypt \
  --set letsEncrypt.email=CERTS_EMAIL \
  --set letsEncrypt.ingress.class=traefik \
  --set agentTLSMode=system-store \
  --set ingress.extraAnnotations."cert-manager\.io/cluster-issuer"=letsencrypt-azuredns \
  --set ingress.extraAnnotations."cert-manager\.io/acme-challenge-type"=dns01
```
_We use ingress class traefik for k3s._
_Also agentTLSMode=system-store allows connection to Harvester later_

3c. Install Rancher with Issuer instead of Cluster Issuer (on **k3s**)
```
helm install rancher rancher-latest/rancher \
  --namespace cattle-system \
  --set hostname=HOSTNAME \
  --set ingress.tls.source=letsEncrypt \
  --set letsEncrypt.email=CERTS_EMAIL \
  --set letsEncrypt.ingress.class=traefik \
  --set agentTLSMode=system-store \
  --set ingress.extraAnnotations."cert-manager\.io/issuer"=letsencrypt-azuredns \
  --set ingress.extraAnnotations."cert-manager\.io/issuer-kind"=Issuer \
  --set ingress.extraAnnotations."cert-manager\.io/acme-challenge-type"=dns01
```

4. Remove the Issuer Annotations if you're using a ClusterIssuer
- Edit with `kubectl edit ingress -n cattle-system rancher`
- Remove these 2 annotations
  ```
    --set ingress.extraAnnotations."cert-manager\.io/issuer"="" \
    --set ingress.extraAnnotations."cert-manager\.io/issuer-kind"=""
  ```
  
5. Allow a few minutes for the certificates to install

  _You can check with_
```
kubectl get certificates -A
kubectl logs -n cert-manager deploy/cert-manager -f
```

6. (Optional) Manually install certificate (if not created automatically)
```
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: rancher-letsencrypt-certificate
  namespace: cattle-system # Ensure it matches your app's namespace
spec:
  secretName: rancher-letsencrypt-secret
  duration: 2160h # 90 days
  renewBefore: 720h # 30 days in hours
  issuerRef:
    name: letsencrypt-digitalocean-clusterissuer
    kind: ClusterIssuer
  commonName: HOSTNAME
  dnsNames:
    - HOSTNAME
```

5. Log in to Rancher via web browser to confirm proper certificates applied

6. (Troubleshooting) Reset Admin Password
If for some reason the bootstrap command does not work and you can't perform the _initial_ login to rancher, run this command
```
kubectl -n cattle-system exec $(kubectl -n cattle-system get pods -l app=rancher | grep '1/1' | head -1 | awk '{ print $1 }') -- reset-password
```
Then log in with user **admin** and the password it gives you
