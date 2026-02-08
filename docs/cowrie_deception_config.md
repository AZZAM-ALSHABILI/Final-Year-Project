# Cowrie Deception Configuration

This guide configures Cowrie to present a convincing fake enterprise server environment using the "Nextera Tech Solutions" theme.

All commands are run on the Cowrie VM as the cowrie user.

```bash
sudo su - cowrie
cd ~/cowrie
source cowrie-env/bin/activate
```

## 13.1 Configure SSH Banners

Create the pre-login banner:

```bash
cat > honeyfs/etc/issue.net << 'EOF'
================================================================
                 NEXTERA TECH SOLUTIONS
              Enterprise Technology Systems
================================================================
AUTHORIZED ACCESS ONLY - All activity is monitored and logged

System: NXTR-PROD-SSH01.internal.nextera.local
Contact: security@nextera-tech.local (internal only)

WARNING: Unauthorized access is prohibited and may be prosecuted
================================================================
EOF
```

Create the post-login MOTD:

```bash
cat > honeyfs/etc/motd << 'EOF'
Welcome to NXTR-PROD-SSH01

Nextera Tech Solutions - Internal Server
Last login: Mon Jan 27 08:15:23 2026 from 192.168.1.45

* Server maintenance window: Sunday 02:00-04:00 SGT
* Report issues to: helpdesk@nextera-tech.local
* Production environment - changes require approval
EOF
```

Create the hostname file:

```bash
echo "NXTR-PROD-SSH01" > honeyfs/etc/hostname
```

Update cowrie.cfg:

```bash
nano etc/cowrie.cfg
```

```ini
[honeypot]
hostname = NXTR-PROD-SSH01
kernel_version = 5.15.0-91-generic
kernel_build_string = #101-Ubuntu SMP Tue Nov 14 13:30:08 UTC 2023
hardware_platform = x86_64
operating_system = GNU/Linux
```

## 13.2 Configure User Accounts

Create the passwd file:

```bash
cat > honeyfs/etc/passwd << 'EOF'
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:Backup Service:/var/backups:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
sysadmin:x:1000:1000:System Administrator:/home/sysadmin:/bin/bash
admin:x:1001:1001:NXTR Admin:/home/admin:/bin/bash
jsmith:x:1002:1002:John Smith - Engineering:/home/jsmith:/bin/bash
mchen:x:1003:1003:Michelle Chen - Finance:/home/mchen:/bin/bash
agarcia:x:1004:1004:Ana Garcia - HR:/home/agarcia:/bin/bash
dkumar:x:1005:1005:Dev Kumar - Development:/home/dkumar:/bin/bash
monitor:x:1006:1006:Monitoring Service:/home/monitor:/bin/bash
deploy:x:1007:1007:Deployment Service:/home/deploy:/bin/bash
oracle:x:1100:1100:Oracle Database:/opt/oracle:/bin/bash
postgres:x:1101:1101:PostgreSQL:/var/lib/postgresql:/bin/bash
mysql:x:1102:1102:MySQL Server:/var/lib/mysql:/bin/false
test:x:9999:9999:Test Account:/home/test:/bin/bash
EOF
```

Create the shadow file:

```bash
cat > honeyfs/etc/shadow << 'EOF'
root:$6$rounds=5000$saltsalt$hashedpassword:19500:0:99999:7:::
daemon:*:19500:0:99999:7:::
bin:*:19500:0:99999:7:::
sys:*:19500:0:99999:7:::
sync:*:19500:0:99999:7:::
www-data:*:19500:0:99999:7:::
backup:$6$nxtr2024$BackupServiceHash:19500:0:99999:7:::
nobody:*:19500:0:99999:7:::
sysadmin:$6$nxtr2024$SysAdminSecure:19580:0:99999:7:::
admin:$6$nxtr2024$AdminNexTera2024:19580:0:99999:7:::
jsmith:$6$nxtr2024$JSmithEngr2024:19550:0:99999:7:::
mchen:$6$nxtr2024$MChenFinance:19560:0:99999:7:::
agarcia:$6$nxtr2024$AGarciaHR2024:19570:0:99999:7:::
dkumar:$6$nxtr2024$DKumarDev2024:19575:0:99999:7:::
monitor:$6$nxtr2024$MonitorSvc:19500:0:99999:7:::
deploy:$6$nxtr2024$DeploySvc2024:19500:0:99999:7:::
oracle:$6$nxtr2024$OracleDB2024:19400:0:99999:7:::
postgres:$6$nxtr2024$PostgresDB:19400:0:99999:7:::
mysql:*:19400:0:99999:7:::
test:$6$nxtr2024$TestAccount123:19600:0:99999:7:::
EOF
```

