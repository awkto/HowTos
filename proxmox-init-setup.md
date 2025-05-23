## Proxmox VE 8.2 Initial Setup Guide

This guide covers common initial tasks after a fresh installation of Proxmox Virtual Environment (PVE) 8.2.

**1. Update Package Repository URLs to Free Versions**

By default, Proxmox installations point to the enterprise repositories. For non-subscription users, we need to modify these to use the free versions.

**1.1. Ceph Repository**

Open the Ceph repository list for editing:

```bash
sudo nano /etc/apt/sources.list.d/ceph.list
```

Comment out the enterprise repository line by adding a `#` at the beginning and add the free version repository as shown below:

```
#deb https://enterprise.proxmox.com/debian/ceph-quincy bookworm enterprise
deb http://download.proxmox.com/debian/ceph-quincy bookworm no-subscription
```

Save the file and exit the editor (usually `Ctrl+X`, then `Y` for yes, and `Enter`).

**1.2. Proxmox VE Repository**

Open the Proxmox VE enterprise repository list for editing:

```bash
sudo nano /etc/apt/sources.list.d/pve-enterprise.list
```

Similarly, comment out the enterprise repository line and add the free version:

```
#deb https://enterprise.proxmox.com/debian/pve bookworm pve-enterprise
deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription
```

Save the file and exit the editor.

**2. Update Packages and Enable sudo**

Now that we've updated the repository sources, let's update the package lists and upgrade the installed packages. We'll also install the `sudo` utility and add your user to the `sudo` group for easier administration.

```bash
sudo apt update
sudo apt upgrade
sudo apt install sudo
```

To allow your non-root user to execute commands with administrative privileges, add your username to the `sudo` group. Replace `$USER` with your actual username if needed:

```bash
sudo usermod -aG sudo $USER
```

You can optionally fine-tune the `sudo` configuration by using `visudo`:

```bash
sudo visudo
```

This command opens the `sudoers` file in a safe editor. Be cautious when making changes here.

**3. Disable Proxmox Nag with nagbuster (Optional)**

If you find the subscription nag screen in the web interface bothersome, you can use the `pve-nag-buster` script to disable it.

```bash
wget -qO- https://raw.githubusercontent.com/foundObjects/pve-nag-buster/master/install.sh | sudo bash
```

This command downloads and executes the installation script. Follow any prompts that appear.

**4. Add nginx Redirect for Port 80/443 (Optional)**

This step allows you to access the Proxmox web interface (which runs on port 8006) using the standard HTTP (port 80) and HTTPS (port 443) ports through an nginx reverse proxy. This can be useful if you want to use a simpler URL or integrate with other web services.

**4.1. Install nginx**

```bash
sudo apt install nginx
```

**4.2. Create a New nginx Site Configuration**

Create a new configuration file for your Proxmox redirect. You can name it `redirect-proxmox`:

```bash
sudo nano /etc/nginx/sites-available/redirect-proxmox
```

Add the following configuration to this file, replacing `proxmox.example.com` with your actual Proxmox hostname or IP address:

```nginx
server {
    listen 80;
    server_name proxmox.example.com;
    return 301 https://$host:8006$request_uri;
}

server {
    listen 443 ssl http2;
    server_name proxmox.example.com;

    ssl_certificate /etc/pve/local/pve-ssl.pem;
    ssl_certificate_key /etc/pve/local/pve-ssl.key;

    return 301 https://$host:8006$request_uri;
}
```

Alternately, if you prefer to proxy instead of redirect, use this config 

```nginx
server {
    listen 80;
    server_name proxmox.example.com;
    return 301 https://$host:8006$request_uri;
}

server {
    listen 443 ssl http2;
    server_name proxmox.example.com;

    # You'll likely want to configure SSL certificates here
    # For self-signed certificates (not recommended for production):
    ssl_certificate /etc/pve/local/pve-ssl.pem;
    ssl_certificate_key /etc/pve/local/pve-ssl.key;

    location / {
        proxy_pass https://localhost:8006;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Note:** This basic configuration for HTTPS assumes you have SSL certificates. For a production environment, you should obtain and configure valid SSL certificates (e.g., using Let's Encrypt). The commented-out `ssl_certificate` and `ssl_certificate_key` lines are for self-signed certificates, which will likely cause browser warnings.

**4.3. Enable the Site and Disable the Default Site**

Create a symbolic link of your configuration file to the `sites-enabled` directory and disable the default nginx site:

```bash
sudo ln -s /etc/nginx/sites-available/redirect-proxmox /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
```

**4.4. Test and Reload nginx Configuration**

Before restarting nginx, test the configuration for any errors:

```bash
sudo nginx -t
```

If the test is successful, reload the nginx service to apply the changes:

```bash
sudo systemctl reload nginx
```

**5. Create your Admins group and user**

**5.1 Create a Linux user:** 

SSH into your Proxmox host as root (or a user with sudo privileges) and use `adduser` to create a new system user (e.g., `adduser bobdylan`). When you add the user it will ask you to specify a password. Remember this password for later.

**5.2 Create an 'Admins' group in Proxmox:**

Log in to the Proxmox web interface as 'root', go to **Datacenter > Permissions > Groups**, and create a new group named 'Admins'.

**5.3 Grant Administrator role to the 'Admins' group:**

Navigate to **Datacenter > Permissions**, click **Add > Group Permission**, set the **Path** to `/`, select **Admins** as the **Group**, and choose the **Administrator** role.

**5.4 Add the Linux user to Proxmox and the 'Admins' group:**

Go to **Datacenter > Permissions > User**, add a new user with the same username as the Linux user created earlier, and then select **Admins** as the **Group** for this user.

**5.5 Verify:**

Log out of the Proxmox web interface as 'root' and log back in using the newly created administrative user to confirm the permissions are working correctly.

The password for the web login will be what you set when you created the user at the OS level. If you need to reset it just SSH via root and run 'passwd [username]' to specify a new password.

**6. Automate SSL Certificates with acme.sh**

[Follow instructions here](./proxmox-certs-with-acme.sh.md)

Now you should be able to access your Proxmox web interface by navigating to `http://proxmox.example.com` or `https://proxmox.example.com` in your web browser.

This guide covers some of the fundamental initial setup steps for your Proxmox VE 8.2 installation. Depending on your specific needs, you might have other configurations to perform, such as setting up networking, storage, or user management. Let me know if you have any other questions or need further assistance!
