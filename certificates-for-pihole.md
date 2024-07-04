# Certbot with Pihole

## Context
[Pihole]([url](https://pi-hole.net/)) is a DNS filtering and management tool. It can be deployed very easily on a Raspberry Pi, but it can also be used on any standard linux machine (x86 or x64 as well)
Pihole gets deployed without any automated SSL certificate signing. If you deploy pihole on your internal network, getting a certificate is very easy with certbot, as long as you have a public domain to certify with.

## How can you use certbot 
Certbot can be used to fetch SSL certificates, by confirming ownership of the domain. Private IPs will work fine here, but the domain needs to be public. 
In fact a public DNS record pointing to your host IP is not required at all. The only requirement for verifying domain ownership is creation of a specific TXT record. This is known as the manual method, and requires a specific command.

## Requirements
- You need certbot installed
- You need a public DNS zone you can create records on

## Part 1 Certbot Instructions
Use this command syntax below, and replace the hostname with your own server hostname. This is the name you will use to connect to your Gitlab server.
_Skip this part if you have already acquired your certificates_

1. Install certbot on a server, it can be any server, not necessary your pihole server
2. Run this command to start the process

`certbot certonly --manual -d *.mydomain.com`

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
6. Grab the 2 certificate files 

- `/etc/letsencrypt/live/dnsif.ca/fullchain.pem`
- `/etc/letsencrypt/live/dnsif.ca/privkey.pem`


---

## Part 2 Certbot Instructions

1. Copy the certificates to Pihole at these locations
- Make a new dir with `sudo mkdir /etc/lighttpd/ssl/`
- Copy **privkey.pem** and **fullchain.pem** to `/etc/lighttpd/ssl/`

2. Create a new config file `/etc/lighttpd/conf-enabled/external.conf` and edit it

3. Enter the following config, replacing the FQDN with your own
```
var.fqdn = "gitlab.dnsif.ca"

$SERVER["socket"] == ":443" {
    ssl.engine = "enable"
    # Public cert and intermediate cert chain
    ssl.pemfile = "/etc/lighttpd/ssl/fullchain.pem"
    ssl.privkey = "/etc/lighttpd/ssl/privkey.pem"
    ssl.ca-file = "/etc/lighttpd/ssl/fullchain.pem"
    # Require TLS 1.3
    ssl.openssl.ssl-conf-cmd = ("MinProtocol" => "TLSv1.3")
}

$HTTP["host"] == fqdn {
    # Set redirect code for any redirects we do
    url.redirect-code = 308
    # Redirect all http to https
    $HTTP["scheme"] == "http" {
        url.redirect = ("" => "https://" + fqdn + "${url.path}${qsa}")
    # Redirect root to admin
    } else $HTTP["url"] == "/" {
        url.redirect = ("" => "/admin/")
    }
}
```

4. Restart lighttpd with `sudo service lighttpd restart`
