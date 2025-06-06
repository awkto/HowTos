# GitLab Workspaces Setup

**Overview**
- Create VM with k8s cluster (rke2, certmanager, clusterissuer, and dns)
- Deploy Gitlab KAS onto k8s cluster
- Add Workspace configuration (proxy, enable for group, agent config)

## DNS Setup
Add DNS records and wildcard DNS records for test and workspaces
    
    k8s.example.com -> [Public IP]
    *.k8s.example.com -> [Public IP]
    workspaces.example.com -> [Public IP]
    *.workspaces.example.com -> [Public IP]
    

## Kubernetes Cluster Setup
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
    - k8s.example.com
    - 175.255.134.206
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

3. Install cert manager via helm
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
   
4. Create ClusterIssuer with Azure SPN secret
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
    Deploy with `kubectl apply -f clusterissuer.yaml`

## Test Application (optional)

Validate ClusterIssuer is working with Test App

1. Create and apply **test-namespace.yaml**
    ```
    # test-namespace.yaml
    apiVersion: v1
    kind: Namespace
    metadata:
      name: test
    ```
2. Create and apply **test-app.yaml**
    ```
    # nginx-deployment.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: nginx
      namespace: test
      labels:
        app: nginx
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: nginx
      template:
        metadata:
          labels:
            app: nginx
        spec:
          containers:
          - name: nginx
            image: nginx:latest
            ports:
            - containerPort: 80
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: nginx
      namespace: test
    spec:
      selector:
        app: nginx
      ports:
      - protocol: TCP
        port: 80
        targetPort: 80
      type: ClusterIP
    ```
3. Create and apply **test-ingress.yaml**
    ```
    # nginx-ingress.yaml
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: nginx-ingress
      namespace: test
      annotations:
        cert-manager.io/cluster-issuer: "letsencrypt-azuredns"
    spec:
      rules:
      - host: test.rke2.tux42.au # Replace with your domain
        http:
          paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: nginx
                port:
                  number: 80
      tls:
      - hosts:
        - test.k8s.example.com
        secretName: nginx-tls
    ```
   
# Workspace Configuration

## GitLab Oauth - Create a new application for a group

1. Go to the desired group.
2. On the left sidebar, select **Settings** > **Applications**
3. Enter a description **Name** 
4. Set the  **Redirect URI** to `https://${GITLAB_WORKSPACES_PROXY_DOMAIN}/auth/callback`
5. Set the scopes to `api`, `read_user`, `openid`, and `profile`.
7. Select **Save application**. GitLab provides:
    - The OAuth 2 Client ID in the **Application ID** field.
    - The OAuth 2 Client Secret, accessible by selecting **Copy** in the **Secret** field.

5. Export your `GITLAB_URL`, `CLIENT_ID`, `CLIENT_SECRET`, `REDIRECT_URI`, and `SIGNING_KEY`:
    ```
    export GITLAB_URL="https://gitlab.com"
    export CLIENT_ID="your_application_id"
    export CLIENT_SECRET="your_application_secret"
    export REDIRECT_URI="https://${GITLAB_WORKSPACES_PROXY_DOMAIN}/auth/callback"
    export SIGNING_KEY="make_up_a_random_key_consisting_of_letters_numbers_and_special_chars"
    ```


## Generate an SSH host key
To generate an RSA key, run this command:
```
ssh-keygen -f ssh-host-key -N '' -t rsa
export SSH_HOST_KEY=$(pwd)/ssh-host-key
```

## Create Kubernetes secrets
Create the namespace for **gitlab-workspaces**
```
kubectl create namespace gitlab-workspaces
```
Create the secret
```
kubectl create secret generic gitlab-workspaces-proxy-config \
  --namespace="gitlab-workspaces" \
  --from-literal="auth.client_id=${CLIENT_ID}" \
  --from-literal="auth.client_secret=${CLIENT_SECRET}" \
  --from-literal="auth.host=${GITLAB_URL}" \
  --from-literal="auth.redirect_uri=${REDIRECT_URI}" \
  --from-literal="auth.signing_key=${SIGNING_KEY}" \
  --from-literal="ssh.host_key=$(cat ${SSH_HOST_KEY})"
```

## Install the **gitlab-workspaces-proxy** via helm

1. Add the helm repository:
```
helm repo add gitlab-workspaces-proxy \
  https://gitlab.com/api/v4/projects/gitlab-org%2fworkspaces%2fgitlab-workspaces-proxy/packages/helm/devel
helm repo update
```

2. Create env vars
```
export GITLAB_WORKSPACES_WILDCARD_DOMAIN="workspaces.example.com"
export GITLAB_WORKSPACES_PROXY_DOMAIN="workspaces.example.com"
```

3. Install the helm
```
helm upgrade --install gitlab-workspaces-proxy \
  gitlab-workspaces-proxy/gitlab-workspaces-proxy \
  --version=0.1.16 \
  --namespace="gitlab-workspaces" \
  --set="ingress.enabled=true" \
  --set="ingress.hosts[0].host=${GITLAB_WORKSPACES_PROXY_DOMAIN}" \
  --set="ingress.hosts[0].paths[0].path=/" \
  --set="ingress.hosts[0].paths[0].pathType=ImplementationSpecific" \
  --set="ingress.hosts[1].host=${GITLAB_WORKSPACES_WILDCARD_DOMAIN}" \
  --set="ingress.hosts[1].paths[0].path=/" \
  --set="ingress.hosts[1].paths[0].pathType=ImplementationSpecific" \
  --set="ingress.tls[0].hosts[0]=${GITLAB_WORKSPACES_PROXY_DOMAIN}" \
  --set="ingress.tls[0].secretName=gitlab-workspace-proxy-tls" \
  --set="ingress.tls[1].hosts[0]=${GITLAB_WORKSPACES_WILDCARD_DOMAIN}" \
  --set="ingress.tls[1].secretName=gitlab-workspace-proxy-wildcard-tls" \
  --set="ingress.className=nginx"
```
_Todo: See if there is a way to add the clusterissuer anotation during this helm command_

4. Edit the ingress to add the annotation
Edit the ingress
```
kubectl edit ingress -n gitlab-workspaces
```
Add anotation
```
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-azuredns"
```

## Verify Kubernetes resources
Verify the Ingress class, hosts, address, and port for the gitlab-workspaces namespace:
```
kubectl -n gitlab-workspaces get ingress
```

Verify the pods are running:
```
kubectl -n gitlab-workspaces get pods
```

