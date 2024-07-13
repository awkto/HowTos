# AlmaLinux Setup on New Install

This is a result of broken key trust on DigitalOcean's AlmaLinux images. And this below is the fix.

## Fix broken GPG key for Repository
[Source](https://serverfault.com/questions/1144827/alma-linux-8-update-fails-for-any-package-with-gpg-keys-check-fail)

- Install wget `yum install wget`
- Download key `wget https://repo.almalinux.org/almalinux/RPM-GPG-KEY-AlmaLinux`
- Move to right place `sudo mv RPM-GPG-KEY-AlmaLinux /etc/pki/rpm-gpg/`

Alternately, in fewer commands 
```
yum install wget
sudo wget https://repo.almalinux.org/almalinux/RPM-GPG-KEY-AlmaLinux -o /etc/pki/rpm-gpg/RPM-GPG-KEY-AlmaLinux
sudo wget https://repo.almalinux.org/almalinux/RPM-GPG-KEY-AlmaLinux; sudo mv RPM-GPG-KEY-AlmaLinux /etc/pki/rpm-gpg/
```

## Setup New User

```
adduser ...
usermod -aG wheel ...
visudo   #add NOPASSWD
mkdir /home/[...]/.ssh
cp ~/.ssh/authorized_keys /home/[...]/.ssh/
chown user:user /home/user/.ssh
chown user:user /home/user/.ssh/authorized_keys
passwd user
```
