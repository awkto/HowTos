## Mini-Guide: WireGuard Bastion Setup for NAT'd Server Access

**Scenario:** You want to access a private network (`10.50.0.0/16`) connected to a WireGuard server (`wg-server`) that is behind a NAT/firewall with no public port forwarded. You will use a publicly accessible server (`wg-bastion`) as a jump host/bastion. Clients connect to the bastion, which relays traffic through a reverse tunnel initiated by the `wg-server`.

<br>

## **Network Setup:**

- **VPN Subnet:** `10.88.0.0/24`
- **wg-server (Behind NAT):** VPN IP `10.88.0.1`, physical IP on `10.50.0.0/16` network (e.g., `10.50.4.18`). Needs access to the `10.50.0.0/16` subnet via a specific interface (e.g., `ens18`).
- **wg-bastion (Public):** VPN IP `10.88.0.2`, public IP/domain (e.g., `wgjump.dnsif.ca`), UDP port `51820` open.
- **Client(s):** VPN IP `10.88.0.3` (and subsequent IPs).

**Date Context:** This guide reflects the setup as of April 19, 2025.

**1\. Prerequisites:**

- Three machines (Linux recommended for server/bastion, any OS for client).
- WireGuard and `wireguard-tools` installed on all machines.
- Publicly accessible IP address and/or domain name for `wg-bastion`.
- Ability to open UDP port `51820` (or your chosen port) on the `wg-bastion` firewall.
- Root/sudo access on server and bastion.

**2\. Key Generation:**

Each machine needs a private and public key pair. You can generate them using `wg genkey | tee privatekey | wg pubkey > publickey`.

_(Using the keys provided in the example):_

- **wg-bastion:**
    - Private: `bN3xP7yGz6hK0jL9mN2qR5tV8xZ1bA4cD7fG9hJ1kM`
    - Public: `fG9hJ1kM3bN3xP7yGz6hK0jL9mN2qR5tV8xZ1bA4cD=`
- **wg-server:**
    - Private: `rV8xZ1bA4cD7fG9hJ1kM3bN3xP7yGz6hK0jL9mN2qQ=`
    - Public: `z6hK0jL9mN2qR5tV8xZ1bA4cD7fG9hJ1kM3bN3xP7yG=`
- **Client (spectre):**
    - Private: `qR5tV8xZ1bA4cD7fG9hJ1kM3bN3xP7yGz6hK0jL9mN=`
    - Public: `hK0jL9mN2qR5tV8xZ1bA4cD7fG9hJ1kM3bN3xP7yGz6=`

**3\. WireGuard Configuration Files:**

Create configuration files (e.g., `/etc/wireguard/wg0.conf`) on each machine.

**A. `wg-server` Configuration (`/etc/wireguard/wg0.conf`)**

- Initiates connection to bastion.
- Routes traffic between VPN and physical net (`10.50.0.0/16`).
- Performs NAT (Masquerade) for VPN clients accessing the physical net.
- **CRITICAL:** Replace `ens18` with the actual network interface name on your server connected to the `10.50.0.0/16` network.

**Ini, TOML**

<br>

```
# /etc/wireguard/wg0.conf on wg-server (e.g., wgserver.tux42.au)

[Interface]
PrivateKey = rV8xZ1bA4cD7fG9hJ1kM3bN3xP7yGz6hK0jL9mN2qQ=
Address = 10.88.0.1/24
ListenPort = 51820 # Optional here, but harmless

# --- IMPORTANT: Replace 'ens18' if your physical interface name is different ---
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -s 10.88.0.0/24 -o ens18 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -s 10.88.0.0/24 -o ens18 -j MASQUERADE

# Peer: Bastion/Jump Server
[Peer]
PublicKey = fG9hJ1kM3bN3xP7yGz6hK0jL9mN2qR5tV8xZ1bA4cD=
# AllowedIPs: Accept packets sourced from anywhere in the VPN subnet,
# arriving via the bastion (covers bastion itself + forwarded clients).
AllowedIPs = 10.88.0.0/24
Endpoint = wgjump.dnsif.ca:51820 # Bastion's public address
PersistentKeepalive = 25 # Keeps connection through NAT alive
```

**B. `wg-bastion` Configuration (`/etc/wireguard/wg0.conf`)**

- Listens for connections from server and client(s).
- Forwards traffic between client(s) and the server peer.
- Routes traffic destined for `10.50.0.0/16` towards the server peer.

