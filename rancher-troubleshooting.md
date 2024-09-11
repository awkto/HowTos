### Install nginx to use as ingress
nginx ingress may not be installed by default so install it before installing rancher
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```

### Test Certificate HTTP Validation Manually
This command will simulate what letsencrypt checks during HTTP validation
```
curl -v http://rancher.dok3s.dnsif.ca/.well-known/acme-challenge/<token>
```

### Where do you get the token?
Try 
```
kubectl get challenges -n cattle-system
kubectl describe challenges.acme.cert-manager.io -n cattle-system
```
And
```
kubectl get secret rancher-tls -n cattle-system
kubectl describe secret rancher-tls -n cattle-system
kubectl describe ingress rancher -n cattle-system
kubectl describe ingress rancher-ingress -n cattle-system
```

### Check logs for Cert Manager
This should tell you what is failing
```
kubectl logs -n cert-manager -l app=cert-manager
```
