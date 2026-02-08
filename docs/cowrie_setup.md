# Cowrie Honeypot Setup

This guide covers installing and configuring Cowrie SSH/Telnet honeypot on Ubuntu Server.

All commands are run on the Cowrie honeypot VM.

## Create Dedicated User

```bash
sudo adduser --disabled-password --gecos "" cowrie
```

## Install Dependencies

```bash
sudo apt update
sudo apt install -y git python3-venv python3-dev libssl-dev libffi-dev build-essential python3-pip
```

## Clone Cowrie Repository

```bash
sudo su - cowrie
git clone https://github.com/cowrie/cowrie.git
cd cowrie
```

## Setup Virtual Environment

```bash
pwd
# Should show /home/cowrie/cowrie

python3 -m venv cowrie-env
source cowrie-env/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## Configure Cowrie

```bash
cp etc/cowrie.cfg.dist etc/cowrie.cfg
nano etc/cowrie.cfg
```

Set these values:

```ini
[honeypot]
hostname = NXTR-PROD-SSH01

[output_jsonlog]
enabled = true
logfile = ${honeypot:log_path}/cowrie.json
```

## Configure Port Redirection

Exit to admin user and configure iptables:

```bash
exit
sudo iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 2222
sudo iptables -t nat -A PREROUTING -p tcp --dport 23 -j REDIRECT --to-port 2223
```

Make rules persistent:

```bash
sudo apt install -y iptables-persistent
sudo netfilter-persistent save
```

## Move Real SSH to High Port

```bash
sudo nano /etc/ssh/sshd_config
```

Change to:

```
Port 22222
```

Restart:

```bash
sudo systemctl restart sshd
```

## Start Cowrie

```bash
sudo su - cowrie
cd cowrie
source cowrie-env/bin/activate
cowrie start
```

Verify:

```bash
cowrie status
```

## Testing

From Kali, test SSH:

```bash
ssh root@172.16.0.20
```

Enter any password. You should see a fake shell. Type `exit` to disconnect.

Check logs:

```bash
sudo su - cowrie
tail -5 cowrie/var/log/cowrie/cowrie.json
```

## Troubleshooting

If Cowrie fails to start:

```bash
cat cowrie/var/log/cowrie/cowrie.log
```
