# GitLab Workspaces Setup

## Overview
1. Set up a VM and deploy RKE2 cluster on it
   ```
   curl -sfL https://get.rke2.io | sh -
   systemctl enable rke2-server.service
   systemctl start rke2-server.service
   ```
2. Fix TLS Certs
   Run `sudo nano /etc/rancher/rke2/config.yaml`

   Enter and save
   ```
   tls-san:
   - rancher.demo.com
   - 192.168.152.206
   ```
   Restart rke2 server
   ```
   systemctl restart rke2-server.service
   ```
   Grab kubeconfig
   ```
   cat /etc/rancher/rke2/rke2.yaml
   ```
   Save locally, update FQDN, and point **KUBECONFIG** to it
   ```
   export KUBECONFIG=/home/user/kubeconfig.yaml
   ```

3. Add DNS records and wildcard DNS records for test and workspaces
  - k8s.example.com -> [Public IP]
  - *.k8s.example.com -> [Public IP]
  - workspaces.example.com -> [Public IP]
  - *.workspaces.example.com -> [Public IP]
4. Install cert manager via helm
   Add and update helm repo
   ```
   helm repo add jetstack https://charts.jetstack.io
   helm repo update
   ```
   Install cert manager
   ```
   helm install cert-manager jetstack/cert-manager \
     --namespace cert-manager \
     --version v1.5.4 \
     --set installCRDs=true
   ```
   
5. Create ClusterIssuer with Azure SPN secret
   Add Azure SPN client secret
   ```
   kubectl create secret generic azure-letsencrypt-spn-secret \
     --namespace cert-manager \
     --from-literal=client-secret='iwwww~xxxxxxxxxxxxffffffffffj-yyyyfggggD' 
   ```
   Create **clusterissuer.yaml**
   ```
   apiVersion: cert-manager.io/v1
   kind: ClusterIssuer
   metadata:
     name: letsencrypt-azuredns
   spec:
     acme:
       server: https://acme-v02.api.letsencrypt.org/directory
       email: user@example.com
       privateKeySecretRef:
         name: acme-private-key
       solvers:
       - dns01:
	         azureDNS:
             clientSecretSecretRef:
               name: azure-letsencrypt-spn-secret
               key: client-secret
             clientID: "3ccccccb-dddd-4111-aaad-777dddfffff4"
             subscriptionID: "7ccccccc-bbbb-dddd-8ccc-a000fff11117"
             tenantID: "fecccccc-ffff-4222-bccc-9777ggggdddd"
             resourceGroupName: "my-resource-group1"
             hostedZoneName: "example.com"
             environment: AzurePublicCloud
   ```
