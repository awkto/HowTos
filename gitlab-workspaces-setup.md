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
## GitLab OAuth - Create a user-owned application
To create a new application for your user:
1. On the left sidebar, select your avatar.
2. Select **Edit profile**.
3. On the left sidebar, select **Applications**.
4. Select **Add new application**.
5. Enter a **Name** and **Redirect URI**.
6. Select OAuth 2 **Scopes** as defined in Authorized Applications.
7. In the **Redirect URI**, enter the URL where users are sent after they authorize with GitLab.
8. Select **Save application**. GitLab provides:
    - The OAuth 2 Client ID in the **Application ID** field.
    - The OAuth 2 Client Secret, accessible by selecting **Copy** in the **Secret** field.
    - The **Renew secret** function in GitLab 15.9 and later. Use this function to generate and copy a new secret for this application. Renewing a secret prevents the existing application from functioning until the credentials are updated.


## To register an app on your GitLab instance:
1. Configure GitLab as an **OAuth 2.0 identity provider**.
2. Set the redirect URI to `https://${GITLAB_WORKSPACES_PROXY_DOMAIN}/auth/callback`.
3. Select the **Trusted** checkbox.
4. Set the scopes to `api`, `read_user`, `openid`, and `profile`.
5. Export your `GITLAB_URL`, `CLIENT_ID`, `CLIENT_SECRET`, `REDIRECT_URI`, and `SIGNING_KEY`:
    ```
    export GITLAB_URL="https://gitlab.com"
    export CLIENT_ID="your_application_id"
    export CLIENT_SECRET="your_application_secret"
    export REDIRECT_URI="https://${GITLAB_WORKSPACES_PROXY_DOMAIN}/auth/callback"
    export SIGNING_KEY="make_up_a_random_key_consisting_of_letters_numbers_and_special_chars"
    ```
Store the client ID and generated secret in a safe place (for example, 1Password).



