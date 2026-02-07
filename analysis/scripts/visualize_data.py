# Visualization module for honeypot data analysis.

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sns
from datetime import datetime
import os
from config import PROCESSED_DIR, CHARTS_DIR, ATTACKER_IPS


# THEME CONFIGURATION

# Color palette 
PALETTE = {
    'cowrie': '#1A5F7A',
    'dionaea': '#C73E1D',
    'primary': '#2C3E50',
    'secondary': '#E74C3C',
    'accent': '#F39C12',
    'success': '#1ABC9C',
    'info': '#3498DB',
    'muted': '#95A5A6',
    'background': '#FAFBFC',
    'grid': '#E8EAED',
    'text': '#2C3E50',
    'text_secondary': '#5D6D7E'
}

# Role colors
ROLE_PALETTE = {
    'recon': '#48C9B0',
    'bruteforce': '#F4D03F',
    'exploit': '#EB984E',
    'postaccess': '#E74C3C',
    'multistage': '#8E44AD',
    'manual': '#34495E',
    'unknown': '#BDC3C7'
}

def apply_theme():
    """Apply theme to all charts."""
    plt.style.use('seaborn-v0_8-whitegrid')
    
    plt.rcParams.update({
        'figure.facecolor': PALETTE['background'],
        'axes.facecolor': '#FFFFFF',
        'axes.edgecolor': PALETTE['grid'],
        'axes.labelcolor': PALETTE['text'],
        'axes.titlecolor': PALETTE['text'],
        'axes.titlesize': 13,
        'axes.titleweight': 'bold',
        'axes.labelsize': 10,
        'axes.labelweight': 'medium',
        'axes.grid': True,
        'axes.axisbelow': True,
        'grid.color': PALETTE['grid'],
        'grid.linewidth': 0.8,
        'grid.alpha': 0.7,
        'xtick.color': PALETTE['text_secondary'],
        'ytick.color': PALETTE['text_secondary'],
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 9,
        'legend.frameon': True,
        'legend.facecolor': '#FFFFFF',
        'legend.edgecolor': PALETTE['grid'],
        'figure.dpi': 150,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.2,
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'DejaVu Sans', 'Helvetica'],
    })

apply_theme()


def add_chart_title(fig, title, subtitle=""):
    """Add title and subtitle to chart."""
    fig.suptitle(title, fontsize=14, fontweight='bold', 
                 color=PALETTE['text'], y=1.02)
    if subtitle:
        fig.text(0.5, -0.02, subtitle, ha='center', fontsize=9, 
                 color=PALETTE['text_secondary'], style='italic')


