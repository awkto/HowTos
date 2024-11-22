# K3S SAN update for Cluster TLS certifcate

K3s clusters get deployed with default certs that don't include the hostname as a subject-alternative-name, making them invalid when connecting via DNS. To fix this you can regenerate the cluster TLS certs by adding an option and then deleting the old certs. 

You might have to delete the kubeconfig as well to regenerate it.

1. Create this file `/etc/rancher/k3s/config.yaml` and add these lines
   ```yaml
   tls-san:
   - "k3s.domain.au"
   - "10.31.1.5"
   ```
   _Replace the fqdn and ip with your cluster specific details_

2. (Optional) Delete the cluster certificate files if they don't regenerate
   ```bash
   sudo rm /var/lib/rancher/k3s/server/tls/serving-kube-apiserver.crt
   sudo rm /var/lib/rancher/k3s/server/tls/serving-kube-apiserver.key
   ```

3. Restart k3s service
   ```bash
   sudo systemctl restart k3s
   ```

4. Test and verify the SAN was added with **openssl**
   ```bash
   openssl x509 -in /var/lib/rancher/k3s/server/tls/serving-kube-apiserver.crt -text -nooutq|grep -i alternative -A1
   ```

5. Update your local kubeconfig by copying out the k3s cluster kubeconfig at :
   `/etc/rancher/k3s/k3s.yaml`
   
