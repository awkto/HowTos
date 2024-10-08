### Install Tailscale
```
curl -fsSL https://tailscale.com/install.sh | sh
```

### Enable IP Forwarding
```
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf
```

### Start Tailscale
```
sudo tailscale up --reset --advertise-routes=10.20.0.0/16
```
