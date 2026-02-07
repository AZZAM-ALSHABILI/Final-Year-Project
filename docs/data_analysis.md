# Data Analysis and Visualization

This document describes the process for collecting, processing, and visualizing honeypot data from Phase 3 (deception phase). All commands are run on the Analyst Machine (Ubuntu Server) via SSH.

## Prerequisites

- Analyst VM (analysis-elk) accessible via SSH
- VS Code with Remote-SSH extension for development
- Python 3.10+ with pandas, matplotlib, seaborn, numpy
- Phase 3 completed with honeypot logs generated

## 4.1 Directory Structure

```
~/honeypot_research/
├── analysis/
│   ├── output/
│   │   ├── charts/          # Generated visualizations (13 PNG files)
│   │   ├── processed/       # Unified CSV outputs
│   │ 
│   └── scripts/             # Python analysis scripts
└── raw_data/
    ├── cowrie/
    │   ├── downloads/       # Captured malicious files
    │   ├── logs/            # JSON event logs
    │   └── tty/             # Session recordings
    └── dionaea/
        ├── binaries/        # Captured malware samples
        └── dionaea.sqlite   # SQLite database
```

## 4.2 Environment Setup

Connect to analyst VM via SSH:

```bash
ssh analyst@192.168.56.40
```

For development, use VS Code Remote-SSH extension to connect to the analyst machine.

Install Python dependencies:

```bash
cd ~/honeypot_research/analysis/scripts
pip install pandas matplotlib seaborn numpy
```

## 4.3 Transfer Logs from Honeypots

From the analyst machine, use SCP to collect logs:

```bash
# Create raw_data directory structure
mkdir -p ~/honeypot_research/raw_data/{cowrie,dionaea}

# Transfer Cowrie data
scp -r cowrie@<COWRIE_VM_IP>:~/cowrie/var/log/cowrie/ ~/honeypot_research/raw_data/cowrie/logs/
scp -r cowrie@<COWRIE_VM_IP>:~/cowrie/var/lib/cowrie/downloads/ ~/honeypot_research/raw_data/cowrie/downloads/
scp -r cowrie@<COWRIE_VM_IP>:~/cowrie/var/lib/cowrie/tty/ ~/honeypot_research/raw_data/cowrie/tty/

# Transfer Dionaea data
scp root@<DIONAEA_VM_IP>:/opt/dionaea/var/lib/dionaea/dionaea.sqlite ~/honeypot_research/raw_data/dionaea/
scp -r root@<DIONAEA_VM_IP>:/opt/dionaea/var/lib/dionaea/binaries/ ~/honeypot_research/raw_data/dionaea/binaries/
```

## 4.4 Analysis Scripts

The analysis pipeline consists of 6 Python scripts located in `~/honeypot_research/analysis/scripts/`:

| Script | Purpose |
|--------|---------|
| `config.py` | Configuration constants (paths, attacker IPs, role mappings) |
| `load_cowrie.py` | Parse Cowrie JSON logs into structured DataFrames |
| `load_dionaea.py` | Parse Dionaea SQLite database into structured DataFrames |
| `correlate_logs.py` | Correlate events across honeypots, assign attacker roles |
| `process_data.py` | Main data processing pipeline |
| `visualize_data.py` | Generate all 13 charts from processed data |

> **Note:** Full source code is available in the project GitHub repository.

## 4.5 Run Data Processing

Process raw logs into unified format:

```bash
cd ~/honeypot_research/analysis/scripts
python3 process_data.py
```

Generated outputs in `~/honeypot_research/analysis/output/processed/`:

| File | Description |
|------|-------------|
| `unified_timeline.csv` | Combined events from both honeypots |
| `cowrie_processed.csv` | Structured Cowrie event data |
| `dionaea_processed.csv` | Structured Dionaea event data |
| `attack_sessions.csv` | Correlated attack sessions |
| `dionaea_logins.csv` | Dionaea authentication attempts |
| `dionaea_downloads.csv` | Captured file downloads |
| `multi_honeypot_attackers.csv` | Attackers targeting multiple honeypots |

## 4.6 Generate Visualizations

Create all 13 charts:

```bash
python3 visualize_data.py
```

Generated charts in `~/honeypot_research/analysis/output/charts/`:

| # | Chart File | Description |
|---|------------|-------------|
| 1 | `total_events.png` | Events by honeypot type |
| 2 | `attack_types.png` | Attack distribution by role |
| 3 | `timeline_by_role.png` | Activity over time by attacker role |
| 4 | `targeted_services.png` | Most targeted services/ports |
| 5 | `credentials.png` | Top usernames and passwords |
| 6 | `login_success.png` | Authentication success/failure rates |
| 7 | `commands.png` | Most executed shell commands |
| 8 | `heatmap.png` | Activity by hour and attacker role |
| 9 | `session_duration.png` | Session length distribution |
| 10 | `protocols.png` | Dionaea service distribution |
| 11 | `comparison.png` | Cowrie vs Dionaea metrics |
| 12 | `attack_sources.png` | Events by source IP |
| 13 | `dashboard.png` | Comprehensive multi-panel dashboard |

## 4.7 Verification

Verify successful generation:

```bash
# Check all charts were generated
ls ~/honeypot_research/analysis/output/charts/*.png | wc -l
# Expected: 13

# Check processed data files
ls ~/honeypot_research/analysis/output/processed/*.csv | wc -l
# Expected: 7
```

## 4.8 Troubleshooting

| Issue | Solution |
|-------|----------|
| Missing Python packages | `pip install pandas matplotlib seaborn numpy` |
| Empty charts | Verify logs exist in `raw_data/cowrie/logs/` and `raw_data/dionaea/` |
| Permission denied | Check SSH key access to honeypot VMs |
| Import errors | Ensure running from `scripts/` directory |
