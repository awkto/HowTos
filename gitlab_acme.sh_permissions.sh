# GitLab with Acme.sh for automated SSL certificate renewals

### Assumptions for this guide:

  * **User:** `user`
  * **GitLab Hostname:** `gitlab.example.com`
  * `acme.sh` will be installed in `/home/user/.acme.sh/`
  * **Operating System:** Debian/Ubuntu-like
  * You have root/sudo access to perform system-level configurations.

-----

## Part 1 User and Group Permissions

1.  **Create dedicated user if needed:**
    *(Optional, assuming `user` already exists. If not, create them.)*
    ```bash
    sudo adduser user
    ```
2.  **Add user to `sudo` group:**
    ```bash
    sudo usermod -aG sudo user
    ```
      * **Important:** Log out of the `user` session and log back in for group changes to take effect.
3.  **Add `visudo` `NOPASSWD` option for `user`:**
    This allows `user` to run specific `sudo` commands without being prompted for a password, which is essential for automated renewals.
    Run `sudo visudo` (always use `visudo` to edit `sudoers` file for syntax checking).
    Add the following lines at the end of the file (or create a new file in `/etc/sudoers.d/`, e.g., `sudo visudo -f /etc/sudoers.d/acme_gitlab`):
    ```
    # Allow 'user' to run specific commands without password for acme.sh
    user ALL=(root) NOPASSWD: /usr/bin/gitlab-ctl
    user ALL=(root) NOPASSWD: /bin/chmod
    ```
      * **Rationale:**
          * We specify the exact paths (`/usr/bin/gitlab-ctl`, `/bin/chmod`) for security and robustness in cron environments.
          * `NOPASSWD` is required for `acme.sh`'s automated `--reloadcmd` to work.
      * **Do NOT use `user ALL=(ALL:ALL) NOPASSWD:ALL`** unless you fully understand the security implications. This gives `user` full `sudo` access without a password, which is usually undesirable for non-root accounts. We are limiting it to *only* the commands needed.
4.  **Create `ssladmins` group and add `user` to it:**
    This group will be used for the `/etc/gitlab/ssl` directory's group ownership, allowing `user` to write directly to it.
    ```bash
    sudo groupadd ssladmins
    sudo usermod -aG ssladmins user
    ```
      * **Important:** Log out of the `user` session and log back in for group changes to take effect. Verify with `id user`.

-----

## Part 2 Directory and File Permissions (as `root` or with `sudo`)

These commands ensure `acme.sh` can write to the `ssl` directory, and GitLab's Nginx can securely read the files.

