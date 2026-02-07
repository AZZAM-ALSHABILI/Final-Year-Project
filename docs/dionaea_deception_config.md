# Dionaea Deception Configuration

This guide configures Dionaea to present enterprise services matching the "Nextera Tech Solutions" theme.

## Overview

| Protocol | Port | Identity |
|----------|------|----------|
| HTTP | 80 | Nextera Employee Portal |
| FTP | 21 | NXTR-FTP01 File Server |
| SMB | 445 | NXTR-FILE01 Windows Server 2019 |
| MySQL | 3306 | Database Server |

## 14.2 HTTP Portal Configuration

Create HTTP directory structure:

```bash
docker exec dionaea mkdir -p /opt/dionaea/var/lib/dionaea/http/root/assets/js
docker exec dionaea mkdir -p /opt/dionaea/var/lib/dionaea/http/root/admin
docker exec dionaea mkdir -p /opt/dionaea/var/lib/dionaea/http/root/api
docker exec dionaea mkdir -p /opt/dionaea/var/lib/dionaea/http/root/phpmyadmin
docker exec dionaea mkdir -p /opt/dionaea/var/lib/dionaea/http/root/backup
```

Create main login page:

```bash
docker exec dionaea bash -c 'cat > /opt/dionaea/var/lib/dionaea/http/root/index.html << "EOF"
<!DOCTYPE html>
<html>
<head>
    <title>NEXTERA Tech Solutions - Portal</title>
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e, #16213e); color: #fff; height: 100vh; margin: 0; display: flex; justify-content: center; align-items: center; }
        .container { background: rgba(255,255,255,0.1); padding: 40px; border-radius: 10px; text-align: center; width: 350px; }
        h1 { color: #4fc3f7; margin-bottom: 10px; }
        h2 { color: #aaa; font-size: 14px; margin-bottom: 30px; }
        input { width: 100%; padding: 12px; margin: 8px 0; border: none; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #4fc3f7; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        button:hover { background: #29b6f6; }
        .footer { margin-top: 20px; font-size: 12px; color: #666; }
    </style>
    <!-- TODO: Move to production config before go-live -->
    <script src="/assets/js/config.js"></script>
</head>
<body>
    <div class="container">
        <h1>NEXTERA TECH</h1>
        <h2>Enterprise Portal - Authorized Access Only</h2>
        <form action="/api/login" method="POST">
            <input type="text" name="username" placeholder="Employee ID" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Sign In</button>
        </form>
        <div class="footer">
            <p>Nextera Tech Solutions &copy; 2024</p>
            <p>IT Support: helpdesk@nextera-tech.local | x4500</p>
        </div>
    </div>
</body>
</html>
EOF'
```

Create config.js with credentials:

```bash
docker exec dionaea bash -c 'cat > /opt/dionaea/var/lib/dionaea/http/root/assets/js/config.js << "EOF"
// Nextera Portal Configuration
// WARNING: Move sensitive data to environment variables before production!
const CONFIG = {
    API_BASE: "http://api.internal.nextera.local:8080",
    API_KEY: "nxtr-portal-api-key-2024-prod",
    DB_HOST: "db01.internal.nextera.local",
    DB_USER: "portal_app",
    DB_PASS: "PortalDB@2024!",
    REDIS_HOST: "localhost",
    REDIS_PASS: "RedisNxtr#2024",
    JWT_SECRET: "nxtr-jwt-secret-do-not-share-2024",
    ADMIN_EMAIL: "admin@nextera-tech.local"
};
module.exports = CONFIG;
EOF'
```

Create robots.txt:

```bash
docker exec dionaea bash -c 'cat > /opt/dionaea/var/lib/dionaea/http/root/robots.txt << "EOF"
User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /backup/
Disallow: /assets/js/
Disallow: /phpmyadmin/
Disallow: /.git/
Disallow: /internal/
EOF'
```

Create admin console page:

