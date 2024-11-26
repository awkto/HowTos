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
4. Expose it publicly via a public IP
3. Add DNS records and wildcard DNS records for test and workspaces
  - k8s.example.com -> [Public IP]
  - *.k8s.example.com -> [Public IP]
  - workspaces.example.com -> [Public IP]
  - *.workspaces.example.com -> [Public IP]
4. Deploy cert manager and
5. create ClusterIssuer
