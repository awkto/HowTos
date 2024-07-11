# Gitlab Package Download Pages

## Gitlab EE Version 16
https://packages.gitlab.com/gitlab/gitlab-ee/packages/el/8/gitlab-ee-16.0.0-ee.0.el8.x86_64.rpm 
https://packages.gitlab.com/gitlab/gitlab-ee/packages/el/8/gitlab-ee-16.3.7-ee.0.el8.x86_64.rpm
https://packages.gitlab.com/gitlab/gitlab-ee/packages/el/8/gitlab-ee-16.7.7-ee.0.el8.x86_64.rpm
https://packages.gitlab.com/gitlab/gitlab-ee/packages/el/8/gitlab-ee-16.11.4-ee.0.el8.x86_64.rpm 

## Gitlab EE Version 17
https://packages.gitlab.com/gitlab/gitlab-ee/packages/el/8/gitlab-ee-17.1.0-ee.0.el8.x86_64.rpm


# Direct Download Links
## Gitlab EE Version 16
```
wget --content-disposition https://packages.gitlab.com/gitlab/gitlab-ee/packages/el/8/gitlab-ee-16.0.0-ee.0.el8.x86_64.rpm/download.rpm
wget --content-disposition https://packages.gitlab.com/gitlab/gitlab-ee/packages/el/8/gitlab-ee-16.3.7-ee.0.el8.x86_64.rpm/download.rpm
wget --content-disposition https://packages.gitlab.com/gitlab/gitlab-ee/packages/el/8/gitlab-ee-16.7.7-ee.0.el8.x86_64.rpm/download.rpm
wget --content-disposition https://packages.gitlab.com/gitlab/gitlab-ee/packages/el/8/gitlab-ee-16.11.4-ee.0.el8.x86_64.rpm/download.rpm
```

## Gitlab EE Version 17
`wget --content-disposition https://packages.gitlab.com/gitlab/gitlab-ee/packages/el/8/gitlab-ee-17.1.0-ee.0.el8.x86_64.rpm/download.rpm`

# Gitlab Runner Download Page
https://docs.gitlab.com/runner/install/linux-manually.html

## Direct Link Debian
```
curl -LJO "https://s3.dualstack.us-east-1.amazonaws.com/gitlab-runner-downloads/latest/deb/gitlab-runner_${arch}.deb"
wget "https://s3.dualstack.us-east-1.amazonaws.com/gitlab-runner-downloads/latest/deb/gitlab-runner_amd64.deb"
```
Install with `sudo apt install ./gitlab-runner_amd64.rpm`

## Direct Link CentOS
```
curl -LJO "https://s3.dualstack.us-east-1.amazonaws.com/gitlab-runner-downloads/latest/rpm/gitlab-runner_${arch}.rpm"
wget "https://s3.dualstack.us-east-1.amazonaws.com/gitlab-runner-downloads/latest/rpm/gitlab-runner_amd64.rpm"
```

Install with `sudo rpm -i gitlab-runner_amd64.rpm`