```bash
docker exec dionaea sh -c 'echo "<!DOCTYPE html><html><head><title>NEXTERA Admin Console</title><style>body{font-family:Arial;background:#1a1a2e;color:#fff;padding:20px}h1{color:#4fc3f7}.panel{background:rgba(255,255,255,0.1);padding:20px;margin:10px 0;border-radius:5px}a{color:#4fc3f7}</style></head><body><h1>NEXTERA Admin Console</h1><p>Logged in as: <strong>admin</strong></p><div class=\"panel\"><h3>Quick Links</h3><ul><li><a href=\"/phpmyadmin/\">Database Admin (phpMyAdmin)</a></li><li><a href=\"/api/users\">User Management API</a></li><li><a href=\"/assets/js/config.js\">Portal Configuration</a></li><li><a href=\"/backup/\">Backup Files</a></li></ul></div><div class=\"panel\"><h3>System Status</h3><p>Database: <span style=\"color:green\">Connected</span></p><p>Last Backup: 2026-01-28 02:00:00</p></div></body></html>" > /opt/dionaea/var/lib/dionaea/http/root/admin/index.html'
```

Create API response pages:

```bash
docker exec dionaea sh -c 'echo "<!DOCTYPE html><html><head><title>NEXTERA - Authentication Failed</title><style>body{font-family:Arial;background:#1a1a2e;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}.error{background:rgba(255,0,0,0.1);border:1px solid #ff4444;padding:40px;border-radius:10px;text-align:center}h1{color:#ff4444}a{color:#4fc3f7}</style></head><body><div class=\"error\"><h1>Authentication Failed</h1><p>Invalid Employee ID or Password.</p><p>After 3 failed attempts, your account will be locked.</p><p><a href=\"/\">Return to Login</a></p></div></body></html>" > /opt/dionaea/var/lib/dionaea/http/root/api/login'

docker exec dionaea sh -c 'echo "<!DOCTYPE html><html><head><title>API - Unauthorized</title><style>body{font-family:monospace;background:#1a1a2e;color:#0f0;padding:20px}</style></head><body><pre>{\"error\":\"unauthorized\",\"message\":\"Valid API key required\",\"code\":401,\"hint\":\"Include X-API-Key header\"}</pre></body></html>" > /opt/dionaea/var/lib/dionaea/http/root/api/users'
```

Create phpMyAdmin maintenance page:

```bash
docker exec dionaea sh -c 'echo "<!DOCTYPE html><html><head><title>phpMyAdmin - Maintenance</title><style>body{font-family:Arial;background:#2c3e50;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}.box{background:#34495e;padding:40px;border-radius:10px;text-align:center}h1{color:#f39c12}</style></head><body><div class=\"box\"><h1>Scheduled Maintenance</h1><p>phpMyAdmin is currently undergoing scheduled maintenance.</p><p>Expected completion: 02:00 AM SGT</p></div></body></html>" > /opt/dionaea/var/lib/dionaea/http/root/phpmyadmin/index.html'
```

Create backup forbidden page:

```bash
docker exec dionaea sh -c 'echo "<!DOCTYPE html><html><head><title>403 Forbidden</title><style>body{font-family:Arial;background:#1a1a2e;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}.error{background:rgba(255,100,0,0.1);border:1px solid #ff6600;padding:40px;border-radius:10px;text-align:center}h1{color:#ff6600}</style></head><body><div class=\"error\"><h1>403 Forbidden</h1><p>You do not have permission to access /backup/</p><p>Your IP has been logged.</p></div></body></html>" > /opt/dionaea/var/lib/dionaea/http/root/backup/index.html'
```

## 14.3 FTP Content Configuration

Create FTP directories:

```bash
docker exec dionaea mkdir -p /opt/dionaea/var/lib/dionaea/ftp/root/backups
docker exec dionaea mkdir -p /opt/dionaea/var/lib/dionaea/ftp/root/reports
docker exec dionaea mkdir -p /opt/dionaea/var/lib/dionaea/ftp/root/config
```

Create FTP README:

