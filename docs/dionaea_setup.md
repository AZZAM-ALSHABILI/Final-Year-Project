# Dionaea Honeypot Setup

This guide covers installing Dionaea multi-protocol honeypot using Docker on Ubuntu Server.

All commands are run on the Dionaea honeypot VM.

## Install Docker

```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
```

## Add User to Docker Group

```bash
sudo usermod -aG docker $USER
```

Log out and log back in for group changes to take effect.

## Create Directories for Persistent Storage

```bash
sudo mkdir -p /opt/dionaea/var/log/dionaea
sudo mkdir -p /opt/dionaea/var/lib/dionaea
sudo chown -R $USER:$USER /opt/dionaea
```

## Pull and Run Dionaea Container

```bash
docker pull dinotools/dionaea:latest

docker run -d \
  --name dionaea \
  --network host \
  -v /opt/dionaea/var/log/dionaea:/opt/dionaea/var/log/dionaea \
  -v /opt/dionaea/var/lib/dionaea:/opt/dionaea/var/lib/dionaea \
  dinotools/dionaea:latest
```

## Verify Dionaea is Running

```bash
docker ps
```

Check services:

```bash
ss -tlnp | grep -E "21|80|445|3306"
```

## Testing

From Kali, scan Dionaea:

```bash
nmap -p 21,80,445,3306 172.16.0.30
```

All ports should show as open.

Verify connections are logged in SQLite:

```bash
sqlite3 /opt/dionaea/var/lib/dionaea/dionaea.sqlite "SELECT connection, connection_type, remote_host, local_port FROM connections ORDER BY connection_timestamp DESC LIMIT 5;"
```

Expected output should show `remote_host` as `172.16.0.x` (your namespace IPs), confirming source IP preservation.

## Troubleshooting

If ports not listening:

```bash
docker logs dionaea
```

## Target Protocols

> **Note:** Dionaea supports many protocols, but this experiment focuses on four core protocols to ensure clean, focused data for analysis.

| Port | Protocol | Attack Coverage |
|------|----------|-----------------|
| 21 | FTP | Brute-force + Anonymous login |
| 80 | HTTP | Web exploitation, payload delivery |
| 445 | SMB | EternalBlue, share enumeration |
| 3306 | MySQL | Database brute-force |

## Network Mode Explanation

This setup uses `--network host` instead of port mapping (`-p`).

**Why this matters:**
- Port mapping (`-p 80:80`) would mask source IPs as Docker gateway (172.17.0.x)
- Host networking shares the VM's network stack directly
- Source IPs (172.16.0.101-105) are preserved in logs
- Essential for source diversity analysis in Phase 5
