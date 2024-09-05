# Certbot with Gitlab

## Context
Gitlab uses letsencrypt out of the box to automatically request and install SSL certificates. But this only works with public DNS records. Furthermore, letsencrypt will fail the validation check if your DNS record points to a private IP address.

## How can you use certbot instead
Certbot can similarly be used to fetch SSL certificates, by confirming ownership of the domain. The good news is there isn't a similar validation problem with private IP space. In fact a public DNS record pointing to your host IP is not required at all. The only requirement for verifying domain ownership is creation of a specific TXT record. This is known as the manual method, and requires a specific command.

## Requirements
- You need certbot installed
- You need a public DNS zone you can create records on

## Instructions
Use this command syntax below, and replace the hostname with your own server hostname. This is the name you will use to connect to your Gitlab server.

1. Install certbot on a server, it can be any server, not necessary your Gitlab server
2. Run this command to start the process

`certbot certonly --manual -d *.mydomain.com`
OR 
`certbot certonly --manual --preferred-challenges dns -d *.mydomain.com`


3. Certbot will ask you questions, and eventually give you an output similar to 
```
Please deploy a DNS TXT record under the name:

_acme-challenge.dnsif.ca.

with the following value:

vqcwGUeQVgpfu-D_TIgHobOZ44o7wUUsSpT9nJBKKs4
```
4. Create the TXT record on your public domain, as requested by certbot

5. Hit Enter to continue on certbot

6. Certbot will verify the DNS record and give you this output
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/dnsif.ca/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/dnsif.ca/privkey.pem
This certificate expires on 2024-10-01.
These files will be updated when the certificate renews.
```
6. Grab the 2 certificate files and copy them into your Gitlab server

- `/etc/letsencrypt/live/dnsif.ca/fullchain.pem`
- `/etc/letsencrypt/live/dnsif.ca/privkey.pem`

7. Place the certificates in the following locations, replacing existing certificates
 - sudo cp _fullchain.pem /etc/gitlab/ssl/myhost.mydomain.com.crt_
- sudo cp _privkey.pem /etc/gitlab/ssl/myhost.mydomain.com.key_

8. Restart gitlab services

`sudo gitlab-ctl restart`

Your certificates are now installed.
