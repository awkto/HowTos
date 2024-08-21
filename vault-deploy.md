# First lets sort out DNS and Certificates
This assumes using Ubuntu for the OS and digitalocean for DNS records

## 1. Generate Certificates with certbot
- Install Certbot `sudo dnf install certbot`
- Generate wildcard cert manually with `certbot certonly --manual -d *.example.com`
- This will then give you a specific string to add as TXT record for DNS verification.
- Copy that string and keep this prompt open
- Start a separte session for the next step to create the DNS TXT record

## 2. Create DNS entry
- Create TXT record that it requests on your domain :
```
doctl compute domain records create \
  --record-ttl 300 \
  --record-type TXT \
  --record-name _acme-challenge \
  --record-data [string-from-certbot] \
  [yourdomain].com
```

- Go back to certbot to proceed, hit Enter
```
Certificate is saved at: /etc/letsencrypt/live/example.com/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/example.com/privkey.pem
```
- Copy the certs to correct director
```
sudo cp /etc/letsencrypt/live/example.com/fullchain.pem /opt/vault/tls/
sudo cp /etc/letsencrypt/live/example.com/fullchain.pem /opt/vault/tls/
```
- As root, fix the ownership of the cert files
```
sudo chown vault:vault /opt/vault/tls/fullchain.pem
sudo chown vault:vault /opt/vault/tls/privkey.pem
```

# Now let us Install Vault

## 3. Setup Vault repo on Ubuntu
- Install gpg and wget
```
sudo apt update && sudo apt install gpg wget
```
- Install keyring
```
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
```
- Add hashicorp repo
```
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
```

## 4. Install Vault
- Install with :
```
sudo apt update && sudo apt install vault
```

# Next create Vault config
Vault is now installed but not running. Lets configure and start it

## 5. Configure Vault HCL file
- Edit /etc/vault.d/vault.hcl and paste this template 
```
storage "raft" {
  path    = "/opt/vault/data"
  node_id = "node1"
}

# HTTPS listener
listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_cert_file = "/opt/vault/tls/fullchain.pem"
  tls_key_file  = "/opt/vault/tls/privkey.pem"
}

api_addr = "https://vaultau.dnsif.ca:8200"
cluster_addr = "https://vaultau.dnsif.ca:8201"
ui = true

```
- Create the data directory specified in the hcl and fix owner
```
sudo mkdir -p /opt/vault/data
sudo chown vault:vault /opt/vault/data
```
- Set environment var for VAULT address
```
export VAULT_ADDR='https://[ADD FQDN HERE]:8200'
```

## 6. Add vault to systemd 
Vault is still being run manually. Lets make it a service / systemd unit

- Create a file here `/etc/systemd/system/vault.service`
- Paste this template in the file
```
[Unit]
Description="HashiCorp Vault"
Requires=network-online.target
After=network-online.target ConditionFileNotEmpty=/etc/vault.d/vault.hcl StartLimitIntervalSec=60
StartLimitBurst=3

[Service]
User=vault
Group=vault
ProtectSystem=full
ProtectHome=read-only
PrivateTmp=yes
PrivateDevices=yes
SecureBits=keep-caps
AmbientCapabilities=CAP_IPC_LOCK
Capabilities=CAP_IPC_LOCK+ep
CapabilityBoundingSet=CAP_SYSLOG CAP_IPC_LOCK
NoNewPrivileges=yes
ExecStart=/usr/bin/vault server -config=/etc/vault.d/vault.hcl ExecReload=/bin/kill --signal HUP $MAINPID
KillMode=process
KillSignal=SIGINT
Restart=on-failure
RestartSec=5
TimeoutStopSec=30
StartLimitInterval=60
StartLimitIntervalSec=60
StartLimitBurst=3
LimitNOFILE=65536
LimitMEMLOCK=infinity

[Install]
WantedBy=multi-user.target
```
- Save it
- Start the service with
```
sudo systemctl daemon-reload
sudo systemctl enable vault.service
sudo systemctl start vault.service
```



## 7. Initialize and Unseal Vault
Vault is now running 

- Initialize vault with
```
vault operator init -key-shares=1 -key-threshold=1
```
- Copy the Unseal keys and save them in a secure separate place
- Unseal vault with
```
vault operator unseal
```
- Enter one of the unseal keys


