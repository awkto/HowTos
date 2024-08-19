## Rancher Setup using Docker image

### Install Docker for Fedora
- Run `sudo dnf -y install dnf-plugins-core`
- Run `sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo`
- Start docker with `sudo systemctl start docker`

### Deploy Container
- Create a docker instance for rancher
```
docker run -d --restart=unless-stopped \
  -p 80:80 -p 443:443 \
  --privileged \
  rancher/rancher:latest
```
- Check and grab the ID of the container with `docker ps`
- Get the Rancher password with
```
docker logs  container-id  2>&1 | grep "Bootstrap Password:"
```

### Install Certificate
...
