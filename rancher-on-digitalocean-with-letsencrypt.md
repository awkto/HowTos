## Rancher with LetsEncrypt on DigitalOcean VM
These steps work by using traefik as the ingress instead of nginx (deviation from the official docs)

### Pre-Requisites
1. Deploy a Linux VM on Digital Ocean (I use Ubuntu24)
```
doctl compute droplet create --size s-2vcpu-8gb-amd --region syd1 --image ubuntu-22-04-x64 --ssh-keys [YOUR-SSH-KEY-ID]
```
_You might want to add a non-root user and allow sudo_

2. Install k3s on the VM
```
curl -sfL https://get.k3s.io | sh -
```
_This installs and runs a k3s cluster_
3. Fix up your kube config
```
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config 
```

### Install Cert Manager
1. Install cert manager
```
helm repo add jetstack https://charts.jetstack.io
helm repo update
kubectl create namespace cert-manager
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --version v1.5.4 \
  --set installCRDs=true
```
  _Note we're installing the CRDs via this helm install command, and not manually beforehand_
  
2. Create yaml file cluster-issuer.yaml
```
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
  namespace: cert-manager
spec:
  acme:
    email: certs@jixi.ca
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: traefik
```
  _Notice the class here is traefik and not nginx_
  
3. Install the cluster-issuer.yaml
```
kubectl apply -f cluster-issuer.yaml
```

### Install Rancher

1. Add the repos
```
helm repo add rancher-latest https://releases.rancher.com/server-charts/latest

```
2. Create the namespace
```
kubectl create namespace cattle-system
```

3. Install Rancher
```
helm install rancher rancher-latest/rancher \
  --namespace cattle-system \
  --set hostname=HOSTNAME.EXAMPLE.COM \
  --set ingress.tls.source=letsEncrypt \
  --set letsEncrypt.email=certs@jixi.ca \
  --set letsEncrypt.ingress.class=traefik
```
_Use your correct email and hostname. Also note again we use traefik_

4. Allow a few minutes for the certificates to install

  _You can check with_
```
kubectl -n cattle-system get ingress
```
You may see 2 ingresses here while cert-manager is still trying to validate.
Once validated, the HTTP ingress will stop and you will then just see 1 ingress remain

5. Log in to Rancher via web browser to confirm proper certificates applied
