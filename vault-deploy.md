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

## Configure and Start Vault
- Create config.hcl with this template
```
storage "raft" {
  path    = "./vault/data"
  node_id = "node1"
}

listener "tcp" {
  address     = "127.0.0.1:8200"
  tls_disable = "true"
  tls_cert_file = "/etc/letsencrypt/live/example.com/fullchain.pem"
  tls_key_file = "/etc/letsencrypt/live/example.com/privkey.pem"
}

api_addr = "http://127.0.0.1:8200"
cluster_addr = "https://127.0.0.1:8201"
ui = true
```
- Create the data directory specified in the hcl
```
sudo mkdir -p ./vault/data
```
- Start vault with 
```
vault server -config=config.hcl
```
