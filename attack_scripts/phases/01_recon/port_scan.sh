#!/bin/bash
# Reconnaissance - host discovery and port scanning

SUBNET="172.16.0.0/24"
LOGDIR="/home/kali/Desktop/fyp/attack_scripts/logs/recon"
TARGETS="$LOGDIR/discovered_targets.txt"

mkdir -p "$LOGDIR"

echo "Starting recon on $SUBNET"

nmap -sn $SUBNET -oG "$LOGDIR/host_discovery.txt"
grep "Up" "$LOGDIR/host_discovery.txt" | awk '{print $2}' | grep -vE "172.16.0.(1|10|101|102|103|104|105)$" > "$TARGETS"

echo "Found hosts:"
cat "$TARGETS"

while read -r target; do
    echo "Scanning $target"
    nmap -sV -p 21,22,23,80,445,3306 "$target" -oN "$LOGDIR/portscan_${target}.txt"
    nmap -A -T4 --top-ports 100 "$target" -oN "$LOGDIR/fullscan_${target}.txt"
    nmap -sV --script=banner -p 21,22,23,80,445,3306 "$target" -oN "$LOGDIR/banners_${target}.txt" 2>/dev/null
    nmap --script=ssh-hostkey -p 22,23 "$target" -oN "$LOGDIR/ssh_${target}.txt" 2>/dev/null
    nmap --script=http-title -p 80 "$target" -oN "$LOGDIR/http_${target}.txt" 2>/dev/null
    nmap --script=smb-os-discovery -p 445 "$target" -oN "$LOGDIR/smb_${target}.txt" 2>/dev/null
    nmap --script=ftp-anon -p 21 "$target" -oN "$LOGDIR/ftp_${target}.txt" 2>/dev/null
    nmap --script=mysql-info -p 3306 "$target" -oN "$LOGDIR/mysql_${target}.txt" 2>/dev/null
done < "$TARGETS"

echo "Recon done"
