## How to create a UserData template

1. Go to **Harvester web interface**
2. Go to **Virtual Machines**
3. Go to **Advanced**
4. Select **Cloud Configuration Templates**
5. Click **Create**
6. Set **Template Type** to *User Data*
7. Enter this Userdata template for example
```
#cloud-config
users:
  - name: awktopo
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    groups: sudo
    shell: /bin/bash
    ssh-authorized-keys:
      - ssh-rsa xxxx.xxxxx awkto@box

chpasswd:
  expire: False

ssh_pwauth: False
```
8. Hit Save/Create
