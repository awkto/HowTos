## 1. Install Docker for Fedora
- Run `sudo dnf -y install dnf-plugins-core`
- Run `sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo`
- Start docker with `sudo systemctl start docker`

## 2. Create DNS entry
- Create TXT record that it requests on your domain :
```
doctl compute domain records create \
  --record-ttl 300 \
  --record-type TXT \
  --record-name _acme-challenge \
  --record-data [string-from-certbot] \
  [yourdomain].com
```

## 3. Generate Certificates with certbot
- Install Certbot `sudo dnf install certbot`
- Generate certs manually with `certbot certonly --manual -d rancher.example.com`
- Go back to certbot to proceed, hit Enter
```
Certificate is saved at: /etc/letsencrypt/live/example.com/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/example.com/privkey.pem
```

## 4. Deploy Rancher container
- Create an instance with
```
docker run -d --restart=unless-stopped \
  -p 80:80 -p 443:443 \
  -v /<CERT_DIRECTORY>/<FULL_CHAIN.pem>:/etc/rancher/ssl/cert.pem \
  -v /<CERT_DIRECTORY>/<PRIVATE_KEY.pem>:/etc/rancher/ssl/key.pem \
  --privileged \
  rancher/rancher:latest \
  --no-cacerts
```
- Check and grab the ID of the container with `docker ps`
- Get the Rancher password with
```
docker logs  container-id  2>&1 | grep "Bootstrap Password:"
```

- Log in to Rancher with a web browser
  
---

## (Alternate) Deploy Rancher container without Certs

### Deploy Container
- Create a docker instance for rancher
```
docker run -d --restart=unless-stopped \
  -p 80:80 -p 443:443 \
  --privileged \
  rancher/rancher:latest
```