Create the group file:

```bash
cat > honeyfs/etc/group << 'EOF'
root:x:0:
daemon:x:1:
bin:x:2:
sys:x:3:
adm:x:4:sysadmin,admin
www-data:x:33:
backup:x:34:backup
sudo:x:27:sysadmin,admin
users:x:100:jsmith,mchen,agarcia,dkumar,test
sysadmin:x:1000:
admin:x:1001:
engineering:x:2000:jsmith,dkumar
finance:x:2001:mchen
hr:x:2002:agarcia
it:x:2003:sysadmin,admin,monitor
devops:x:2004:deploy,dkumar
dba:x:2005:oracle,postgres,mysql
nextera:x:3000:admin,sysadmin,jsmith,mchen,agarcia,dkumar
EOF
```

## 13.3 Configure Login Credentials

Edit userdb.txt:

```bash
cat > etc/userdb.txt << 'EOF'
# Nextera Tech Solutions - SSH Credentials

# Deny honeypot detection attempts
root:x:!root
root:x:!123456
root:x:!password
root:x:!/honeypot/i
root:x:!/cowrie/i
*:x:!/test/i

# Nextera employee accounts with specific passwords
admin:x:NxtrAdmin2024
admin:x:Admin@2024
sysadmin:x:SysAdmin#2024
sysadmin:x:Nextera2024
jsmith:x:JSmith@2024
jsmith:x:Engineering1
mchen:x:Finance2024
agarcia:x:HRAccess2024
dkumar:x:DevOps@2024
test:x:Test@123
test:x:test123

# Root access with common passwords
root:x:admin
root:x:toor
root:x:password123

# Fallback weak passwords
*:x:123456
*:x:password
*:x:admin
*:x:root
*:x:qwerty
*:x:letmein

# Catch-all
*:x:*
EOF
```

## 13.4 Configure Network Files

Create the hosts file:

```bash
cat > honeyfs/etc/hosts << 'EOF'
127.0.0.1       localhost
127.0.1.1       NXTR-PROD-SSH01

# Nextera Tech Internal Network
172.16.0.20     NXTR-PROD-SSH01 ssh01 ssh01.internal.nextera.local
172.16.0.30     NXTR-PROD-WEB01 web01 web01.internal.nextera.local
172.16.0.50     NXTR-DB-01 db01 oracle.internal.nextera.local
172.16.0.51     NXTR-DB-02 db02 postgres.internal.nextera.local
172.16.0.60     NXTR-FILE-01 file01 fileserver.internal.nextera.local
172.16.0.100    NXTR-DC-01 dc01 ldap.internal.nextera.local
192.168.1.1     gateway.nextera.local gateway

# External services
10.10.10.5      backup.nextera.local backup-server
EOF
```

Create resolv.conf:

```bash
cat > honeyfs/etc/resolv.conf << 'EOF'
# Nextera Tech Internal DNS
nameserver 172.16.0.100
nameserver 8.8.8.8
search internal.nextera.local nextera.local
domain nextera.local
EOF
```

## 13.5 Configure System Information

```bash
mkdir -p honeyfs/proc/net
```

Create cpuinfo:

```bash
cat > honeyfs/proc/cpuinfo << 'EOF'
processor       : 0
vendor_id       : GenuineIntel
cpu family      : 6
model           : 85
model name      : Intel(R) Xeon(R) Gold 6248 CPU @ 2.50GHz
stepping        : 7
cpu MHz         : 2500.000
cache size      : 28160 KB
physical id     : 0
siblings        : 4
core id         : 0
cpu cores       : 4
bogomips        : 5000.00
flags           : fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss ht syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon rep_good nopl
EOF
```

Create meminfo:

