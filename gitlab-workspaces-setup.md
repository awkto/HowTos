# GitLab Workspaces Setup

**Overview**
- Create VM with k8s cluster (rke2, certmanager, clusterissuer, and dns)
- Deploy Gitlab KAS onto k8s cluster
- Add Workspace configuration (proxy, enable for group, agent config)

## DNS Setup
Add DNS records and wildcard DNS records for test and workspaces
  	- k8s.example.com -> [Public IP]
  	- *.k8s.example.com -> [Public IP]
  	- workspaces.example.com -> [Public IP]
  	- *.workspaces.example.com -> [Public IP]

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
    
