#!/bin/bash
# Master script to run all attack phases

SCRIPTS="/home/kali/Desktop/fyp/attack_scripts"
LOGDIR="/home/kali/Desktop/fyp/attack_scripts/logs"

echo "Attack Simulation Started: $(date)"

mkdir -p "$LOGDIR"/{recon,brute_force,exploitation,post_access,opportunist}

# Check namespaces
if ! ip netns list | grep -q "recon"; then
    echo "Namespaces not set up. Run setup_namespaces.sh first"
    exit 1
fi

[ ! -d "/usr/share/seclists" ] && echo "SecLists not found" && exit 1
[ -f "/usr/share/wordlists/rockyou.txt.gz" ] && sudo gunzip /usr/share/wordlists/rockyou.txt.gz

# Phase 1: Reconnaissance
echo ""
echo "=== PHASE 1: RECONNAISSANCE ==="
sudo ip netns exec recon bash "$SCRIPTS/01_recon/port_scan.sh"
sleep 3

# Phase 2: Brute-Force
echo ""
echo "=== PHASE 2: BRUTE-FORCE ==="
sudo ip netns exec bruteforce bash "$SCRIPTS/02_brute_force/ssh_brute.sh"
sudo ip netns exec bruteforce bash "$SCRIPTS/02_brute_force/telnet_brute.sh"
sudo ip netns exec bruteforce bash "$SCRIPTS/02_brute_force/ftp_brute.sh"
sudo ip netns exec bruteforce bash "$SCRIPTS/02_brute_force/smb_brute.sh"
sudo ip netns exec bruteforce bash "$SCRIPTS/02_brute_force/mysql_brute.sh"
sleep 3

# Phase 3: Exploitation
echo ""
echo "=== PHASE 3: EXPLOITATION ==="
sudo ip netns exec exploit bash "$SCRIPTS/03_exploitation/http_exploit.sh"
sudo ip netns exec exploit bash "$SCRIPTS/03_exploitation/ftp_exploit.sh"
sudo ip netns exec exploit bash "$SCRIPTS/03_exploitation/ssh_exploit.sh"
sudo ip netns exec exploit bash "$SCRIPTS/03_exploitation/smb_exploit.sh"
sudo ip netns exec exploit bash "$SCRIPTS/03_exploitation/mysql_exploit.sh"
sudo ip netns exec exploit bash "$SCRIPTS/03_exploitation/payload_delivery.sh"
sleep 3

# Phase 4: Post-Access
echo ""
echo "=== PHASE 4: POST-ACCESS ==="
sudo ip netns exec postaccess bash "$SCRIPTS/04_post_access/insider_threat.sh"
sleep 3

# Phase 5: Multi-Stage
echo ""
echo "=== PHASE 5: MULTI-STAGE ==="
sudo ip netns exec multistage bash "$SCRIPTS/05_multi_stage/attack_chain.sh"

echo ""
echo "Attack Simulation Finished: $(date)"
echo "Logs saved to: $LOGDIR"
