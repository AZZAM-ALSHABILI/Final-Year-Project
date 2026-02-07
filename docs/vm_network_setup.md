# VirtualBox and Network Setup

This guide covers creating virtual machines and configuring networking for the honeypot.

## Prerequisites

- Oracle VirtualBox installed on host system
- Ubuntu Server 22.04 LTS ISO
- Kali Linux 2024 ISO

## Software Versions

| Software | Version | Notes |
|----------|---------|-------|
| Oracle VirtualBox | 7.0.x | With Extension Pack |
| Ubuntu Server | 22.04.3 LTS | Cowrie, Dionaea, Analysis VMs |
| Kali Linux | 2024.1 | Attacker VM |
| Host OS | Windows 10/11 | Development environment |

## Part 1: VirtualBox Network Configuration

Open VirtualBox and navigate to File → Tools → Network Manager.

### Create NAT Network

Click the NAT Networks tab, then Create:

```
Name: HoneypotNAT
IPv4 Prefix: 10.0.2.0/24
Enable DHCP: Yes
```

### Create Host-Only Network

Click the Host-only Networks tab, then Create:

```
Name: VirtualBox Host-Only Ethernet Adapter
IPv4 Address: 192.168.56.1
IPv4 Network Mask: 255.255.255.0
DHCP Server: Disabled
```

The Internal Network is created automatically when assigned to a VM.

## Part 2: Virtual Machine Creation

Create four virtual machines:

### Kali Linux VM (Attacker)

```
Name: kali-attacker
Type: Linux
Version: Debian (64-bit)
RAM: 4096 MB
CPU Cores: 2
Disk: 40 GB (dynamically allocated)
```

### Cowrie Honeypot VM

```
Name: cowrie-honeypot
Type: Linux
Version: Ubuntu (64-bit)
RAM: 2048 MB
CPU Cores: 2
Disk: 20 GB (dynamically allocated)
```

### Dionaea Honeypot VM

```
Name: dionaea-honeypot
Type: Linux
Version: Ubuntu (64-bit)
RAM: 2048 MB
CPU Cores: 2
Disk: 20 GB (dynamically allocated)
```

### Analysis VM

```
Name: analysis-machine
Type: Linux
Version: Ubuntu (64-bit)
RAM: 8192 MB
CPU Cores: 4
Disk: 30 GB (dynamically allocated)
```

## Part 3: Network Adapter Configuration

For each VM, configure three network adapters:

### Adapter 1: NAT Network

```
Attached to: NAT Network
Name: HoneypotNAT
```

### Adapter 2: Host-Only Adapter

```
Attached to: Host-only Adapter
Name: VirtualBox Host-Only Ethernet Adapter
```

### Adapter 3: Internal Network

```
Attached to: Internal Network
Name: honeypot-internal
```

## Part 4: Operating System Installation

Install Ubuntu Server on Cowrie, Dionaea, and Analysis VMs. Install Kali Linux on the attacker VM using default options.

## Part 5: Static IP Configuration

### Ubuntu Servers (Netplan)

Edit `/etc/netplan/00-installer-config.yaml`:

**Cowrie honeypot:**

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: true
    enp0s8:
      addresses:
        - 192.168.56.20/24
    enp0s9:
      addresses:
        - 172.16.0.20/24
```

**Dionaea honeypot:**

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: true
    enp0s8:
      addresses:
        - 192.168.56.30/24
    enp0s9:
      addresses:
        - 172.16.0.30/24
```

**Analysis machine:**

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: true
    enp0s8:
      addresses:
        - 192.168.56.40/24
    enp0s9:
      addresses:
        - 172.16.0.40/24
```

Apply with:

```bash
sudo netplan apply
```

### Kali Linux (NetworkManager)

```bash
# Host-Only interface
sudo nmcli connection add type ethernet con-name "host-only" ifname eth1
sudo nmcli connection modify "host-only" ipv4.addresses 192.168.56.10/24
sudo nmcli connection modify "host-only" ipv4.method manual
sudo nmcli connection up "host-only"

# Internal interface
sudo nmcli connection add type ethernet con-name "internal" ifname eth2
sudo nmcli connection modify "internal" ipv4.addresses 172.16.0.10/24
sudo nmcli connection modify "internal" ipv4.method manual
sudo nmcli connection up "internal"
```

Verify:

```bash
nmcli connection show
ip a
```

## IP Address Summary

| VM | Host-Only IP | Internal IP |
|-----|--------------|-------------|
| Kali (Attacker) | 192.168.56.10 | 172.16.0.10 |
| Cowrie | 192.168.56.20 | 172.16.0.20 |
| Dionaea | 192.168.56.30 | 172.16.0.30 |
| Analysis | 192.168.56.40 | 172.16.0.40 |

## Time Synchronization

Configure NTP on all VMs:

```bash
sudo apt install systemd-timesyncd -y
sudo timedatectl set-ntp true
timedatectl
```

## Shared Folder Configuration

1. Create folder on Windows host:

```powershell
New-Item -ItemType Directory -Force -Path "C:\Users\<username>\Desktop\fyp_shared"
```

2. In VirtualBox → Analysis VM → Settings → Shared Folders:

```
Folder Path: C:\Users\<username>\Desktop\fyp_shared
Folder Name: fyp_shared
Auto-mount: Checked
Mount point: /home/<username>/fyp_shared
```

3. Enable access on Analysis VM:

```bash
sudo usermod -aG vboxsf $USER
sudo reboot
```


