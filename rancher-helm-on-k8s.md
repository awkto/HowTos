# Rancher with Helm chart
This assumes Ubuntu OS

1. Install **kubectl** binary ([source](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/))
```
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

```
2. Install **helm** binary ([source](https://helm.sh/docs/intro/install/))
```
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```
3. Place kubeconf to ~/.kube/config or repoint env var $KUBECONFIG
4. Add Rancher helm repos stable and latest
```
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable
helm repo add rancher-latest https://releases.rancher.com/server-charts/latest
```

5. Install Rancher helm chart ([source](https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/install-upgrade-on-a-kubernetes-cluster))
```
helm install rancher rancher-latest/rancher \
  --namespace cattle-system \
  --set hostname=rancher.my.org \
  --set bootstrapPassword=admin \
  --set ingress.tls.source=secret
```

6. Add certs
```
kubectl -n cattle-system create secret tls tls-rancher-ingress \
  --cert=fullchain.pem \
  --key=privkey.pem
```
