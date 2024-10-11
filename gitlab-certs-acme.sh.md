# How to use Acme.sh to automate SSL certs for Gitlab

This assumes using DNS challenge and hosting DNS records on Azure DNS. As such an SPN with a client secret is required.

1. Add Azure SPN details into environment variables
   ```bash
   export AZUREDNS_SUBSCRIPTIONID="your_subscription_id"
   export AZUREDNS_TENANTID="your_tenant_id"
   export AZUREDNS_APPID="your_app_id"
   export AZUREDNS_CLIENTSECRET="your_app_secret"
   ```
2. Install acme.sh on the Gitlab server (as root)
   ```bash
   curl https://get.acme.sh | sh
   ```

3. Register an acme account
   ```bash
   acme.sh --register-account -m your-email@example.com
   ```

4. Provision certificates for your server fqdn
   ```bash
   acme.sh --install-cert -d yourdomain.com \
   --cert-file /etc/gitlab/ssl/yourdomain.com.crt \
   --key-file /etc/gitlab/ssl/yourdomain.com.key \
   --fullchain-file /etc/gitlab/ssl/yourdomain.com.fullchain.crt \
   --reloadcmd "gitlab-ctl restart nginx"
   ```
