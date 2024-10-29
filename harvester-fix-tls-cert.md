## Fixing TLS SAN to use DNS name

Harvester comes with default tls-san that may not match your DNS records

#### To add a SAN to the auto-generated TLS certificates : 
1. SSH into Harvester as `ssh rancher@harvester-fqdn`
2. Switch to root with `sudo bash`
3. Edit the file **/etc/rancher/rke2/config.yaml.d/90-harvester-server.yaml**
4. Under 'tls-san' section add your DNS names. Example : 
```
cni: multus,canal
cluster-cidr: 10.52.0.0/16
service-cidr: 10.53.0.0/16
cluster-dns: 10.53.0.10
tls-san:
  - 192.168.152.205
  - harvester.example.com      <--- ADD FQDN HERE
kubelet-arg:
- "max-pods=200"
audit-policy-file: /etc/rancher/rke2/config.yaml.d/92-harvester-kube-audit-policy.yaml
```
5. You might have to delete the existing certs to force them to regenerate
```
    sudo rm -f /var/lib/rancher/rke2/server/tls/serving-kube-apiserver.crt
    sudo rm -f /var/lib/rancher/rke2/server/tls/serving-kube-apiserver.key
```


6. Restart rancher with `sudo systemctl restart rke2-server`
```
sudo systemctl restart rke2-server
```

#### Verify, Update Kubeconfig

1. Grab a copy of the new kubeconfig from **/etc/rancher/rke2/rke2.yaml**
   - This should be copied to your local system for kubectl
   - Previous copies are now invalid as the cert authority changed
   - You can also just update the _certificate-authority-data_ field
   - You can also comment out the _insecure-skip-tls-verify_ line now

2. Verify with
```
openssl s_client -connect <your-api-server-ip>:6443 -showcerts
```
3. Verify with kubeconfig as well
```kubectl get pods```
---



## Alternate Solution
1. Alternately, either
   - simply use the **IP address** in your kubeconfig, OR
   - use `--insecure-skip-tls-verify` in the kubeconfig

---

## Troubleshooting

1. Manually Fix TLS SAN on harvester configmap (~broken, resets)

First edit the config map

`kubectl edit configmap harvester-helpers -n harvester-system`

Next Find the VIP section under **tls-san** which looks like this
```
    tls-san:
      - $VIP
```
Insert your harvester DNS FQDN into that section, so it looks like this
```
    tls-san:
      - harvester.example.com
      - $VIP
```

