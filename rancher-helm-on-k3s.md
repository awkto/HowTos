# Rancher on k3s with Helm chart
This assumes Ubuntu OS with helm and kubectl already installed

**Prerequisite** : Get certs manually
```
certbot certonly --manual --preferred-challenges dns --email [EMAIL] --domains [FQDN]
```
**Important**
Certbot generates multiple files.
- Don't use fullchain.pem
- Rename cert.pem to tls.crt
- Rename privkey.pem to tls.key


1. Install k3s
```
curl -sfL https://get.k3s.io | sh -
```

2. Grab kube conf from k3s
```
mkdir ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
chown user:user ~/.kube/config
chmod 600 ~/.kube/config
```

3. Add helm repos for rancher
```
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable
helm repo add rancher-latest https://releases.rancher.com/server-charts/latest
```

4. Create namespace for rancher
```
kubectl create namespace cattle-system
```

5. Add Secret
```
kubectl -n cattle-system create secret tls tls-rancher-ingress \
  --cert=tls.crt \
  --key=tls.key
```
_Make sure the file names are tls.crt and tls.key_


6. Deploy rancher (update the DNS name)
```
helm install rancher rancher-latest/rancher \
  --namespace cattle-system \
  --set hostname=rancher.my.org \
  --set bootstrapPassword=admin \
  --set ingress.tls.source=secret
```

6b. Using lets encrypt and traefik ingress controller
```yaml
 helm install rancher rancher-latest/rancher \
  --namespace cattle-system \
  --set hostname=HOSTNAME \
  --set ingress.tls.source=letsEncrypt \
  --set letsEncrypt.email=certs@jixi.ca \
  --set letsEncrypt.ingress.class=traefik \
  --set agentTLSMode=system-store
```

7. (Optional) QOL Tweaks
- Set default namespace
```
kubectl config set-context --current --namespace=cattle-system
```
- Add this line to .bashrc to set default kube editor
```
export KUBE_EDITOR=/usr/bin/nano
```