```bash
docker exec dionaea bash -c 'cat > /opt/dionaea/var/lib/dionaea/ftp/root/README.txt << "EOF"
=================================================================
              NEXTERA TECH SOLUTIONS - FTP SERVER
=================================================================
This FTP server is for internal file sharing only.
Contact: it-helpdesk@nextera-tech.local | Ext: 4500
DIRECTORIES:
  /backups  - Weekly database backups (automated)
  /reports  - Monthly financial reports
  /config   - System configuration files
IMPORTANT: Do not store passwords in plain text!
Last updated: 2026-01-15
=================================================================
EOF'
```

Create backup script with credentials:

```bash
docker exec dionaea bash -c 'cat > /opt/dionaea/var/lib/dionaea/ftp/root/backups/backup_config.sh << "EOF"
#!/bin/bash
# Nextera Automated Backup Script v2.1
# Run via cron: 0 2 * * 0 /opt/scripts/backup_config.sh
MYSQL_HOST="db01.internal.nextera.local"
MYSQL_USER="backup_admin"
MYSQL_PASS="Bkp@Nxtr2024!"
POSTGRES_HOST="db02.internal.nextera.local"
POSTGRES_USER="postgres"
POSTGRES_PASS="PgNxtr#Secure24"
S3_BUCKET="s3://nextera-backups-prod"
AWS_ACCESS_KEY="AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
mysqldump -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASS --all-databases > /tmp/mysql_backup.sql
aws s3 cp /tmp/mysql_backup.sql $S3_BUCKET/mysql/$(date +%Y%m%d).sql
EOF'
```

Create financial report (honeytoken):

```bash
docker exec dionaea bash -c 'cat > /opt/dionaea/var/lib/dionaea/ftp/root/reports/Q4_2025_Finance.txt << "EOF"
NEXTERA TECH SOLUTIONS - Q4 2025 FINANCIAL SUMMARY
===================================================
CONFIDENTIAL - INTERNAL USE ONLY
Revenue:     $4,250,000
Expenses:    $2,890,000
Net Profit:  $1,360,000
Top Clients:
  - GlobalTech Industries: $850,000
  - Singapore Gov Contract: $1,200,000
  - Regional SMB Clients: $2,200,000
Bank Details (for reference):
  Account: Nextera Tech Solutions Pte Ltd
  Bank: DBS Singapore
  Account No: 0012-345678-9
  SWIFT: DBSSSGSG
Contact: finance@nextera-tech.local
===================================================
EOF'
```

**Note:** Bank account 0012-345678-9 serves as a honeytoken. If this string appears in external sources, it indicates data exfiltration.

Create database connections file:

```bash
docker exec dionaea bash -c 'cat > /opt/dionaea/var/lib/dionaea/ftp/root/config/db_connections.ini << "EOF"
[production]
host = db01.internal.nextera.local
port = 3306
user = prod_app
password = ProdDB@2024Secure!
database = nextera_prod
[staging]
host = staging-db.internal.nextera.local
port = 3306
user = staging_user
password = StagingPass123
database = nextera_staging
[analytics]
host = analytics.internal.nextera.local
port = 5432
user = analytics_ro
password = AnalyticsRead0nly!
database = nextera_analytics
EOF'
```

## 14.4 FTP Banner Configuration

```bash
docker exec dionaea bash -c 'cat > /opt/dionaea/etc/dionaea/services-available/ftp.yaml << "EOF"
# SPDX-FileCopyrightText: none
# SPDX-License-Identifier: CC0-1.0
- name: ftp
  config:
    root: "var/lib/dionaea/ftp/root"
    response_messages:
      welcome_msg: 220 NXTR-FTP01.internal.nextera.local FTP Server Ready - Authorized Users Only
EOF'
```

## 14.5 SMB Service Configuration

