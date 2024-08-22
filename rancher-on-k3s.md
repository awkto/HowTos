# Rancher on k3s with Helm chart
This assumes Ubuntu OS with helm and kubectl already installed

1. Install microk8s
```
sudo snap install microk8s --classic
```

2. Grab kube conf from microk8s
```
mkdir ~/.kube
microk8s config > ~/.kube/config
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
kubectl create secret generic tls-ca --from-file=/opt/rancherkeys/fullchain.pem -n cattle-system
```
