# Attacker Network Namespaces

This guide configures network namespaces on Kali to simulate multiple distinct attackers representing different phases of the cyberattack lifecycle.

## Prerequisites

1. Shut down Kali VM
2. Open VM Settings → Network → Adapter 3 (Internal Network)
3. Expand Advanced → Set Promiscuous Mode to "Allow All"
4. Start Kali VM

## Namespace Overview

| Namespace | IP Address | Attack Phase | Description |
|-----------|------------|--------------|-------------|
| recon | 172.16.0.101 | Reconnaissance | Port scanning, service enumeration |
| bruteforce | 172.16.0.102 | Access Attempts | Credential attacks (SSH, FTP, SMB) |
| exploit | 172.16.0.103 | Exploitation | Metasploit, payload delivery |
| postaccess | 172.16.0.104 | Post-Compromise | Post-login commands, data harvesting |
| multistage | 172.16.0.105 | Full Chain | Combined multi-stage attacks |

## Notes

- Namespaces do not persist after reboot
- Run setup script before each attack session
- Each namespace has a unique MAC address
- Promiscuous mode is required for VirtualBox to pass traffic
- Names map directly to cyberattack lifecycle phases for analysis clarity

- **Interface Note:** Verify your internal interface name with `ip a` (eth0, eth1, or eth2)


## Setup Script

Create the script:

```bash
mkdir -p ~/fyp/scripts
nano ~/fyp/scripts/setup_namespaces.sh
```

Content:

```bash
#!/bin/bash
# Network Namespaces for Attack Phase Simulation
# Maps to Cyberattack Lifecycle: Recon → Access → Exploit → Post-Compromise

if [[ $EUID -ne 0 ]]; then
    echo "Error: Run with sudo"
    exit 1
fi

IFACE="eth2"

# Clean up existing namespaces
for ns in recon bruteforce exploit postaccess multistage; do
    ip netns del "$ns" 2>/dev/null
    ip link del "mv-$ns" 2>/dev/null
done

# Enable promiscuous mode
ip link set "$IFACE" promisc on

echo "Creating attack phase namespaces..."
echo ""

# Phase 1: Reconnaissance
ip netns add recon
ip link add mv-recon link $IFACE type macvlan mode bridge
ip link set mv-recon netns recon
ip netns exec recon ip addr add 172.16.0.101/24 dev mv-recon
ip netns exec recon ip link set mv-recon up
ip netns exec recon ip link set lo up
echo "  [RECON]      172.16.0.101 - Port scanning, enumeration"

# Phase 2: Access Attempts (Brute-Force)
ip netns add bruteforce
ip link add mv-bruteforce link $IFACE type macvlan mode bridge
ip link set mv-bruteforce netns bruteforce
ip netns exec bruteforce ip addr add 172.16.0.102/24 dev mv-bruteforce
ip netns exec bruteforce ip link set mv-bruteforce up
ip netns exec bruteforce ip link set lo up
echo "  [BRUTEFORCE] 172.16.0.102 - Credential attacks"

# Phase 3: Exploitation
ip netns add exploit
ip link add mv-exploit link $IFACE type macvlan mode bridge
ip link set mv-exploit netns exploit
ip netns exec exploit ip addr add 172.16.0.103/24 dev mv-exploit
ip netns exec exploit ip link set mv-exploit up
ip netns exec exploit ip link set lo up
echo "  [EXPLOIT]    172.16.0.103 - Metasploit, payloads"

# Phase 4: Post-Compromise
ip netns add postaccess
ip link add mv-postaccess link $IFACE type macvlan mode bridge
ip link set mv-postaccess netns postaccess
ip netns exec postaccess ip addr add 172.16.0.104/24 dev mv-postaccess
ip netns exec postaccess ip link set mv-postaccess up
ip netns exec postaccess ip link set lo up
echo "  [POSTACCESS] 172.16.0.104 - Post-login activity"

# Multi-Stage Attacker
ip netns add multistage
ip link add mv-multistage link $IFACE type macvlan mode bridge
ip link set mv-multistage netns multistage
ip netns exec multistage ip addr add 172.16.0.105/24 dev mv-multistage
ip netns exec multistage ip link set mv-multistage up
ip netns exec multistage ip link set lo up
echo "  [MULTISTAGE] 172.16.0.105 - Combined attacks"

echo ""
echo "Done. Usage: sudo ip netns exec <namespace> <command>"
echo "Example: sudo ip netns exec recon nmap -sV 172.16.0.20"
```

