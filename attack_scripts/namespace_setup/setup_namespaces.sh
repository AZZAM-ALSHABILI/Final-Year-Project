#!/bin/bash
# Network Namespaces for Attack Phase Simulation
# Maps to Cyberattack Lifecycle: Recon → Access → Exploit → Post-Compromise

if [[ $EUID -ne 0 ]]; then
    echo "Error: Run with sudo"
    exit 1
fi

IFACE="eth0"

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
