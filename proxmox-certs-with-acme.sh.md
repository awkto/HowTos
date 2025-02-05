### Updated Summary: Installing SSL Certificates on Proxmox Using `acme.sh` and DigitalOcean DNS Challenge

#### Prerequisites
- Ensure `acme.sh` is installed.
- Obtain a DigitalOcean API token with DNS write permissions.

#### 1. **Register Your Email with `acme.sh`**
Before issuing any certificates, register your email address (for notifications and key recovery):

```bash
acme.sh --register-account -m your-email@example.com
```

#### 2. **Issue the SSL Certificate**
Request an ECC certificate for your Proxmox domain using the DNS challenge with DigitalOcean:

```bash
export DO_API_TOKEN="your_digitalocean_api_token"
acme.sh --issue --dns dns_dgon -d proxmox.example.com --keylength ec-256
```

#### 3. **Install the Certificate to a Staging Directory**
Install the certificate to a user-accessible directory:

```bash
acme.sh --install-cert -d proxmox.example.com \
--key-file /home/demouser/.acme.sh/proxmox.example.com_ecc/proxmox.example.com.key \
--fullchain-file /home/demouser/.acme.sh/proxmox.example.com_ecc/fullchain.cer \
--reloadcmd "/home/demouser/acme-proxmox-hook.sh"
```

#### 4. **Create a Hook Script to Copy the Certificates**
Create a script (`/home/demouser/acme-proxmox-hook.sh`) to copy the certificates to Proxmox’s SSL folder:

```bash
#!/bin/bash

# Copy the key and certificate to Proxmox's SSL folder
sudo cp /home/demouser/.acme.sh/proxmox.example.com_ecc/proxmox.example.com.key /etc/pve/local/pve-ssl.key
sudo cp /home/demouser/.acme.sh/proxmox.example.com_ecc/fullchain.cer /etc/pve/local/pve-ssl.pem

# Set correct permissions
sudo chmod 640 /etc/pve/local/pve-ssl.key
sudo chmod 640 /etc/pve/local/pve-ssl.pem

# Restart the Proxmox proxy service to apply the new certificates
sudo systemctl restart pveproxy
```

Make the script executable:

```bash
chmod +x /home/demouser/acme-proxmox-hook.sh
```

#### 5. **Grant `sudo` Permissions for the Hook Script**
Edit the `sudoers` file using `visudo` and add:

```bash
demouser ALL=(root) NOPASSWD: /bin/cp, /bin/chmod, /bin/systemctl
```

#### 6. **Run the Hook Script Manually for Initial Setup**
Execute the hook script to copy the certificates and restart Proxmox:

```bash
/home/demouser/acme-proxmox-hook.sh
```

#### 7. **Verify the SSL Certificate**
Visit your Proxmox web interface (`https://proxmox.example.com`) to ensure the new SSL certificate is applied correctly.

### Key Points
- Registered an account with `acme.sh` using your email.
- Used `acme.sh` as a non-root user.
- Leveraged a hook script with `sudo` for secure file copying.
- Automated the reload of the Proxmox proxy service to apply changes.

This process is secure, streamlined, and includes account registration for better certificate management.
