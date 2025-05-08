## Automating Proxmox VE SSL Certificates with acme.sh

This document outlines the steps to automatically obtain and renew Let's Encrypt SSL certificates for your Proxmox VE server using the `acme.sh` script. This method leverages DNS verification, allowing you to secure your Proxmox web interface even if it's not directly accessible via HTTP.

**Tested Environment:** Proxmox VE 8.2

### Prerequisites

* A running Proxmox VE 8.2 instance.
* A registered domain name that you control.
* Access to manage DNS records for your domain.
* `curl` installed on your Proxmox server.

### Step 1: Create a Dedicated User and Add to the `www-data` Group

For security best practices, we'll create a dedicated user to run `acme.sh` and add it to the `www-data` group, which owns the Proxmox SSL certificate files.

```bash
sudo adduser acmeuser
sudo usermod -aG www-data acmeuser
```

You'll be prompted to set a password for the `acmeuser`. Remember this password or store it securely.

### Step 2: Adjust Proxmox SSL Certificate File Permissions

We need to adjust the ownership and permissions of the Proxmox SSL certificate and key files to allow the `www-data` group to read and write to them.

Note : We temporarily set the private key to 660 because acme.sh will need to write to the private key the first time. All renewals after that will only update the certificate file but not the private key. So we will set the permission back to 640 afterwards.

```bash
sudo chown root:www-data /etc/pve/local/pve-ssl.pem
sudo chmod 660 /etc/pve/local/pve-ssl.pem
sudo chown root:www-data /etc/pve/local/pve-ssl.key
sudo chmod 660 /etc/pve/local/pve-ssl.key
```

These commands change the owner of the files to `root` and the group to `www-data`, and then set the permissions so that the owner (root) has read and write access, the group (`www-data`) has read and write access for `pve-ssl.pem` and only read access for `pve-ssl.key`, and no permissions for others.

### Step 3: Install `acme.sh`

`acme.sh` is a simple yet powerful ACME client. We'll install it using `curl`. Replace `your_email@example.com` with your actual email address for Let's Encrypt registration.

```bash
curl https://get.acme.sh | sh -s email=your_email@example.com
```

After installation, source the `acme.sh` environment variables to make the `acme.sh` command available in your current session:

```bash
source ~/.acme.sh/acme.sh.env
```

### Step 4: Configure DNS Provider

`acme.sh` supports various DNS providers for automated DNS challenges. Choose the provider where your domain's DNS records are managed and follow the corresponding instructions.

#### Azure DNS

If you're using Azure DNS, you'll need to set up the necessary environment variables. You'll typically need your Azure Subscription ID, Tenant ID, Client ID, and Client Secret. Refer to the `acme.sh` documentation for detailed instructions on obtaining these credentials.

Once you have the credentials, you can set them as environment variables:

```bash
export AZURE_SUBID="your_azure_subscription_id"
export AZURE_TENANT="your_azure_tenant_id"
export AZURE_CLIENT_ID="your_azure_client_id"
export AZURE_SECRET="your_azure_client_secret"
```

#### DigitalOcean DNS

If you're using DigitalOcean DNS, you'll need to obtain a Personal Access Token with "Read and Write" permissions for your DNS records. You can generate this token in your DigitalOcean control panel.

Once you have the token, set it as an environment variable:

```bash
export DO_API_KEY="your_digitalocean_api_token"
```

### Step 5: Issue and Install the Certificate

Now, we'll issue the certificate for your Proxmox hostname and instruct `acme.sh` to automatically install it to the Proxmox certificate locations and reload the `pveproxy` service. Replace `proxmox2.tux42.au` with your actual Proxmox hostname.

**For Azure DNS:**

```bash
acme.sh --issue --dns dns_azure -d proxmox.example.com --keylength ec-256 \
--install-cert \
--fullchain-file /etc/pve/local/pve-ssl.pem \
--key-file /etc/pve/local/pve-ssl.key \
--reloadcmd "systemctl reload pveproxy.service"
```

**For DigitalOcean DNS:**

```bash
acme.sh --issue --dns dns_dgon -d proxmox.example.com --keylength ec-256 \
--install-cert \
--fullchain-file /etc/pve/local/pve-ssl.pem \
--key-file /etc/pve/local/pve-ssl.key \
--reloadcmd "systemctl reload pveproxy.service"
```

**Explanation of the command:**

* `--issue`: Tells `acme.sh` to request a new certificate.
* `--dns dns_azure` or `--dns dns_dgon`: Specifies the DNS provider to use for verification. Swap `dns_azure` with `dns_dgon` if you are using DigitalOcean.
* `-d proxmox2.tux42.au`: The domain name for which you are requesting the certificate. Ensure this matches your Proxmox hostname.
* `--keylength ec-256`: Requests an ECDSA key with a 256-bit curve, which is a modern and secure option. You can omit this for a standard RSA key.
* `--install-cert`: Instructs `acme.sh` to install the issued certificate.
* `--fullchain-file /etc/pve/local/pve-ssl.pem`: Specifies the destination path for the full certificate chain file.
* `--key-file /etc/pve/local/pve-ssl.key`: Specifies the destination path for the private key file.
* `--reloadcmd "systemctl reload pveproxy.service"`: Specifies the command to run after the certificate is successfully installed. This reloads the Proxmox proxy service to use the new certificate.

After running the command, `acme.sh` will communicate with Let's Encrypt and your DNS provider to issue and install the certificate. You should see output indicating the progress.

### Step 6: Reduce Private Key Permissions

Once the private key has been installed by **acme.sh** into `/etc/pve/local/pve-ssl.key` we can set the group permissions back to read-only.

```bash
sudo chmod 640 /etc/pve/local/pve-ssl.key
```

This is best practice and prevents issues with web-servers complaining about insecure private key permissions (looking at you nginx).

Acme cert renewals only update the certificate, but never modify the private key.


### Step 7: Verify the Certificate

Once the process is complete, open your Proxmox web interface in your browser (using `https://proxmox.example.com:8006`). You should see a valid SSL certificate issued by Let's Encrypt.

### Step 8: Automate Renewal

`acme.sh` automatically creates a cron job to renew your certificates before they expire. You can verify the cron job by listing the cron entries for the `root` user:

```bash
sudo crontab -l
```

You should see an entry related to `acme.sh` that handles the renewal process.

### Conclusion

By following these steps, you have successfully automated the process of obtaining and renewing Let's Encrypt SSL certificates for your Proxmox VE server using `acme.sh` and DNS verification. This ensures your Proxmox web interface is always secured with a valid and trusted SSL certificate. Remember to replace the example domain and DNS provider details with your actual information.
