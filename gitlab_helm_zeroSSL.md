# Fix for Rate Limited LetsEncrypt
This is a fix/workaround for Rate Limited LetsEncrypt on GitLab Helm installation. The GitLab helm chart includes bundled certmanager which uses letsencrypt by default. If you use this too frequently LetsEncrypt's CA will rate limit you and block and certificate requests for the host.

This solution deploys a differet CA (ZeroSSL) as a separate ClusterIssuer, and manually deploys a certificate using that clusterissuer. The cert will be installed into secret **gitlab-gitlab-tls** which should be the default with Gitlab's ingress. 

When you have certificate issues, your GitLab Runner registration will also fail. So this solution will also solve runner registration problems

## Steps : 

1. Create this **zero.yaml** and apply it
```
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: zerossl-issuer
spec:
  acme:
    email: "ADD-YOUR-EMAIL-HERE"
    server: "https://acme.zerossl.com/v2/DV90"
    externalAccountBinding:
      keyID: "<YOUR_EAB_KID>"
      keySecretRef:
        name: zerossl-secret
        key: secret
    privateKeySecretRef:
      name: zerossl-account-key
    solvers:
      - http01:
          ingress:
            class: nginx
```

2. Apply it with `kubectl apply -f zero.yaml`

3. Create another file, **certificate.yaml**
```
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: gitlab-gitlab-tls
  namespace: default
spec:
  secretName: gitlab-gitlab-tls
  issuerRef:
    name: zerossl-issuer
    kind: ClusterIssuer
  dnsNames:
    - ADD-VALID-FQDN-HERE

```

4. Apply it with `kubectl apply -f certificate.yaml`

5. Delete orders and challenges to let it restart
```
kubectl delete certificate gitlab-gitlab-tls -n default
kubectl delete order -n default --all
kubectl delete challenge -n default --all
kubectl delete secret gitlab-gitlab-tls -n default
```



## Bonus - Fix Runner
Once your SSL certificate is valid on GitLab's ingress, you can redeploy any Runner deployments that were failing
```
kubectl rollout restart deployment gitlab-runner
```