**Ini, TOML**

<br>

```
# /etc/wireguard/wg0.conf on wg-bastion (e.g., wgjump.dnsif.ca)

[Interface]
PrivateKey = bN3xP7yGz6hK0jL9mN2qR5tV8xZ1bA4cD7fG9hJ1kM
Address = 10.88.0.2/24
ListenPort = 51820 # Essential: Must listen for connections

# Allow forwarding between wg0 peers
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT

# Peer: WG Server (behind NAT)
[Peer]
PublicKey = z6hK0jL9mN2qR5tV8xZ1bA4cD7fG9hJ1kM3bN3xP7yG=
# AllowedIPs: Route server's VPN IP and the target physical subnet TO this peer.
AllowedIPs = 10.88.0.1/32, 10.50.0.0/16
# NO Endpoint - Server initiates

# Peer: Client (spectre)
[Peer]
PublicKey = hK0jL9mN2qR5tV8xZ1bA4cD7fG9hJ1kM3bN3xP7yGz6=
# AllowedIPs: Route only this client's VPN IP TO this peer.
AllowedIPs = 10.88.0.3/32

# Add more [Peer] sections for additional clients, assigning unique IPs (e.g., 10.88.0.4/32)
```

**C. `Client` Configuration (e.g., `wg0.conf` or imported into GUI)**

- Connects to the bastion.
- Routes traffic for VPN subnet and target physical subnet through the tunnel.

**Ini, TOML**

<br>

```
# wg0.conf on Client (e.g., spectre)

[Interface]
PrivateKey = qR5tV8xZ1bA4cD7fG9hJ1kM3bN3xP7yGz6hK0jL9mN=
Address = 10.88.0.3/24
# Optional: DNS = 10.88.0.1 # Or another DNS server accessible via VPN

# Peer: Bastion/Jump Server
[Peer]
PublicKey = fG9hJ1kM3bN3xP7yGz6hK0jL9mN2qR5tV8xZ1bA4cD=
# AllowedIPs: Route traffic for VPN subnet and target physical subnet via bastion.
AllowedIPs = 10.88.0.0/24, 10.50.0.0/16
Endpoint = wgjump.dnsif.ca:51820 # Bastion's public address
# Optional: PersistentKeepalive = 25 # Useful if client is also behind NAT
```

**4\. System Configuration:**

**A. Enable IP Forwarding (on `wg-server` AND `wg-bastion`)**

- Edit `/etc/sysctl.conf` or create a file like `/etc/sysctl.d/99-forwarding.conf`:

```
net.ipv4.ip_forward=1
```
- Apply the setting: `sudo sysctl -p` (or reboot).

**B. Open Firewall Port (on `wg-bastion` only)**

- Allow incoming UDP traffic on the port specified in `ListenPort` (e.g., 51820).
- Example (`ufw`): `sudo ufw allow 51820/udp`
- Example (`iptables`): `sudo iptables -A INPUT -p udp --dport 51820 -j ACCEPT` (adjust if needed based on existing rules).

**C. `iptables` Rules (Handled by `PostUp`/`PostDown`)**

- The `PostUp`/`PostDown` lines in the WireGuard configs automatically add/remove necessary `iptables` rules:
    - **`wg-server`:** Enables forwarding and NATs (Masquerades) traffic from VPN clients (`10.88.0.0/24`) going to the physical network via `ens18`.
    - **`wg-bastion`:** Enables forwarding for traffic transiting the `wg0` interface (between peers).

**5\. Starting the Tunnel:**

- On all three machines (server, bastion, client), bring the interface up:

**Bash**

<br>

```
sudo wg-quick up wg0
```
- To make it start automatically on boot (Linux):

**Bash**

<br>

```
sudo systemctl enable wg-quick@wg0
```

**6\. Verification:**

1. **Check Status:** Run `sudo wg show` on all machines. Look for:
    - Peers listed.
    - Recent `latest handshake` times for active connections (client<->bastion, server<->bastion).
    - Correct `endpoint` addresses.
    - Correct `allowed ips`.
2. **Ping Tests:**
    - Client -> Bastion VPN IP (`ping 10.88.0.2`)
    - Client -> Server VPN IP (`ping 10.88.0.1`)
    - Client -> Target Physical Host (`ping 10.50.0.50` or other IP)
    - Bastion -> Server VPN IP (`ping 10.88.0.1`)
    - Bastion -> Target Physical Host (`ping 10.50.0.50`)
