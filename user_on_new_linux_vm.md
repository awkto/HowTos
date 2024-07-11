# New User Setup

These instructions assume you have just created a new cloud VM with an SSH key login for the root user.

The goal is to setup a separate user, add it to sudoers, and disable password prompt for sudo, and add authorized keys file to the new user.

## On Ubuntu / Debian based VMs
```
adduser [user]
mkdir /home/[user]/.ssh
cp ~/.ssh/authorized_keys /home/[user]/.ssh/
chown [user]:[user] /home/[user]/.ssh
chown [user]:[user] /home/[user]/.ssh/authorized_keys
usermod -aG sudo [user]
```


## On CentOS / Alma / Redhat based VMs
```
adduser [user]
mkdir /home/[user]/.ssh
cp ~/.ssh/authorized_keys /home/[user]/.ssh/
chown [user]:[user] /home/[user]/.ssh
chown [user]:[user] /home/[user]/.ssh/authorized_keys
usermod -aG wheel [user]
```