```bash
docker exec dionaea bash -c 'cat > /opt/dionaea/etc/dionaea/services-available/smb.yaml << "EOF"
# SPDX-FileCopyrightText: none
# SPDX-License-Identifier: CC0-1.0
- name: smb
  config:
    os_type: 4
    primary_domain: NEXTERA
    oem_domain_name: NEXTERA
    server_name: NXTR-FILE01
    native_os: Windows Server 2019 Standard 10.0.17763
    native_lan_manager: Windows Server 2019 Standard 10.0
    shares:
      ADMIN$:
        comment: Remote Admin
        path: C:\\Windows
        type: disktree
      C$:
        comment: Default Share
        path: C:\\
        type:
          - disktree
          - special
      IPC$:
        comment: Remote IPC
        type: ipc
      IT_Share$:
        comment: IT Department Files
        path: D:\\Shares\\IT
        type: disktree
      Finance$:
        comment: Finance Department - Restricted
        path: D:\\Shares\\Finance
        type: disktree
      Backups$:
        comment: Backup Storage
        path: E:\\Backups
        type: disktree
      Public:
        comment: Public Share - All Staff
        path: D:\\Shares\\Public
        type: disktree
EOF'
```

## 14.6 Apply Changes

```bash
docker restart dionaea
docker ps | grep dionaea
```

## 14.7 Deception Summary

| Protocol | Path/Setting | Content |
|----------|--------------|---------|
| HTTP | /index.html | Nextera login portal |
| HTTP | /assets/js/config.js | API keys and DB credentials |
| HTTP | /robots.txt | Hidden paths disclosure |
| HTTP | /admin/index.html | Admin console |
| HTTP | /api/login | Authentication error page |
| HTTP | /api/users | Unauthorized API response |
| HTTP | /phpmyadmin/ | Maintenance page |
| HTTP | /backup/ | 403 Forbidden page |
| FTP | Banner | NXTR-FTP01.internal.nextera.local |
| FTP | /README.txt | Server information |
| FTP | /backups/backup_config.sh | MySQL, PostgreSQL, AWS credentials |
| FTP | /reports/Q4_2025_Finance.txt | Financial data with bank details |
| FTP | /config/db_connections.ini | Database connection credentials |
| SMB | Server Name | NXTR-FILE01 |
| SMB | Domain | NEXTERA |
| SMB | OS | Windows Server 2019 Standard 10.0.17763 |
| SMB | Shares | IT_Share$, Finance$, Backups$, Public |

## 14.8 Credential Trap Summary

| Location | Credential | Type |
|----------|------------|------|
| config.js | PortalDB@2024! | Web DB password |
| config.js | nxtr-portal-api-key-2024-prod | API key |
| config.js | RedisNxtr#2024 | Redis password |
| backup_config.sh | Bkp@Nxtr2024! | MySQL backup |
| backup_config.sh | PgNxtr#Secure24 | PostgreSQL |
| backup_config.sh | AKIAIOSFODNN7EXAMPLE | AWS access key |
| db_connections.ini | ProdDB@2024Secure! | Production DB |
| db_connections.ini | AnalyticsRead0nly! | Analytics DB |
| Q4_2025_Finance.txt | 0012-345678-9 | Bank account (honeytoken) |

## 14.9 Cross-Pollination with Cowrie

Update Cowrie bash history to reference Dionaea (run on Cowrie VM):

```bash
cat >> /home/cowrie/cowrie/honeyfs/home/sysadmin/.bash_history << 'EOF'
ftp nxtr-ftp01.internal.nextera.local
cd /backups
get backup_config.sh
quit
sftp admin@172.16.0.30
EOF

cat >> /home/cowrie/cowrie/honeyfs/home/admin/.bash_history << 'EOF'
# Check FTP backups
ftp 172.16.0.30
cd /reports
get Q4_2025_Finance.txt
quit
# Upload to file server
smbclient //NXTR-FILE01/Backups$ -U admin
EOF
```

This makes both honeypots appear as part of the same enterprise network.

## Verification

Test from Kali:

```bash
# HTTP
curl -s http://172.16.0.30/ | grep -i nextera
curl -s http://172.16.0.30/robots.txt
curl -s http://172.16.0.30/assets/js/config.js

# FTP
ftp 172.16.0.30
# anonymous login
ls
cd backups
get backup_config.sh
quit

# SMB
smbclient -L 172.16.0.30 -N
```