1.  **Ensure ownership and permissions for `/etc/gitlab/ssl` directory:**
    ```bash
    sudo chown root:ssladmins /etc/gitlab/ssl/
    sudo chmod 770 /etc/gitlab/ssl/
    ```
      * **Rationale:** `770` (`drwxrws---`) allows `root` and members of `ssladmins` (which now includes `user`) to read, write, and execute in this directory. This is essential for `acme.sh` (running as `user`) to copy/overwrite certificate files. The `s` bit (`setgid`) ensures new files inherit the `ssladmins` group (though we'll explicitly `chown`/`chmod` them later).
2.  **Ensure ownership and permissions for certificate file (`/etc/gitlab/ssl/gitlab.example.com.cer`):**
    *(These commands will be part of the `acme.sh --reloadcmd` and are applied manually after initial deployment for correctness).*
      * **For `acme.sh` to copy/overwrite:**
        ```bash
        sudo chown root:ssladmins /etc/gitlab/ssl/gitlab.example.com.cer
        sudo chmod 664 /etc/gitlab/ssl/gitlab.example.com.cer
        ```
          * **Rationale:** This makes the existing `.cer` file writable by `user` (via `ssladmins` group) to allow `acme.sh` to overwrite it.
      * **For final, secure state (in `reloadcmd`):**
        ```bash
        sudo chown root:root /etc/gitlab/ssl/gitlab.example.com.cer
        sudo chmod 644 /etc/gitlab/ssl/gitlab.example.com.cer
        ```
          * **Rationale:** `644` (`rw-r--r--`) is standard for certificates: `root` can read/write, others can read. `root:root` ownership is standard.
3.  **Ensure ownership and permissions for key file (`/etc/gitlab/ssl/gitlab.example.com.key`):**
    *(These commands will be part of the `acme.sh --reloadcmd` and are applied manually after initial deployment for correctness).*
      * **For `acme.sh` to copy/overwrite:**
        ```bash
        sudo chown root:ssladmins /etc/gitlab/ssl/gitlab.example.com.key
        sudo chmod 660 /etc/gitlab/ssl/gitlab.example.com.key
        ```
          * **Rationale:** This makes the existing `.key` file writable by `user` (via `ssladmins` group) to allow `acme.sh` to overwrite it.
      * **For final, secure state (in `reloadcmd`):**
        ```bash
        sudo chown root:root /etc/gitlab/ssl/gitlab.example.com.key
        sudo chmod 600 /etc/gitlab/ssl/gitlab.example.com.key
        ```
          * **Rationale:** `600` (`rw-------`) is **CRITICAL** for private keys: `root` can read/write, no one else has any access. `root:root` ownership is standard. This is essential for Nginx to load the key securely.

-----

## Part 3 Deploy Cert with `acme.sh` (as `user`)

1.  **Install `acme.sh` (if not already installed):**

    ```bash
    curl https://get.acme.sh | sh -s -- home /home/user/.acme.sh
    ```

      * **Rationale:** This installs `acme.sh` to the specified home directory and usually sets up a cron job (see Part 4).
      * **Important:** Close your terminal and open a new one after installation to ensure `acme.sh`'s environment variables are loaded.

2.  **Initial deployment and certificate issuance (run only once for the first time):**
    This command obtains the certificate and sets up the deployment hook.

    ```bash
    cd /home/user/.acme.sh/
    ./acme.sh --issue -d gitlab.example.com --nginx \
    --home "/home/user/.acme.sh" \
    --key-file /etc/gitlab/ssl/gitlab.example.com.key \
    --fullchain-file /etc/gitlab/ssl/gitlab.example.com.cer \
    --reloadcmd "sudo chmod 600 /etc/gitlab/ssl/gitlab.example.com.key && sudo chmod 644 /etc/gitlab/ssl/gitlab.example.com.cer && sudo gitlab-ctl reconfigure && sudo gitlab-ctl restart nginx" \
    --debug 2
    ```

      * **Rationale:**
          * `--issue`: Instructs `acme.sh` to obtain a new certificate.
          * `--nginx`: Specifies the validation method (assuming Nginx is serving web content on ports 80/443).
          * `--key-file` and `--fullchain-file`: These tell `acme.sh` where to copy the newly issued certificate and key. Since `user` is in `ssladmins` and `/etc/gitlab/ssl` is `g+w`, `acme.sh` can write here.
          * `--reloadcmd`: This crucial part runs *after* a successful issue/renewal. It first secures the copied files' permissions and then tells GitLab to pick them up.
              * **Initial deployment requires `acme.sh` to write a *new* key file to `/etc/gitlab/ssl/`.** This command handles that.
          * `--debug 2`: Provides verbose output for debugging.

3.  **Manually verify final key/cert permissions and ownership (as `root` or `sudo`):**
    Even though `reloadcmd` runs `chmod`, it's good to verify the *final* state after the first deployment.

    ```bash
    sudo ls -lh /etc/gitlab/ssl/gitlab.example.com.key
    sudo ls -lh /etc/gitlab/ssl/gitlab.example.com.cer
    # Expected: -rw------- (600) root root for key, -rw-r--r-- (644) root root for cert
    ```

-----

## Part 4 Verify Scheduled `acme.sh` in Cron Tab

1.  **Check `crontab` for the `user`:**
    ```bash
    crontab -l
    ```
      * **Expected Output:** You should see a line similar to:
        ```
        0 0 * * * "/home/user/.acme.sh"/acme.sh --cron --home "/home/user/.acme.sh" > /dev/null
        ```
      * **Rationale:** This cron job ensures `acme.sh` runs daily at midnight to check for and perform renewals.
2.  **Check `systemd` timers (if applicable and `acme.sh` installed with systemd timer):**
    ```bash
    systemctl list-timers --all | grep acme.sh
    ```
      * **Rationale:** Some `acme.sh` installations use `systemd` timers instead of `cron`. If you primarily use `systemd` and `acme.sh` was installed to leverage it, you might see an entry here. Our guide primarily focuses on cron, but it's good to check.

-----

## Part 5 Save Command to Manually Renew

These aliases provide quick commands for manual renewal, useful for testing or emergencies. Add them to your `~/.bashrc` (or `~/.zshrc` if you use Zsh) and then run `source ~/.bashrc`.

```bash
alias renewcert='acme.sh --renew -d gitlab.example.com"'
alias renewcertforce='acme.sh --renew -d gitlab.example.com --force'
alias renewcertdebug='acme.sh --renew -d gitlab.example.com --debug 2'
alias renewcertforcedebug='acme.sh --renew -d gitlab.example.com --force --debug 2'
```

  * **Rationale:** The `cd` command ensures `acme.sh` is run from its correct directory. These commands allow you to manually trigger a renewal, which then executes the `--reloadcmd` to copy files and update GitLab.

