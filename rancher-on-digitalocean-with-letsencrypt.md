# Rancher with LetsEncrypt with DigitalOcean DNS API
These instructions help you deploy Rancher on either k3s or an rke2 cluster, and avoid some pitfalls that I spent a lot of time troubleshooting.

## Pre-Requisites
1. Deploy a Linux VM on Digital Ocean (I use Ubuntu24)
```
doctl compute droplet create --size s-2vcpu-8gb-amd --region syd1 --image ubuntu-22-04-x64 --ssh-keys [YOUR-SSH-KEY-ID]
```
  _You might want to add a non-root user and allow sudo_

2. Install rke2 or k3s on the VM

   - **rke2 install**
```
curl -sfL https://get.rke2.io | sh -
systemctl enable rke2-server.service
systemctl start rke2-server.service
```

  - **k3s install**
```
curl -sfL https://get.k3s.io | sh -
```


3. Add SAN to TLS config on **rke2** `sudo nano /etc/rancher/rke2/config.yaml`
```
tls-san:
- rancher.demo.com   <---- add FQDN
- 192.168.152.206
```
  - Restart rke2 with `systemctl restart rke2-server`
  - Copy/update your kubeconfig from `/etc/rancher/rke2/rke2.yaml`
  - Disable `insecure-skip-tls-verify` option if you added it previously
  - Test with **kubectl get namespaces**

3b. Add SAN to TLS config on **k3s** `sudo nano /etc/rancher/k3s/config.yaml`
```
tls-san:
- rancher.demo.com   <---- add FQDN
- 192.168.152.206
```
  - Important : If the file doesn't exist, CREATE IT
  - Restart k3s with `systemctl restart k3s`
  - Copy/update your kubeconfig from `/etc/rancher/k3s/k3s.yaml`
  - Disable `insecure-skip-tls-verify` option if you added it previously
  - Test with **kubectl get namespaces**

4. Add digitalocean API token (replace or use the env var)
```
kubectl create namespace cert-manager
kubectl create secret generic digitalocean-api-token \
  --from-literal=token=$DOKEYK8S \
  --namespace cert-manager
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

6. Deploy **cluster-issuer.yaml** with dns01 challenge

```
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-digitalocean-clusterissuer
  namespace: cert-manager
spec:
  acme:
    email: CERTS_EMAIL     <---- UPDATE THIS
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: acme-private-key
    solvers:
    - dns01:
        digitalocean:
          tokenSecretRef:
            key: token
            name: digitalocean-api-token
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
  --set hostname=HOSTNAME.EXAMPLE.COM \
  --set ingress.tls.source=letsEncrypt \
  --set letsEncrypt.email=certs@jixi.ca \
  --set letsEncrypt.ingress.class=nginx \
  --set agentTLSMode=system-store

```
_Note we use ingress class nginx for rke2_

3b. Install Rancher on **k3s** with **agentTLSMode** set to `system-store`
```
 helm install rancher rancher-latest/rancher \
  --namespace cattle-system \
  --set hostname=HOSTNAME \
  --set ingress.tls.source=letsEncrypt \
  --set letsEncrypt.email=certs@jixi.ca \
  --set letsEncrypt.ingress.class=traefik \
  --set agentTLSMode=system-store

```
_Note we use ingress class traefik for k3s_

4. Allow a few minutes for the certificates to install

  _You can check with_
```
kubectl -n cattle-system get ingress
```
You may see 2 ingresses here while cert-manager is still trying to validate.
Once validated, the HTTP ingress will stop and you will then just see 1 ingress remain

4b. Manually install certificate
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
