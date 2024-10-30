# Gitlab Runner with DIND support
Using Ubuntu 24.10

1. Add the official GitLab repository:
```
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
```

2. Install runner
```
sudo apt install gitlab-runner
```

3. Register with Gitlab using this format 
_(Important : run this as root)_
```
sudo gitlab-runner register -n \
  --url "https://gitlab.com/" \
  --registration-token REGISTRATION_TOKEN \
  --executor docker \
  --description "My Docker Runner" \
  --docker-image "docker:24.0.5" \
  --docker-privileged \
  --docker-volumes "/certs/client"
```

4. Install docker on runner
```
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```

5. Enable and start the service
```
sudo systemctl start docker
sudo systemctl enable docker
```

6. Add gitlab-runner user to allow docker access
```
sudo usermod -aG docker $USER
```