Make executable:

```bash
chmod +x ~/fyp/scripts/setup_namespaces.sh
```

## Running the Setup

```bash
cd ~/fyp/scripts
sudo ./setup_namespaces.sh
```

Expected output:

```
Creating attack phase namespaces...

  [RECON]      172.16.0.101 - Port scanning, enumeration
  [BRUTEFORCE] 172.16.0.102 - Credential attacks
  [EXPLOIT]    172.16.0.103 - Metasploit, payloads
  [POSTACCESS] 172.16.0.104 - Post-login activity
  [MULTISTAGE] 172.16.0.105 - Combined attacks

Done. Usage: sudo ip netns exec <namespace> <command>
Example: sudo ip netns exec recon nmap -sV 172.16.0.20
```

## Verification

List namespaces:

```bash
ip netns list
```

Expected:
```
multistage
postaccess
exploit
bruteforce
recon
```

Test connectivity:

```bash
sudo ip netns exec recon ping -c 1 172.16.0.20
sudo ip netns exec recon ping -c 1 172.16.0.30
```

## Usage Examples

```bash
# Reconnaissance: Port scanning
sudo ip netns exec recon nmap -sV 172.16.0.20
sudo ip netns exec recon nmap -sS -p- 172.16.0.30

# Brute-Force: Credential attacks
sudo ip netns exec bruteforce hydra -L users.txt -P pass.txt ssh://172.16.0.20
sudo ip netns exec bruteforce hydra -L users.txt -P pass.txt ftp://172.16.0.30

# Exploitation: Metasploit
sudo ip netns exec exploit msfconsole

# Post-Access: SSH login and commands
sudo ip netns exec postaccess ssh root@172.16.0.20

# Multi-Stage: Full attack chain
sudo ip netns exec multistage nmap -sV 172.16.0.20 && \
sudo ip netns exec multistage hydra -l root -p root ssh://172.16.0.20
```

## Helper Scripts

### Test Script (`test_namespaces.sh`)

```bash
#!/bin/bash
# test_namespaces.sh - Test connectivity from each namespace

if [[ $EUID -ne 0 ]]; then
    echo "Error: Run with sudo"
    exit 1
fi

COWRIE="172.16.0.20"
DIONAEA="172.16.0.30"

echo "Testing namespace connectivity..."
echo ""

for ns in recon bruteforce exploit postaccess multistage; do
    if ! ip netns list | grep -q "^$ns"; then
        echo "$ns: NOT FOUND"
        continue
    fi

    # Test Cowrie
    if ip netns exec "$ns" ping -c 1 -W 2 "$COWRIE" >/dev/null 2>&1; then
        cowrie_status="OK"
    else
        cowrie_status="FAIL"
    fi

    # Test Dionaea
    if ip netns exec "$ns" ping -c 1 -W 2 "$DIONAEA" >/dev/null 2>&1; then
        dionaea_status="OK"
    else
        dionaea_status="FAIL"
    fi
    echo "$ns: Cowrie=$cowrie_status, Dionaea=$dionaea_status"
done

echo ""
echo "Done."
```

### Cleanup Script (`cleanup_namespaces.sh`)

```bash
#!/bin/bash
# cleanup_namespaces.sh - Remove all namespaces

if [[ $EUID -ne 0 ]]; then
    echo "Error: Run with sudo"
    exit 1
fi

echo "Removing namespaces..."

for ns in recon bruteforce exploit postaccess multistage; do
    if ip netns list | grep -q "^$ns"; then
        ip netns del "$ns"
        ip link del "mv-$ns" 2>/dev/null
        echo "  Removed $ns"
    fi
done

echo "Done."
```