```bash
cat > honeyfs/proc/meminfo << 'EOF'
MemTotal:       16384000 kB
MemFree:         8234567 kB
MemAvailable:   12456789 kB
Buffers:          234567 kB
Cached:          3456789 kB
SwapTotal:       4194304 kB
SwapFree:        4194304 kB
EOF
```

Create version:

```bash
cat > honeyfs/proc/version << 'EOF'
Linux version 5.15.0-91-generic (buildd@nextera-build01) (gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0, GNU ld (GNU Binutils for Ubuntu) 2.38) #101-Ubuntu SMP Tue Nov 14 13:30:08 UTC 2023
EOF
```

Create ARP table:

```bash
cat > honeyfs/proc/net/arp << 'EOF'
IP address       HW type     Flags       HW address            Mask     Device
172.16.0.1       0x1         0x2         00:50:56:c0:00:08     *        eth0
172.16.0.30      0x1         0x2         08:00:27:ab:cd:02     *        eth0
172.16.0.50      0x1         0x2         08:00:27:ab:cd:05     *        eth0
192.168.56.1     0x1         0x2         0a:00:27:00:00:00     *        eth1
EOF
```

## 13.6 Create Trap Files

Create directory structure:

```bash
mkdir -p honeyfs/home/admin/{scripts,.ssh,.config}
mkdir -p honeyfs/home/sysadmin/{tools,.ssh}
mkdir -p honeyfs/home/jsmith/{projects,.ssh}
mkdir -p honeyfs/home/mchen/reports
mkdir -p honeyfs/home/agarcia/documents
mkdir -p honeyfs/home/dkumar/code
mkdir -p honeyfs/home/test
mkdir -p honeyfs/opt/nextera/{config,bin,logs,backup}
mkdir -p honeyfs/var/www/html/portal
mkdir -p honeyfs/tmp/systemd-private-abc123
```

Create admin notes (credential trap):

```bash
cat > honeyfs/home/admin/notes.txt << 'EOF'
=== Server Access Notes ===
Updated: 2026-01-15

Production Database:
  Host: db01.internal.nextera.local (172.16.0.50)
  User: nxtr_admin
  Pass: NxtrDB@2024!

Backup Server:
  Host: backup.nextera.local
  SSH Key: /home/admin/.ssh/backup_key
  Passphrase: BackupNexTera#2024

Web Portal Admin:
  URL: http://web01.internal.nextera.local/admin
  User: portal_admin
  Pass: PortalNxtr2024

TODO:
- Change test account password (currently: Test@123)
- Rotate MySQL credentials next month
- Update Oracle listener config
EOF
```

Create backup script:

```bash
cat > honeyfs/home/admin/scripts/backup.sh << 'EOF'
#!/bin/bash
# Nextera Backup Script
# Cron: 0 2 * * * /home/admin/scripts/backup.sh

DB_USER="backup_admin"
DB_PASS="BackupNxtr#2024"
BACKUP_DIR="/opt/nextera/backup"

mysqldump -u $DB_USER -p$DB_PASS nextera_prod > $BACKUP_DIR/mysql_$(date +%Y%m%d).sql
pg_dump -U nxtr_backup nextera_prod > $BACKUP_DIR/pg_$(date +%Y%m%d).sql

# Sync to remote
rsync -avz $BACKUP_DIR/ backup@backup.nextera.local:/backups/
EOF
```

Create SSH config:

```bash
cat > honeyfs/home/admin/.ssh/config << 'EOF'
Host db01
    HostName 172.16.0.50
    User oracle
    IdentityFile ~/.ssh/id_rsa

Host db02
    HostName 172.16.0.51
    User postgres
    IdentityFile ~/.ssh/id_rsa

Host backup
    HostName 10.10.10.5
    User backup
    IdentityFile ~/.ssh/backup_key

Host web01
    HostName 172.16.0.30
    User deploy
    ProxyJump admin@172.16.0.20
EOF
```

Create fake SSH private key:

