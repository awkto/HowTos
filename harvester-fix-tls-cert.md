## Fixing TLS SAN to use DNS name
_Currently this section isn't complete, you can skip this section_
1. Fix TLS SAN on harvester configmap (~broken, resets)

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

2. Verify TLS san by checking file on harvester server
```
cat /etc/rancher/rke2/config.yaml.d/90-harvester-server.yaml
```
_Manually updating this works but will reset on reboot_

3. Restart rke2
```
sudo systemctl restart rke2-server
```

4. Alternately, either
   - simply use the **IP address** in your kubeconfig, OR
   - use `--insecure-skip-tls-verify` in the kubeconfig