def format_bars(ax, orientation='vertical'):
    """Apply bar styling."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['bottom'].set_linewidth(0.5)
    ax.tick_params(axis='both', which='both', length=0)


def load_all_data():
    """Load all processed CSV files."""
    data = {}
    
    files = {
        'unified': 'unified_timeline.csv',
        'cowrie': 'cowrie_processed.csv',
        'dionaea': 'dionaea_processed.csv',
        'logins': 'dionaea_logins.csv',
        'downloads': 'dionaea_downloads.csv',
        'sessions': 'attack_sessions.csv',
        'multi_hp': 'multi_honeypot_attackers.csv'
    }
    
    for key, filename in files.items():
        filepath = os.path.join(PROCESSED_DIR, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            if 'start_time' in df.columns:
                df['start_time'] = pd.to_datetime(df['start_time'])
            if 'end_time' in df.columns:
                df['end_time'] = pd.to_datetime(df['end_time'])
            data[key] = df
            print(f"Loaded {key}: {len(df)} records")
    
    return data


# CHART FUNCTIONS

def chart_total_events(data, save=True):
    """Total events comparison between honeypots."""
    
    df = data['unified']
    counts = df['source'].value_counts()
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    colors = [PALETTE['cowrie'], PALETTE['dionaea']]
    labels = ['Cowrie (SSH/Telnet)', 'Dionaea (Network)']
    
    bars = ax.bar(labels, [counts.get('cowrie', 0), counts.get('dionaea', 0)],
                  color=colors, edgecolor='white', linewidth=2, width=0.6)
    
    for bar, val in zip(bars, [counts.get('cowrie', 0), counts.get('dionaea', 0)]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() - bar.get_height()*0.1,
                f'{val:,}', ha='center', va='top', fontweight='bold', 
                fontsize=14, color='white')
    
    ax.set_ylabel('Total Events Captured')
    ax.set_ylim(0, max(counts.values) * 1.1)
    format_bars(ax)
    
    total = sum(counts.values)
    pct = counts.get('cowrie', 0) / total * 100
    ax.text(0.5, -0.12, f"Cowrie captured {pct:.1f}% of all events",
            transform=ax.transAxes, ha='center', fontsize=9, 
            color=PALETTE['text_secondary'])
    
    add_chart_title(fig, "Total Events Captured by Each Honeypot",
                    "Event volume between medium-interaction (Cowrie) and low-interaction (Dionaea) honeypots")
    
    plt.tight_layout()
    
    if save:
        filepath = os.path.join(CHARTS_DIR, 'total_events.png')
        plt.savefig(filepath, facecolor=fig.get_facecolor())
        print(f"Saved: {filepath}")
    
    plt.close()
    return fig


def chart_attack_types(data, save=True):
    # Attack category distribution.
    
    df = data['unified']
    categories = df['event_category'].value_counts()
    
    rename_map = {
        'session': 'Session Management',
        'client_info': 'Client Fingerprinting',
        'connection': 'Network Connections',
        'authentication': 'Authentication Attempts',
        'command': 'Command Execution',
        'file_transfer': 'File Transfers',
        'other': 'Other Events'
    }
    categories.index = categories.index.map(lambda x: rename_map.get(x, x.title()))
    
    fig, ax = plt.subplots(figsize=(9, 7))
    
    colors = [PALETTE['primary'], PALETTE['secondary'], PALETTE['accent'],
              PALETTE['success'], PALETTE['info'], PALETTE['muted'], '#BDC3C7']
    
    wedges, texts, autotexts = ax.pie(
        categories.values,
        labels=None,
        autopct=lambda pct: f'{pct:.1f}%' if pct > 3 else '',
        colors=colors[:len(categories)],
        explode=[0.02] * len(categories),
        startangle=90,
        pctdistance=0.75,
        wedgeprops={'linewidth': 2, 'edgecolor': 'white'}
    )
    
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
        autotext.set_color('white')
    
    ax.legend(wedges, [f'{cat} ({val:,})' for cat, val in zip(categories.index, categories.values)],
              loc='center left', bbox_to_anchor=(1, 0.5), frameon=True, fontsize=9)
    
    add_chart_title(fig, "Attack Category Distribution",
                    "Distribution of event types across both honeypot platforms")
    
    plt.tight_layout()
    
    if save:
        filepath = os.path.join(CHARTS_DIR, 'attack_types.png')
        plt.savefig(filepath, facecolor=fig.get_facecolor())
        print(f"Saved: {filepath}")
    
    plt.close()
    return fig


def chart_timeline_by_role(data, save=True):
    """Attack timeline by attacker role."""
    
    df = data['unified'].copy()
    df['hour_bin'] = df['timestamp'].dt.floor('h')
    
    pivot = df.groupby(['hour_bin', 'attacker_role']).size().unstack(fill_value=0)
    
    if len(pivot) > 0:
        full_range = pd.date_range(start=pivot.index.min(), end=pivot.index.max(), freq='h')
        pivot = pivot.reindex(full_range, fill_value=0)
    
    role_order = ['recon', 'bruteforce', 'exploit', 'postaccess', 'multistage', 'manual', 'unknown']
    pivot = pivot.reindex(columns=[c for c in role_order if c in pivot.columns])
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    colors = [ROLE_PALETTE.get(role, '#999') for role in pivot.columns]
    
    pivot.plot(kind='bar', stacked=True, ax=ax, color=colors, width=0.85, 
               edgecolor='white', linewidth=0.5)
    
    ax.set_xlabel('Time Period')
    ax.set_ylabel('Number of Events')
    
    n_ticks = min(12, len(pivot.index))
    tick_positions = np.linspace(0, len(pivot.index)-1, n_ticks, dtype=int)
    ax.set_xticks(tick_positions)
    ax.set_xticklabels([pivot.index[i].strftime('%m/%d %H:%M') for i in tick_positions], 
                       rotation=45, ha='right')
    
    handles = [mpatches.Patch(color=ROLE_PALETTE.get(r, '#999'), label=r.title()) 
               for r in pivot.columns]
    ax.legend(handles=handles, title='Attacker Role', bbox_to_anchor=(1.01, 1), 
              loc='upper left', frameon=True)
    
    format_bars(ax)
    
    add_chart_title(fig, "Attack Activity Timeline by Attacker Role",
                    "Stacked view showing attack phase progression")
    
    plt.tight_layout()
    
    if save:
        filepath = os.path.join(CHARTS_DIR, 'timeline_by_role.png')
        plt.savefig(filepath, facecolor=fig.get_facecolor())
        print(f"Saved: {filepath}")
    
    plt.close()
    return fig


def chart_targeted_services(data, save=True):
    # Top targeted services across all honeypots.
    
    df = data['unified']
    services = df['service'].value_counts().head(10)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = [PALETTE['cowrie'] if 'SSH' in str(s) or 'Telnet' in str(s) else PALETTE['dionaea'] 
              for s in services.index]
    
    bars = ax.barh(range(len(services)), services.values, color=colors, 
                   edgecolor='white', linewidth=1.5, height=0.7)
    ax.set_yticks(range(len(services)))
    ax.set_yticklabels(services.index, fontsize=10)
    ax.invert_yaxis()
    
    max_val = max(services.values)
    for i, (bar, val) in enumerate(zip(bars, services.values)):
        ax.text(val + max_val*0.02, i, f'{val:,}', va='center', fontsize=9, 
                color=PALETTE['text_secondary'])
    
    ax.set_xlabel('Number of Events')
    ax.set_xlim(0, max_val * 1.15)
    format_bars(ax)
    
    legend_elements = [mpatches.Patch(facecolor=PALETTE['cowrie'], label='Cowrie Services'),
                       mpatches.Patch(facecolor=PALETTE['dionaea'], label='Dionaea Services')]
    ax.legend(handles=legend_elements, loc='lower right', frameon=True)
    
    add_chart_title(fig, "Top Targeted Services",
                    "Services most frequently targeted by attackers")
    
    plt.tight_layout()
    
    if save:
        filepath = os.path.join(CHARTS_DIR, 'targeted_services.png')
        plt.savefig(filepath, facecolor=fig.get_facecolor())
        print(f"Saved: {filepath}")
    
    plt.close()
    return fig


def chart_credentials(data, save=True):
    # Top credentials used across all honeypots.
    
    cowrie = data['cowrie'][['username', 'password']].dropna(subset=['username'])
    dionaea = data['logins'][['username', 'password']].dropna(subset=['username'])
    all_creds = pd.concat([cowrie, dionaea], ignore_index=True)
    
    def clean_password(x):
        if pd.isna(x):
            return '(empty)'
        x_str = str(x).strip()
        if x_str == '' or x_str == 'nan' or x_str == 'None':
            return '(empty)'
        return x_str[:20] if len(x_str) > 20 else x_str
    
    all_creds['password'] = all_creds['password'].apply(clean_password)
    
    def clean_username(x):
        x_str = str(x).strip()
        return x_str[:20] if len(x_str) > 20 else x_str
    
    all_creds['username'] = all_creds['username'].apply(clean_username)
    
    top_users = all_creds['username'].value_counts().head(10)
    top_passwords = all_creds['password'].value_counts().head(10)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    bars1 = ax1.barh(range(len(top_users)), top_users.values, 
                     color=PALETTE['primary'], edgecolor='white', height=0.7)
    ax1.set_yticks(range(len(top_users)))
    ax1.set_yticklabels(top_users.index, fontfamily='monospace', fontsize=10)
    ax1.invert_yaxis()
    ax1.set_xlabel('Frequency')
    ax1.set_title('Top 10 Usernames', fontsize=11, fontweight='bold', pad=10)
    format_bars(ax1)
    
    for i, val in enumerate(top_users.values):
        ax1.text(val + max(top_users.values)*0.02, i, str(val), 
                 va='center', fontsize=9, color=PALETTE['text_secondary'])
    
    bars2 = ax2.barh(range(len(top_passwords)), top_passwords.values,
                     color=PALETTE['secondary'], edgecolor='white', height=0.7)
    ax2.set_yticks(range(len(top_passwords)))
    ax2.set_yticklabels(top_passwords.index, fontfamily='monospace', fontsize=10)
    ax2.invert_yaxis()
    ax2.set_xlabel('Frequency')
    ax2.set_title('Top 10 Passwords', fontsize=11, fontweight='bold', pad=10)
    format_bars(ax2)
    
    for i, val in enumerate(top_passwords.values):
        ax2.text(val + max(top_passwords.values)*0.02, i, str(val),
                 va='center', fontsize=9, color=PALETTE['text_secondary'])
    
    add_chart_title(fig, "Credential Analysis",
                    "Most commonly attempted usernames and passwords")
    
    plt.tight_layout()
    
    if save:
        filepath = os.path.join(CHARTS_DIR, 'credentials.png')
        plt.savefig(filepath, facecolor=fig.get_facecolor())
        print(f"Saved: {filepath}")
    
    plt.close()
    return fig


def chart_login_success(data, save=True):
    # Login attempt outcomes in Cowrie.
    
    df = data['cowrie']
    login_events = df[df['event_type'].str.contains('login', case=False, na=False)]
    
    success_count = len(login_events[login_events['event_type'].str.contains('success', case=False, na=False)])
    failed_count = len(login_events[login_events['event_type'].str.contains('failed', case=False, na=False)])
    
    fig, ax = plt.subplots(figsize=(8, 7))
    
    sizes = [success_count, failed_count]
    labels = ['Successful', 'Failed']
    colors = [PALETTE['success'], PALETTE['secondary']]
    
    wedges, texts, autotexts = ax.pie(
        sizes, labels=None, autopct='%1.1f%%',
        colors=colors, explode=[0.03, 0],
        startangle=90, pctdistance=0.6,
        wedgeprops={'linewidth': 2, 'edgecolor': 'white'}
    )
    
    for autotext in autotexts:
        autotext.set_fontsize(12)
        autotext.set_fontweight('bold')
        autotext.set_color('white')
    
    total = sum(sizes)
    centre_circle = plt.Circle((0, 0), 0.4, fc='white')
    ax.add_patch(centre_circle)
    ax.text(0, 0.05, f'{total:,}', ha='center', va='center', fontsize=18, fontweight='bold')
    ax.text(0, -0.12, 'Total Attempts', ha='center', va='center', fontsize=10, 
            color=PALETTE['text_secondary'])
    
    ax.legend(wedges, [f'{l} ({v:,})' for l, v in zip(labels, sizes)],
              loc='lower center', bbox_to_anchor=(0.5, -0.08), ncol=2, frameon=True)
    
    add_chart_title(fig, "Login Attempt Outcomes",
                    "Success vs failure rate for authentication attempts in Cowrie")
    
    plt.tight_layout()
    
    if save:
        filepath = os.path.join(CHARTS_DIR, 'login_success.png')
        plt.savefig(filepath, facecolor=fig.get_facecolor())
        print(f"Saved: {filepath}")
    
    plt.close()
    return fig


def chart_commands(data, save=True):
    # Top commands executed in Cowrie.
    
    df = data['cowrie']
    commands = df[df['event_category'] == 'command']['input'].dropna()
    commands = commands.str.strip()
    commands = commands[commands != '']
    
    sip_patterns = [
        'CSeq:', 'Max-Forwards:', 'Call-ID:', 'Content-Length:',
        'Accept:', 'Via:', 'From:', 'To:', 'Contact:', 'User-Agent:',
        'SIP/', 'OPTIONS sip:', 'INVITE sip:', 'REGISTER sip:',
        'application/sdp', 'sip:', '@', 'Allow:'
    ]
    
    def is_valid_shell_command(cmd):
        cmd_upper = str(cmd).upper()
        for pattern in sip_patterns:
            if pattern.upper() in cmd_upper:
                return False
        if cmd_upper.startswith(('OPTIONS ', 'INVITE ', 'REGISTER ')):
            return False
        if cmd.isdigit():
            return False
        return True
    
    commands = commands[commands.apply(is_valid_shell_command)]
    command_counts = commands.value_counts().head(15)
    
    fig, ax = plt.subplots(figsize=(11, 7))
    
    n = len(command_counts)
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, n))[::-1]
    
    bars = ax.barh(range(n), command_counts.values, color=colors, 
                   edgecolor='white', height=0.75)
    ax.set_yticks(range(n))
    ax.set_yticklabels(command_counts.index, fontfamily='monospace', fontsize=9)
    ax.invert_yaxis()
    
    for i, val in enumerate(command_counts.values):
        ax.text(val + max(command_counts.values)*0.02, i, str(val),
                va='center', fontsize=9, color=PALETTE['text_secondary'])
    
    ax.set_xlabel('Execution Count')
    ax.set_xlim(0, max(command_counts.values) * 1.12)
    format_bars(ax)
    
    add_chart_title(fig, "Command Execution Analysis",
                    "Top 15 commands executed by attackers in Cowrie")
    
    plt.tight_layout()
    
    if save:
        filepath = os.path.join(CHARTS_DIR, 'commands.png')
        plt.savefig(filepath, facecolor=fig.get_facecolor())
        print(f"Saved: {filepath}")
    
    plt.close()
    return fig


def chart_heatmap(data, save=True):
    # Attack activity heatmap by hour and role.
    
    df = data['unified'].copy()
    df['hour'] = df['timestamp'].dt.hour
    
    pivot = df.groupby(['hour', 'attacker_role']).size().unstack(fill_value=0)
    
    pivot = pivot.reindex(range(24), fill_value=0)
    
    role_order = ['recon', 'bruteforce', 'exploit', 'postaccess', 'multistage', 'manual', 'unknown']
    pivot = pivot.reindex(columns=[c for c in role_order if c in pivot.columns])
    
    pivot.columns = [c.title() for c in pivot.columns]
    pivot.index = [f'{h:02d}:00' for h in pivot.index]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    sns.heatmap(pivot.T, ax=ax, cmap='viridis', annot=True, fmt='d',
                annot_kws={'size': 8}, cbar_kws={'label': 'Number of Events'},
                linewidths=0.5, linecolor='white')
    
    ax.set_xlabel('Hour of Day (UTC+8)')
    ax.set_ylabel('Attacker Role')
    
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(fontsize=10)
    
    add_chart_title(fig, "Attack Activity Heatmap",
                    "Temporal distribution of attacks by hour and role")
    
    plt.tight_layout()
    
    if save:
        filepath = os.path.join(CHARTS_DIR, 'heatmap.png')
        plt.savefig(filepath, facecolor=fig.get_facecolor())
        print(f"Saved: {filepath}")
    
    plt.close()
    return fig


def chart_session_duration(data, save=True):
    # Session duration distribution by attacker role.
    
    df = data['sessions'].copy()
    df['duration_seconds'] = (df['end_time'] - df['start_time']).dt.total_seconds()
    
    df = df[(df['duration_seconds'] > 0) & (df['duration_seconds'] < 7200)]
    
    role_order = ['manual', 'recon', 'bruteforce', 'exploit', 'postaccess', 'multistage']
    roles = [r for r in role_order if r in df['attacker_role'].values]
    
    fig, ax = plt.subplots(figsize=(11, 6))
    
    data_by_role = [df[df['attacker_role'] == role]['duration_seconds'].values / 60 for role in roles]
    
    bp = ax.boxplot(data_by_role, tick_labels=[r.title() for r in roles], patch_artist=True,
                    widths=0.6, showfliers=True)
    
    for patch, role in zip(bp['boxes'], roles):
        patch.set_facecolor(ROLE_PALETTE.get(role, '#999'))
        patch.set_alpha(0.8)
        patch.set_edgecolor(PALETTE['text'])
        patch.set_linewidth(1.5)
    
    for median in bp['medians']:
        median.set_color(PALETTE['text'])
        median.set_linewidth(2)
    
    ax.set_xlabel('Attacker Role')
    ax.set_ylabel('Session Duration (minutes)')
    format_bars(ax)
    ax.grid(True, axis='y', alpha=0.5)
    
    for i, (role, role_data) in enumerate(zip(roles, data_by_role)):
        if len(role_data) > 0:
            median = np.median(role_data)
            ax.text(i + 1, median + 1, f'{median:.1f}m', ha='center', 
                    fontsize=9, color=PALETTE['text_secondary'])
    
    add_chart_title(fig, "Session Duration by Attacker Role",
                    "Distribution of attack session lengths")
    
    plt.tight_layout()
    
    if save:
        filepath = os.path.join(CHARTS_DIR, 'session_duration.png')
        plt.savefig(filepath, facecolor=fig.get_facecolor())
        print(f"Saved: {filepath}")
    
    plt.close()
    return fig


def chart_protocols(data, save=True):
    # Protocol/service distribution in Dionaea.
    
    df = data['dionaea']
    services = df['service'].value_counts()
    
    TOP_N = 8
    if len(services) > TOP_N:
        top_services = services.head(TOP_N)
        other_count = services.iloc[TOP_N:].sum()
        services_display = pd.concat([
            top_services,
            pd.Series({'Other Services': other_count})
        ])
    else:
        services_display = services
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    colors = [PALETTE['primary'], PALETTE['secondary'], PALETTE['accent'],
              PALETTE['success'], PALETTE['info'], PALETTE['cowrie'],
              PALETTE['dionaea'], '#9B59B6', PALETTE['muted']][:len(services_display)]
    
    wedges, texts, autotexts = ax.pie(
        services_display.values, labels=None, 
        autopct=lambda pct: f'{pct:.1f}%' if pct > 3 else '',
        colors=colors, explode=[0.02] * len(services_display),
        startangle=90, pctdistance=0.75,
        wedgeprops={'linewidth': 2, 'edgecolor': 'white'}
    )
    
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
        autotext.set_color('white')
    
    ax.legend(wedges, [f'{svc} ({val:,})' for svc, val in zip(services_display.index, services_display.values)],
              loc='center left', bbox_to_anchor=(1, 0.5), frameon=True, fontsize=10)
    
    if len(services) > TOP_N:
        other_note = f"'Other Services' includes {len(services) - TOP_N} additional port/protocols"
        ax.text(0.5, -0.08, other_note, transform=ax.transAxes, ha='center', 
                fontsize=9, color=PALETTE['text_secondary'], style='italic')
    
    add_chart_title(fig, "Dionaea Service Distribution",
                    "Network services targeted by attackers in Dionaea")
    
    plt.tight_layout()
    
    if save:
        filepath = os.path.join(CHARTS_DIR, 'protocols.png')
        plt.savefig(filepath, facecolor=fig.get_facecolor())
        print(f"Saved: {filepath}")
    
    plt.close()
    return fig


def chart_comparison(data, save=True):
    # Comparative metrics between honeypots.
    
    cowrie_df = data['cowrie']
    dionaea_df = data['dionaea']
    unified_df = data['unified']
    
    metrics = {
        'Total\nEvents': [
            len(unified_df[unified_df['source'] == 'cowrie']),
            len(unified_df[unified_df['source'] == 'dionaea'])
        ],
        'Unique\nAttackers': [
            cowrie_df['src_ip'].nunique(),
            dionaea_df['src_ip'].nunique()
        ],
        'Auth\nAttempts': [
            len(cowrie_df[cowrie_df['event_category'] == 'authentication']),
            len(data['logins'])
        ],
        'Shell Cmds\n/ Net Conns*': [
            len(cowrie_df[cowrie_df['event_category'] == 'command']),
            len(dionaea_df)
        ]
    }
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(metrics))
    width = 0.35
    
    cowrie_vals = [m[0] for m in metrics.values()]
    dionaea_vals = [m[1] for m in metrics.values()]
    
    bars1 = ax.bar(x - width/2, cowrie_vals, width, label='Cowrie', 
                   color=PALETTE['cowrie'], edgecolor='white', linewidth=1.5)
    bars2 = ax.bar(x + width/2, dionaea_vals, width, label='Dionaea',
                   color=PALETTE['dionaea'], edgecolor='white', linewidth=1.5)
    
    ax.set_xticks(x)
    ax.set_xticklabels(metrics.keys(), fontsize=10)
    ax.set_ylabel('Count')
    ax.legend(loc='upper right', frameon=True)
    
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + max(cowrie_vals + dionaea_vals)*0.02,
                    f'{int(height):,}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    format_bars(ax)
    ax.set_ylim(0, max(cowrie_vals + dionaea_vals) * 1.15)
    
    ax.text(0.5, -0.12, "* Shell Cmds (Cowrie) and Net Conns (Dionaea) measure different interaction types",
            transform=ax.transAxes, ha='center', fontsize=8, 
            color=PALETTE['text_secondary'], style='italic')
    
    add_chart_title(fig, "Comparative Metrics: Cowrie vs Dionaea",
                    "Side-by-side comparison of key metrics")
    
    plt.tight_layout()
    
    if save:
        filepath = os.path.join(CHARTS_DIR, 'comparison.png')
        plt.savefig(filepath, facecolor=fig.get_facecolor())
        print(f"Saved: {filepath}")
    
    plt.close()
    return fig


def chart_dashboard(data, save=True):
    # Overview dashboard.
    
    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor(PALETTE['background'])
    
    gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3, 
                          left=0.06, right=0.94, top=0.9, bottom=0.08)
    
    unified_df = data['unified']
    cowrie_df = data['cowrie']
    
    ax1 = fig.add_subplot(gs[0, 0])
    counts = unified_df['source'].value_counts()
    ax1.bar(['Cowrie', 'Dionaea'], [counts.get('cowrie', 0), counts.get('dionaea', 0)],
            color=[PALETTE['cowrie'], PALETTE['dionaea']], edgecolor='white')
    ax1.set_title('Events by Honeypot', fontweight='bold', fontsize=10)
    ax1.set_ylabel('Count', fontsize=9)
    format_bars(ax1)
    
    ax2 = fig.add_subplot(gs[0, 1])
    roles = unified_df['attacker_role'].value_counts().head(6)
    colors = [ROLE_PALETTE.get(r, '#999') for r in roles.index]
    ax2.barh(range(len(roles)), roles.values, color=colors, edgecolor='white')
    ax2.set_yticks(range(len(roles)))
    ax2.set_yticklabels([r.title() for r in roles.index], fontsize=9)
    ax2.invert_yaxis()
    ax2.set_title('Events by Attacker Role', fontweight='bold', fontsize=10)
    format_bars(ax2)
    
    ax3 = fig.add_subplot(gs[0, 2])
    services = unified_df['service'].value_counts().head(6)
    ax3.barh(range(len(services)), services.values, color=PALETTE['primary'], edgecolor='white')
    ax3.set_yticks(range(len(services)))
    ax3.set_yticklabels(services.index, fontsize=9)
    ax3.invert_yaxis()
    ax3.set_title('Top Targeted Services', fontweight='bold', fontsize=10)
    format_bars(ax3)
    
    ax4 = fig.add_subplot(gs[1, 0])
    categories = unified_df['event_category'].value_counts()
    colors = plt.cm.Set2(np.linspace(0, 1, len(categories)))
    wedges, texts, autotexts = ax4.pie(categories.values, labels=None, autopct='%1.0f%%', startangle=90,
            colors=colors,
            wedgeprops={'linewidth': 1, 'edgecolor': 'white'})
    ax4.legend(wedges, [c.title() for c in categories.index], 
               loc='center left', bbox_to_anchor=(-0.3, 0.5), fontsize=7)
    ax4.set_title('Event Categories', fontweight='bold', fontsize=10)
    
    ax5 = fig.add_subplot(gs[1, 1])
    users = cowrie_df['username'].dropna().value_counts().head(5)
    ax5.barh(range(len(users)), users.values, color=PALETTE['secondary'], edgecolor='white')
    ax5.set_yticks(range(len(users)))
    ax5.set_yticklabels(users.index, fontfamily='monospace', fontsize=9)
    ax5.invert_yaxis()
    ax5.set_title('Top Usernames', fontweight='bold', fontsize=10)
    format_bars(ax5)
    
    ax6 = fig.add_subplot(gs[1, 2])
    
    def clean_pwd(x):
        if pd.isna(x):
            return '(empty)'
        x_str = str(x).strip()
        if x_str == '' or x_str == 'nan' or x_str == 'None':
            return '(empty)'
        return x_str[:15] if len(x_str) > 15 else x_str
    
    pwd_cleaned = cowrie_df['password'].apply(clean_pwd)
    passwords = pwd_cleaned.value_counts().head(5)
    ax6.barh(range(len(passwords)), passwords.values, color=PALETTE['accent'], edgecolor='white')
    ax6.set_yticks(range(len(passwords)))
    ax6.set_yticklabels(passwords.index, fontfamily='monospace', fontsize=9)
    ax6.invert_yaxis()
    ax6.set_title('Top Passwords', fontweight='bold', fontsize=10)
    format_bars(ax6)
    
    ax7 = fig.add_subplot(gs[2, :])
    hourly = unified_df.set_index('timestamp').resample('h').size()
    ax7.fill_between(hourly.index, hourly.values, alpha=0.3, color=PALETTE['primary'])
    ax7.plot(hourly.index, hourly.values, color=PALETTE['primary'], linewidth=2)
    ax7.set_title('Attack Activity Over Time', fontweight='bold', fontsize=10)
    ax7.set_xlabel('Time', fontsize=9)
    ax7.set_ylabel('Events/Hour', fontsize=9)
    ax7.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
    plt.setp(ax7.xaxis.get_majorticklabels(), rotation=30, ha='right', fontsize=8)
    format_bars(ax7)
    ax7.grid(True, alpha=0.5)
    
    fig.suptitle('Dashboard Overview', fontsize=14, fontweight='bold', y=0.97)
    fig.text(0.5, 0.02, 'Summary of attack patterns captured during the collection period',
             ha='center', fontsize=10, style='italic', color=PALETTE['text_secondary'])
    
    if save:
        filepath = os.path.join(CHARTS_DIR, 'dashboard.png')
        plt.savefig(filepath, facecolor=fig.get_facecolor())
        print(f"Saved: {filepath}")
    
    plt.close()
    return fig


def chart_attack_sources(data: dict, save=True):
    """Attack source distribution by IP address."""
    
    df = data['unified']
    if df.empty:
        return None
    
    ip_counts = df['src_ip'].value_counts()
    
    role_colors = ROLE_PALETTE.copy()
    role_colors['unknown'] = PALETTE['muted']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = []
    for ip in ip_counts.index:
        role = ATTACKER_IPS.get(ip, 'unknown')
        color = role_colors.get(role, PALETTE['text_secondary'])
        bar = ax.barh(ip, ip_counts[ip], color=color, edgecolor='white', linewidth=0.5)
        bars.append(bar)
    
    for i, (ip, count) in enumerate(ip_counts.items()):
        ax.text(count + ip_counts.max() * 0.02, i, f'{count:,}',
                va='center', ha='left', fontsize=10, fontweight='bold',
                color=PALETTE['text'])
    
    ax.set_xlabel('Number of Events', fontsize=11, fontweight='bold')
    ax.set_ylabel('Source IP Address', fontsize=11, fontweight='bold')
    
    yticklabels = [f"{ip} ({ATTACKER_IPS.get(ip, 'unknown').title()})" for ip in ip_counts.index]
    ax.set_yticks(range(len(ip_counts)))
    ax.set_yticklabels(yticklabels, fontsize=10)
    
    ax.set_xlim(0, ip_counts.max() * 1.15)
    
    legend_handles = []
    roles_present = df['attacker_role'].unique()
    for role in ['recon', 'bruteforce', 'exploit', 'postaccess', 'multistage', 'manual']:
        if role in roles_present:
            patch = mpatches.Patch(color=role_colors[role], label=role.title())
            legend_handles.append(patch)
    
    ax.legend(handles=legend_handles, title='Attacker Role', loc='lower right',
              fontsize=9, title_fontsize=10, framealpha=0.9)
    
    add_chart_title(fig, "Attack Source Distribution",
                    "Events by source IP showing network namespace attacker profiles")
    
    plt.tight_layout()
    
    if save:
        filepath = os.path.join(CHARTS_DIR, 'attack_sources.png')
        plt.savefig(filepath, facecolor=fig.get_facecolor())
        print(f"Saved: {filepath}")
    
    plt.close()
    return fig


# MAIN

def main():
    """Generate all visualization charts."""
    
    print("=" * 60)
    print("Honeypot Data Visualization")
    print("=" * 60)
    
    print("\nLoading processed data...")
    data = load_all_data()
    
    if not data:
        print("Error: No data found. Run correlate_logs.py first.")
        return
    
    print("\nGenerating charts...")
    
    charts = [
        ("Total Events", chart_total_events),
        ("Attack Types", chart_attack_types),
        ("Timeline by Role", chart_timeline_by_role),
        ("Targeted Services", chart_targeted_services),
        ("Credentials", chart_credentials),
        ("Login Success", chart_login_success),
        ("Commands", chart_commands),
        ("Heatmap", chart_heatmap),
        ("Session Duration", chart_session_duration),
        ("Protocols", chart_protocols),
        ("Comparison", chart_comparison),
        ("Dashboard", chart_dashboard),
        ("Attack Sources", chart_attack_sources)
    ]
    
    successful = 0
    for name, func in charts:
        try:
            print(f"\n  Generating {name}...")
            func(data)
            successful += 1
        except Exception as e:
            print(f"  Error in {name}: {e}")
    
    print("\n" + "=" * 60)
    print(f"Complete: {successful}/{len(charts)} charts generated")
    print("=" * 60)
    print(f"\nOutput directory: {CHARTS_DIR}")

if __name__ == "__main__":
    main()