```bash
cat > honeyfs/home/admin/.ssh/id_rsa << 'EOF'
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACBHK9toNqPcH7fpQnP9bLt/LCyZTSFmNxBLsVmNbQAAACDe1Fake1KeyAAA
AAtzc2gtZWQyNTUxOQAAACBHK9toNqPcH7fpQnP9bLt/LCyZTSFmNxBLsVmNbQAAAEBo
cml2YXRlS2V5RGF0YUhlcmVJc0Zha2VBbmROb3RSZWFsAAAAE2FkbWluQE5YVFItUFJPRC
1TU0gwMQECAwQF
-----END OPENSSH PRIVATE KEY-----
EOF
```

Create credentials backup:

```bash
cat > honeyfs/home/admin/.config/credentials.bak << 'EOF'
# Backup before AD migration - DELETE AFTER TESTING
# Created: 2026-01-08

ORACLE_PROD: nxtr_admin / OracleProd@2024!
POSTGRES_DEV: dev_user / DevPostgres#2024
LDAP_BIND: cn=admin,dc=nextera / LdapBind@Nextera
AWS_ACCESS_KEY: AKIA3NEXTERA7EXAMPLE
AWS_SECRET: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
EOF
```

Create database config:

```bash
cat > honeyfs/opt/nextera/config/db.conf << 'EOF'
# Nextera Tech Database Configuration
# Last updated: 2026-01-10

[oracle]
host = 172.16.0.50
port = 1521
service = NXTRPROD
user = nxtr_app
password = OracleNxtr2024!

[postgresql]
host = 172.16.0.51
port = 5432
database = nextera_prod
user = nxtr_read
password = PgNexTera#2024

[mysql]
host = localhost
port = 3306
database = nextera_web
user = web_user
password = WebMySQL2024
EOF
```

Create development code config:

```bash
cat > honeyfs/home/dkumar/code/config.py << 'EOF'
# Nextera Application Config
# TODO: Move to environment variables

DATABASE_URL = "postgresql://app_user:AppDB2024!@db02:5432/nextera_app"
SECRET_KEY = "nxtr-secret-key-do-not-share-2024"
API_KEY = "sk-nxtr-api-1a2b3c4d5e6f7g8h"

REDIS_HOST = "localhost"
REDIS_PASSWORD = "RedisNxtr#2024"
EOF
```

Create HR employee data:

```bash
cat > honeyfs/home/agarcia/documents/employees.csv << 'EOF'
employee_id,name,email,department,hire_date,salary
1001,John Smith,jsmith@nextera-tech.local,Engineering,2020-03-15,85000
1002,Michelle Chen,mchen@nextera-tech.local,Finance,2019-08-22,78000
1003,Ana Garcia,agarcia@nextera-tech.local,HR,2021-01-10,72000
1004,Dev Kumar,dkumar@nextera-tech.local,Development,2022-06-01,92000
1005,Admin User,admin@nextera-tech.local,IT,2018-01-01,95000
EOF
```

Create finance payroll:

```bash
cat > honeyfs/home/mchen/reports/Q4_payroll.txt << 'EOF'
Nextera Tech Solutions - Q4 2025 Payroll Summary
CONFIDENTIAL - Internal Use Only

Department Budgets:
- Engineering: $450,000
- Finance: $180,000
- HR: $120,000
- IT Operations: $320,000

Vendor Payment Portal: https://payments.nextera-tech.local
Admin: finance_admin / FinanceNxtr2025!
EOF
```

Create .htpasswd:

```bash
cat > honeyfs/var/www/html/.htpasswd << 'EOF'
admin:$apr1$xyz123$hashedpasswordhere
portal_admin:$apr1$abc456$anotherhashedpass
jsmith:$apr1$def789$johnsmithpassword
EOF
```

## 13.7 Create Bash Histories

```bash
cat > honeyfs/home/admin/.bash_history << 'EOF'
ssh db01.internal.nextera.local
mysql -u root -p'NxtrMySQL2024'
cat /opt/nextera/config/db.conf
sudo systemctl restart nginx
tail -f /var/log/auth.log
scp backup@backup.nextera.local:/backups/db_dump.sql .
cd /opt/nextera/backup
./backup.sh --full
cat /etc/shadow
passwd jsmith
exit
EOF

cat > honeyfs/home/sysadmin/.bash_history << 'EOF'
tail -f /var/log/auth.log
netstat -tlnp
ps aux | grep nginx
ssh admin@web01
cat /etc/shadow
systemctl restart sshd
iptables -L -n
df -h
free -m
exit
EOF

cat > honeyfs/home/jsmith/.bash_history << 'EOF'
cd projects
git pull origin main
python manage.py runserver
ssh db01
cat /opt/nextera/config/db.conf
sudo systemctl status nginx
exit
EOF

cat > honeyfs/home/dkumar/.bash_history << 'EOF'
cd code
git status
docker ps
kubectl get pods
vim config.py
python3 app.py
ssh deploy@web01
cat ~/.ssh/config
exit
EOF
```

