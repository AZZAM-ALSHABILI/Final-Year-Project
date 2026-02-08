# Attack Simulation

This document describes the process for executing simulated attacks against the honeypots to generate realistic log data. All commands are run on the Kali VM.

## Prerequisites

- Network namespaces configured (see `attacker_namespaces.md`)
- Honeypots running and verified (see `deception_verification.md`)
- Kali VM with required tools: nmap, hydra, sshpass, curl, netcat, smbclient

## 3.1 Directory Structure

```
~/fyp/
├── scripts/
│   ├── setup_namespaces.sh    # Network namespace setup
│   ├── test_namespaces.sh     # Connectivity test
│   └── cleanup_namespaces.sh  # Cleanup script
└── attack_scripts/
    ├── run_attacks.sh         # Master orchestration script
    ├── 01_recon/              # Reconnaissance attacks
    │   └── port_scan.sh
    ├── 02_brute_force/        # Credential attacks
    │   ├── ssh_brute.sh
    │   ├── telnet_brute.sh
    │   ├── ftp_brute.sh
    │   ├── smb_brute.sh
    │   └── mysql_brute.sh
    ├── 03_exploitation/       # Exploitation attempts
    │   ├── http_exploit.sh
    │   ├── ftp_exploit.sh
    │   ├── ssh_exploit.sh
    │   ├── smb_exploit.sh
    │   ├── mysql_exploit.sh
    │   └── payload_delivery.sh
    ├── 04_post_access/        # Post-compromise activity
    │   └── insider_threat.sh
    └── 05_multi_stage/        # Multi-phase attacks
        └── attack_chain.sh
```

## 3.2 Attack Phases Overview

| Phase | Namespace | Scripts | Target Activity |
|-------|-----------|---------|-----------------|
| 1. Reconnaissance | `recon` | `port_scan.sh` | Nmap scanning, service enumeration |
| 2. Access Attempts | `bruteforce` | 5 scripts | Hydra credential attacks |
| 3. Exploitation | `exploit` | 6 scripts | Service exploitation, payload delivery |
| 4. Post-Compromise | `postaccess` | `insider_threat.sh` | Post-login commands |
| 5. Multi-Stage | `multistage` | `attack_chain.sh` | Combined attack chain |

## 3.3 Pre-Attack Setup

1. Set up network namespaces:
```bash
cd ~/fyp/scripts
sudo ./setup_namespaces.sh
```

2. Verify connectivity:
```bash
sudo ./test_namespaces.sh
```

3. Ensure SecLists is installed:
```bash
ls /usr/share/seclists
# If not installed: sudo apt install seclists
```

4. Extract rockyou wordlist:
```bash
sudo gunzip /usr/share/wordlists/rockyou.txt.gz
```

## 3.4 Running Attack Simulation

### Full Automated Run

Execute all phases sequentially:

```bash
cd ~/fyp/attack_scripts
sudo ./run_attacks.sh
```

The script runs phases in order with delays between each.

## 3.5 Target Honeypots

| Honeypot | IP Address | Services |
|----------|------------|----------|
| Cowrie | 172.16.0.20 | SSH (22), Telnet (23) |
| Dionaea | 172.16.0.30 | FTP (21), HTTP (80), SMB (445), MySQL (3306) |

## 3.6 Monitoring During Attacks

Monitor honeypot logs in real-time during attacks:

**Cowrie (on Cowrie VM):**
```bash
tail -f ~/cowrie/var/log/cowrie/cowrie.json | jq .
```

**Dionaea (on Dionaea VM):**
```bash
tail -f /opt/dionaea/var/log/dionaea/dionaea.json
```

## 3.7 Post-Attack Verification

After running attacks, verify logs were generated:

**Cowrie:**
```bash
wc -l ~/cowrie/var/log/cowrie/cowrie.json.*
```

**Dionaea:**
```bash
sqlite3 /opt/dionaea/var/lib/dionaea/dionaea.sqlite "SELECT COUNT(*) FROM connections;"
```

## 3.8 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Namespaces not set up" | Run `sudo ./setup_namespaces.sh` first |
| "SecLists not found" | Install with `sudo apt install seclists` |
| Connection timeout | Check honeypot services are running |
| Permission denied | Ensure scripts are executable: `chmod +x *.sh` |

## Notes

- Each namespace represents a distinct attacker with unique IP address
- Scripts are designed to generate varied attack patterns for analysis
- Attack intensity is controlled to avoid overloading honeypots
- Full source code available in project GitHub repository (see Appendix)

