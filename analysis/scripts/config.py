# Configuration settings 

import os

# Base directory
BASE_DIR = os.path.expanduser("~/honeypot_research")

# Raw data paths
RAW_DATA_DIR = os.path.join(BASE_DIR, "raw_data")
COWRIE_LOG = os.path.join(RAW_DATA_DIR, "cowrie/logs/cowrie_combined.json")
DIONAEA_DB = os.path.join(RAW_DATA_DIR, "dionaea/dionaea.sqlite")

# Output paths
OUTPUT_DIR = os.path.join(BASE_DIR, "analysis/output")
PROCESSED_DIR = os.path.join(OUTPUT_DIR, "processed")
CHARTS_DIR = os.path.join(OUTPUT_DIR, "charts")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")

# Create directories if they don't exist
for directory in [PROCESSED_DIR, CHARTS_DIR, REPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Attack source IP mapping
ATTACKER_IPS = {
    "172.16.0.101": "recon",
    "172.16.0.102": "bruteforce",
    "172.16.0.103": "exploit",
    "172.16.0.104": "postaccess",
    "172.16.0.105": "multistage",
    "172.16.0.10": "manual"
}