## 13.11 Configure System Logs

```bash
mkdir -p honeyfs/var/log

cat > honeyfs/var/log/auth.log << 'EOF'
Jan 27 08:15:12 NXTR-PROD-SSH01 sshd[12345]: Accepted password for admin from 192.168.1.45 port 49876 ssh2
Jan 27 08:15:12 NXTR-PROD-SSH01 sshd[12345]: pam_unix(sshd:session): session opened for user admin by (uid=0)
Jan 27 13:22:45 NXTR-PROD-SSH01 sshd[12567]: Accepted publickey for sysadmin from 172.16.0.100 port 52341 ssh2
Jan 26 14:30:01 NXTR-PROD-SSH01 sshd[11234]: Accepted password for admin from 192.168.1.45 port 48123 ssh2
Jan 24 09:00:15 NXTR-PROD-SSH01 sshd[10123]: Accepted password for jsmith from 10.0.2.15 port 45678 ssh2
Jan 23 03:45:12 NXTR-PROD-SSH01 sshd[9876]: Failed password for root from 203.0.113.45 port 39876 ssh2
Jan 23 03:45:14 NXTR-PROD-SSH01 sshd[9876]: Failed password for root from 203.0.113.45 port 39876 ssh2
EOF

cat > honeyfs/var/log/cron.log << 'EOF'
Jan 27 02:00:01 NXTR-PROD-SSH01 CRON[23456]: (root) CMD (/home/admin/scripts/backup.sh)
Jan 27 02:00:45 NXTR-PROD-SSH01 CRON[23456]: (root) CMD backup completed successfully
Jan 26 02:00:01 NXTR-PROD-SSH01 CRON[22345]: (root) CMD (/home/admin/scripts/backup.sh)
Jan 26 02:00:38 NXTR-PROD-SSH01 CRON[22345]: (root) CMD backup completed successfully
EOF
```

## 13.12-13.15 Additional Files

Create project README:

```bash
cat > honeyfs/home/jsmith/projects/README.md << 'EOF'
# Nextera Customer Portal
Internal customer portal for Nextera Tech Solutions.
## Development Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
## Database Connection
Uses PostgreSQL on db02.internal.nextera.local
- Database: nextera_portal
- User: portal_app (see config/db.conf for password)
EOF
```

Create server check script:

```bash
cat > honeyfs/home/sysadmin/tools/server_check.sh << 'EOF'
#!/bin/bash
# Server Health Check Script
echo "=== Nextera Server Health Check ==="
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime)"
df -h
free -m
netstat -tlnp 2>/dev/null | head -20
EOF
```

Create healthcheck script:

```bash
cat > honeyfs/opt/nextera/bin/healthcheck.sh << 'EOF'
#!/bin/bash
# Nextera Health Check Service
LOG="/opt/nextera/logs/healthcheck.log"
SLACK_WEBHOOK="https://hooks.slack.com/services/T0XXX/B0XXX/xxxxxxxxxxx"
check_service() {
    if systemctl is-active --quiet $1; then
        echo "[OK] $1 running"
    else
        echo "[FAIL] $1 not running"
    fi
}
echo "=== Health Check $(date) ===" >> $LOG
check_service nginx >> $LOG
check_service postgresql >> $LOG
PGPASSWORD='NxtrDB@2024!' psql -h db01.internal.nextera.local -U nxtr_admin -c "SELECT 1" &>/dev/null
EOF
```

Create .env file:

```bash
cat > honeyfs/home/dkumar/code/.env << 'EOF'
# Development Environment Variables
# DO NOT COMMIT THIS FILE
DATABASE_URL=postgresql://dev_user:DevDB2024!@db02:5432/nextera_dev
REDIS_URL=redis://:RedisNxtr2024@localhost:6379
SECRET_KEY=nxtr-dev-secret-key-change-in-prod
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
STRIPE_SECRET_KEY=sk_test_nextera_payment_key_2024
EOF
```

