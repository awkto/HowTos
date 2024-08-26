# Rancher on k3s with Helm chart
This assumes Ubuntu OS with helm and kubectl already installed

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

5. Deploy rancher (update the DNS name)
```
helm install rancher rancher-latest/rancher \
  --namespace cattle-system \
  --set hostname=rancher.my.org \
  --set bootstrapPassword=admin \
  --set ingress.tls.source=secret
  [--set privateCA=true]
```

6. Add Secret
```
kubectl -n cattle-system create secret tls tls-rancher-ingress \
  --cert=tls.crt \
  --key=tls.key
```
_Make sure the file names are tls.crt and tls.key_
