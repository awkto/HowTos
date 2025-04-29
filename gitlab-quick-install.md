## Deploy GitLab and certs with 1 command

Note : Public port 80 must be accessible for this to work because GitLab’s built-in letsencrypt option uses the web server verification only, and DNS is not yet supported.

<br>

1. Deploy Ubuntu VM with public IP (and port 80 accessible)
2. Create public DNS record for the VM
3. SSH into the VM
4. Add pre-requisites

```
sudo apt-get update
sudo apt-get install -y curl openssh-server ca-certificates tzdata perl
```
5. Add gitlab package repo

```
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ee/script.deb.sh | sudo bash
```
6. List GitLab versions and pick one  
`apt-cache madison gitlab-ee` 
7. Install GitLab with certs

```
 sudo EXTERNAL_URL="https://gitlab5.dnsif.ca" apt-get install gitlab-ee=17.11.1-ee.0
```

<br>

#### Additonal Options

- Specify version:`sudo EXTERNAL_URL="https://gitlab.example.com" apt-get install gitlab-ee=17.11.1-ee.0`
- Pin the version to limit auto-updates:`sudo apt-mark hold gitlab-ee`
- Show what packages are held back:`sudo apt-mark showhold`