Create crontab:

```bash
cat > honeyfs/etc/crontab << 'EOF'
# /etc/crontab: system-wide crontab
# Nextera Tech Solutions - Production Server

SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user  command
0 2 * * * root /home/admin/scripts/backup.sh >> /var/log/cron.log 2>&1
0 * * * * root /opt/nextera/bin/healthcheck.sh >> /opt/nextera/logs/healthcheck.log 2>&1
30 3 * * 0 root /opt/nextera/bin/weekly_report.sh
EOF
```

## 13.18 Configure OS and SSH Files

```bash
cat > honeyfs/etc/os-release << 'EOF'
PRETTY_NAME="Debian GNU/Linux 11 (bullseye)"
NAME="Debian GNU/Linux"
VERSION_ID="11"
VERSION="11 (bullseye)"
VERSION_CODENAME=bullseye
ID=debian
EOF

mkdir -p honeyfs/etc/ssh

cat > honeyfs/etc/ssh/sshd_config << 'EOF'
# Nextera Tech Solutions SSH Configuration
Port 22
Protocol 2
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_ed25519_key

PermitRootLogin no
PasswordAuthentication yes
PubkeyAuthentication yes
Banner /etc/issue.net

MaxAuthTries 6
LoginGraceTime 60
EOF
```

## 13.9 Register Files in Filesystem

```bash
python -m cowrie.scripts.fsctl src/cowrie/data/fs.pickle
```

Run in fsctl:

```
# Create directories
mkdir /home/admin
mkdir /home/admin/.ssh
mkdir /home/admin/.config
mkdir /home/admin/scripts
mkdir /home/sysadmin
mkdir /home/sysadmin/.ssh
mkdir /home/sysadmin/tools
mkdir /home/jsmith
mkdir /home/jsmith/projects
mkdir /home/mchen
mkdir /home/mchen/reports
mkdir /home/agarcia
mkdir /home/agarcia/documents
mkdir /home/dkumar
mkdir /home/dkumar/code
mkdir /home/test
mkdir /opt/nextera
mkdir /opt/nextera/config
mkdir /opt/nextera/bin
mkdir /opt/nextera/logs
mkdir /opt/nextera/backup
mkdir /proc/net
mkdir /var/www/html
mkdir /var/www/html/portal

# Add files
touch /home/admin/.bash_history 2048 random
touch /home/admin/notes.txt 1024 random
touch /home/admin/scripts/backup.sh 512 random
touch /home/admin/.ssh/config 512 random
touch /home/admin/.ssh/id_rsa 2048 random
touch /home/admin/.config/credentials.bak 512 random
touch /home/sysadmin/.bash_history 2048 random
touch /home/jsmith/.bash_history 1024 random
touch /home/dkumar/.bash_history 1024 random
touch /home/dkumar/code/config.py 1024 random
touch /home/dkumar/code/.env 512 random
touch /home/agarcia/documents/employees.csv 2048 random
touch /home/mchen/reports/Q4_payroll.txt 1024 random
touch /opt/nextera/config/db.conf 1024 random
touch /var/www/html/.htpasswd 256 random
touch /proc/net/arp 512 random

# Fix permissions
chmod 600 /home/admin/.ssh/id_rsa
chmod 600 /home/admin/.config/credentials.bak
chmod 600 /home/dkumar/code/.env

# Fix ownership
chown 1001 /home/admin
chown 1001 /home/admin/.ssh
chown 1001 /home/admin/.ssh/id_rsa
chown 1000 /home/sysadmin
chown 1002 /home/jsmith
chown 1003 /home/mchen
chown 1004 /home/agarcia
chown 1005 /home/dkumar

exit
```

## Apply and Verify

```bash
bin/cowrie restart
```

Test from Kali:

```bash
ssh admin@172.16.0.20
# Password: NxtrAdmin2024

ls -la /home/
cat /etc/passwd
cat /home/admin/notes.txt
cat /opt/nextera/config/db.conf
exit
```
