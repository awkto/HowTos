# How to Install Gitlab EE on a VM quickly

These instructions are for RHEL/Fedora based distros (but should mostly work for Debian based distros as well)

## Grab Installer files 
- Grab installer from [packages site](https://packages.gitlab.com/gitlab/gitlab-ee)
- Search to filter for version
- Filter for `el/8` to match RHEL8 or AlmaLinux8 version
- Select x86_64 architecture
- Example package [gitlab-ee-17.1.1-ee.0.el8.x86_64.rpm](https://packages.gitlab.com/gitlab/gitlab-ee/packages/el/8/gitlab-ee-17.1.1-ee.0.el8.x86_64.rpm)
- Download it with the wget command from that download page
```
wget --content-disposition https://packages.gitlab.com/gitlab/gitlab-ee/packages/el/8/gitlab-ee-17.1.1-ee.0.el8.x86_64.rpm/download.rpm
```

## Install Dependencies
- Install dependencies with
```
sudo yum install ca-certificates curl openssh-server postfix tzdata perl
```

## Install the package
- Install it with
```
sudo rpm -i gitlab-ee-17.1.1-ee.0.el8.x86_64.rpm
```

## Configure gitlab.rb file
- Edit the file
```
sudo nano /etc/gitlab/gitlab.rb
```
- Add or enable the following options
```
# Use a proper public FQDN and use https
external_url 'https://gitlab.example.com'

## Line 2816, uncomment these lines, use own email
letsencrypt['enable'] = nil
letsencrypt['contact_emails'] = ['certs@example.com'] 
```

- Re-configure with
```
sudo gitlab-ctl reconfigure
```

## Log in with initial password
- Grab initial root password from **/etc/gitlab/initial_root_password**
- Log in and change root password
- Disable signups
