## How to add TLS SAN to RKE2 Server
This is needed to be able to use DNS FQDN in your kubeconfig without a TLS warning or error.
1. Manually create this file `/etc/rancher/rke2/config.yaml`
2. Add this in the contents
   ```
   write-kubeconfig-mode: "0644"
   tls-san:
     - "foo.local"
   ```
3. Replace foo.local with your FQDN
4. Restart rke2 server with `systemctl restart rke2-server`
