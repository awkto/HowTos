# Rancher on k3s with certmanager and azure SPN
This guide assumes Ubuntu OS with helm and kubectl already installed, DNS on Azure, and an SPN provisioned.


## Part 1 - K3s Setup
1. Install k3s
```
curl -sfL https://get.k3s.io | sh -
```

2. Add tls subject alt name
Edit `/etc/rancher/k3s/config.yaml` and add these lines
```
tls-san:
- "k3s.domain.au"
- "10.31.1.5"
```

3. Restart k3s
```
sudo systemctl restart k3s
```

4. Copy out kube conf from k3s (and update the hostname)
```
cat /etc/rancher/k3s/k3s.yaml
```

5. Paste it in your local system and point your $KUBECONFIG var to the file
```
export KUBECONFIG=/home/user/k3s.yaml
```

## Part 2 - Rancher Setup with Cluster Issuer

1. Add helm repos for rancher and cert manager
```
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable
helm repo add rancher-latest https://releases.rancher.com/server-charts/latest
helm repo add jetstack https://charts.jetstack.io
helm repo update
```

2. Create namespace for rancher and cert manager
```
kubectl create namespace cattle-system
kubectl create namespace cert-manager
```

3. Add Azure SPN client Secret
```
kubectl create secret generic azure-letsencrypt-spn-secret \
  --namespace cert-manager \
  --from-literal=client-secret='your-client-secret' 
```

4. Install the ClusterIssuer (edit file clusterissuer.yaml and then kubectl apply -f):

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-azuredns
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: user@gmail.com
    privateKeySecretRef:
      name: acme-private-key
    solvers:
    - dns01:
        azureDNS:
          clientSecretSecretRef:
            name: azure-letsencrypt-spn-secret
            key: client-secret
          clientID: "your-client-id"
          subscriptionID: "your-subscription-id"
          tenantID: "your-tenant-id"
          resourceGroupName: "your-resource-group"
          hostedZoneName: "example.com"
          environment: AzurePublicCloud 
```

5. Install rancher with helm
```
helm repo add rancher-latest https://releases.rancher.com/server-charts/latest
helm repo update
kubectl create namespace cattle-system
helm install rancher rancher-latest/rancher \
  --namespace cattle-system \
  --set hostname=rancher.example.com \
  --set ingress.tls.source=letsEncrypt \
  --set letsEncrypt.email=user@gmail.com \
  --set letsEncrypt.ingress.class=traefik \
  --set agentTLSMode=system-store \
  --set ingress.extraAnnotations."cert-manager\.io/cluster-issuer"=letsencrypt-azuredns \
  --set ingress.extraAnnotations."cert-manager\.io/acme-challenge-type"=dns01 
```

6. Edit the ingress:

```bash
kubectl edit ingress -n cattle-system rancher
```

7. Delete these two annotations:
```bash
--set ingress.extraAnnotations."cert-manager\.io/issuer"="" \
--set ingress.extraAnnotations."cert-manager\.io/issuer-kind"=""
```

8. Check the certificates and logs :
```bash
kubectl get certificates -A
kubectl logs -n cert-manager deploy/cert-manager -f
```

9. (Optional) QOL Tweaks
- Set default namespace
```
kubectl config set-context --current --namespace=cattle-system
```
- Add this line to .bashrc to set default kube editor
```
export KUBE_EDITOR=/usr/bin/nano
```


## Part 2 Alternate - Rancher Setup with Local Issuer

1. Add helm repos for rancher and cert manager
```
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable
helm repo add rancher-latest https://releases.rancher.com/server-charts/latest
helm repo add jetstack https://charts.jetstack.io
helm repo update
```

2. Create namespace for rancher and cert manager
```
kubectl create namespace cattle-system
kubectl create namespace cert-manager
```

3. Add Azure SPN Client Secret (for local issuer)
```
kubectl create namespace cattle-system
kubectl create secret generic azure-letsencrypt-spn-secret \
  --namespace cattle-system \
  --from-literal=client-secret='your-client-secret' 
```

4. Install the local Issuer (edit file issuer.yaml and then kubectl apply -f):

```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: letsencrypt-azuredns
  namespace: cattle-system
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: user@gmail.com
    privateKeySecretRef:
      name: acme-private-key
    solvers:
    - dns01:
        azureDNS:
          clientSecretSecretRef:
            name: azure-letsencrypt-spn-secret
            key: client-secret
          clientID: "your-client-id"
          subscriptionID: "your-subscription-id"
          tenantID: "your-tenant-id"
          resourceGroupName: "your-resource-group"
          hostedZoneName: "example.com"
          environment: AzurePublicCloud 
```

5. Install rancher with helm (with local issuer)
```
helm install rancher rancher-latest/rancher \
  --namespace cattle-system \
  --set hostname=rancher.example.com \
  --set ingress.tls.source=letsEncrypt \
  --set letsEncrypt.email=user@gmail.com \
  --set letsEncrypt.ingress.class=traefik \
  --set agentTLSMode=system-store \
  --set ingress.extraAnnotations."cert-manager\.io/issuer"=letsencrypt-azuredns \
  --set ingress.extraAnnotations."cert-manager\.io/issuer-kind"=Issuer \
  --set ingress.extraAnnotations."cert-manager\.io/acme-challenge-type"=dns01
```

6. Check the certificates and logs :
```bash
kubectl get certificates -A
kubectl logs -n cert-manager deploy/cert-manager -f
```
