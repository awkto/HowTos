kub   # LetsEncrypt SSL certs on Harvester

#### Notes
- Harvester gets installed as a cluster on namespace cattle-system
- Runs on an RKE2 cluster, with NGINX as the ingress
- We use cert-manager and add azure SPN secret for automatic TXT record creation
- We will use Azure for DNS

## Install Harvester and TLS workaround
1. Install Harvester with ISO boot
   - Set a static IP or DHCP reservation
   - Create DNS record to match the name used during install
   - Store/save cluster passwords etc

2. In the kubeconfig, simply use the **IP address** for connection, OR use `--insecure-skip-tls-verify` in the kubeconfig

## Certifying Harvester Ingress
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
2. Add your Azure SPN secret
```
kubectl create secret generic azure-letsencrypt-spn-secret \
  --namespace cert-manager \
  --from-literal=client-secret='CLIENT_SECRET_HERE' 
```

3. Create and deploy a ClusterIssuer `clusterissuer.yaml`
```
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-azuredns
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: altan.changezi@adfinis.com
    privateKeySecretRef:
      name: acme-private-key
    solvers:
    - dns01:
        azureDNS:
          clientSecretSecretRef:
            name: azure-letsencrypt-spn-secret
            key: client-secret
          clientID: "AZURE-SPN-APP-ID"
          subscriptionID: "AZURE-ZONE-SUBSCRIPTION-ID"
          tenantID: "AZURE-SPN-TENANT-ID"
          resourceGroupName: "RESOURCE-GROUP-NAME"
          hostedZoneName: "ZONE-NAME"
          environment: AzurePublicCloud
```

4. Edit your rancher ingress with 
```
kubectl edit ingress -n cattle-system rancher-expose
```

Add these two lines in the annotation section
```
      cert-manager.io/acme-challenge-type: dns01
      cert-manager.io/cluster-issuer: letsencrypt-azuredns
```

Add a host line above 'http' so it looks like this
```
    rules:
    - host: HOSTNAME
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
       - HOSTNAME
       secretName: tls-rancher-ingress

```
5. Verify with
```
kubectl get certificates -A
kubectl logs -n cert-manager deploy/cert-manager -f
```

