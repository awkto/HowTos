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

## Part 2 - Rancher Setup

1. Add helm repos for rancher
```
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable
helm repo add rancher-latest https://releases.rancher.com/server-charts/latest
```

2. Create namespace for rancher
```
kubectl create namespace cattle-system
```

3. Add Secret
```
kubectl -n cattle-system create secret tls tls-rancher-ingress \
  --cert=tls.crt \
  --key=tls.key
```
_Make sure the file names are tls.crt and tls.key_


4. Deploy rancher (update the DNS name)
```
helm install rancher rancher-latest/rancher \
  --namespace cattle-system \
  --set hostname=rancher.my.org \
  --set bootstrapPassword=admin \
  --set ingress.tls.source=secret
```

4b. Using lets encrypt and traefik ingress controller
```yaml
 helm install rancher rancher-latest/rancher \
  --namespace cattle-system \
  --set hostname=HOSTNAME \
  --set ingress.tls.source=letsEncrypt \
  --set letsEncrypt.email=certs@jixi.ca \
  --set letsEncrypt.ingress.class=traefik \
  --set agentTLSMode=system-store
```

5. (Optional) QOL Tweaks
- Set default namespace
```
kubectl config set-context --current --namespace=cattle-system
```
- Add this line to .bashrc to set default kube editor
```
export KUBE_EDITOR=/usr/bin/nano
```
