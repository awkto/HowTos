# How to use Acme.sh to automate SSL certs for Gitlab

This assumes using DNS challenge and hosting DNS records on DigitalOcean DNS. As such an SPN with a client secret is required.

1. Add DigitalOcean token into environment variable
   ```bash
   export DO_API_KEY=[your-digitalocean-api-key]
   ```
   
2. Install acme.sh on the Gitlab server (as root)
   ```bash
   curl https://get.acme.sh | sh
   ```

3. Register an acme account
   ```bash
   acme.sh --register-account -m your-email@example.com
   ```

4. Provision certificates for your gitlab server FQDN
   ```bash
   acme.sh --issue --dns dns_dgon -d gitlab.yourdomain.com
   ```
   Or
   ```bash
   acme.sh --issue --dns dns_dgon -d gitlab.yourdomain.com --server letsencrypt
   ```


5. Install the certificates into the Gitlab SSL directory
   ```bash
   acme.sh --install-cert -d gitlab.yourdomain.com \
   --cert-file /etc/gitlab/ssl/gitlab.yourdomain.com.crt \
   --key-file /etc/gitlab/ssl/gitlab.yourdomain.com.key \
   --fullchain-file /etc/gitlab/ssl/gitlab.yourdomain.com.fullchain.crt \
   --reloadcmd "gitlab-ctl restart nginx"
   ```

6. Alternately add symbolic links to the SSL certificates
   ```bash
   ln -s /home/user/.acme.sh/gitlab.domain.com/gitlab.domain.com.key /etc/gitlab/ssl/gitlab.domain.com.key
   ln -s /home/user/.acme.sh/gitlab.domain.com/gitlab.domain.com.cer /etc/gitlab/ssl/gitlab.domain.com.cer
   ```

7. Make sure your gitlab nginx conf points to the correct cert files
   ```bash
   ssl_certificate /etc/gitlab/ssl/gitlab.domain.com.cer;
   ssl_certificate_key /etc/gitlab/ssl/gitlab.domain.com.key;
   ```

8. Restart nginx
   ```bash
   sudo gitlab-ctl restart nginx
   ```

9. (Optional), add an HTTP redirect to Gitlab's Nginx config `/var/opt/gitlab/nginx/conf/gitlab-http.conf`
   ```bash
   server {
     listen *:80;
     server_name gitlab.domain.com gitlab02.domain.com gitlab.nginx.domain.com gitlab02.nginx.domain.com;
     return 302 https://$host$request_uri;
   }
   ```

10. If you ever need to re-configure gitlab with `gitlab-ctl reconfigure` make sure your **gitlab.rb** contains these lines
```bash
nginx['ssl_certificate'] = "/etc/gitlab/ssl/gitlab.domain.com.cer"
nginx['ssl_certificate_key'] = "/etc/gitlab/ssl/gitlab.domain.com.key"
nginx['listen_https'] = true
nginx['generate_default_cert'] = false
```

