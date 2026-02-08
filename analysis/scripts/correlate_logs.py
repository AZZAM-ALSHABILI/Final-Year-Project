"""
Log Correlation Engine for Honeypot Data Analysis.
Correlates events across Cowrie and Dionaea honeypots to build unified attack timelines.

"""

import pandas as pd
import os
from datetime import timedelta
from config import PROCESSED_DIR, ATTACKER_IPS


# Time window for correlating events from the same attack session (seconds)
CORRELATION_WINDOW = 300


def normalize_timestamp(ts):
    """Convert timestamp to timezone-naive for consistent comparison."""
    if pd.isna(ts):
        return ts
    if hasattr(ts, 'tz') and ts.tz is not None:
        return ts.tz_localize(None)
    return ts


def load_processed_data():
    """Load all processed CSV files into DataFrames."""
    
    data = {}
    
    # Load Cowrie events
    cowrie_path = os.path.join(PROCESSED_DIR, "cowrie_processed.csv")
    if os.path.exists(cowrie_path):
        data["cowrie"] = pd.read_csv(cowrie_path, parse_dates=["timestamp"])
        print(f"Loaded Cowrie: {len(data['cowrie'])} events")
    
    # Load Dionaea connections
    dionaea_path = os.path.join(PROCESSED_DIR, "dionaea_processed.csv")
    if os.path.exists(dionaea_path):
        data["dionaea"] = pd.read_csv(dionaea_path, parse_dates=["timestamp"])
        print(f"Loaded Dionaea connections: {len(data['dionaea'])} events")
    
    # Load Dionaea logins
    logins_path = os.path.join(PROCESSED_DIR, "dionaea_logins.csv")
    if os.path.exists(logins_path):
        data["logins"] = pd.read_csv(logins_path, parse_dates=["timestamp"])
        print(f"Loaded Dionaea logins: {len(data['logins'])} events")
    
    # Load Dionaea downloads
    downloads_path = os.path.join(PROCESSED_DIR, "dionaea_downloads.csv")
    if os.path.exists(downloads_path):
        data["downloads"] = pd.read_csv(downloads_path, parse_dates=["timestamp"])
        print(f"Loaded Dionaea downloads: {len(data['downloads'])} events")
    
    return data


def build_unified_timeline(data):
    """
    Build a unified timeline of all events from both honeypots.
    Each event is tagged with its source honeypot for comparison.
    """
    
    timeline_records = []
    
    # Process Cowrie events
    if "cowrie" in data:
        for _, row in data["cowrie"].iterrows():
            record = {
                "timestamp": row["timestamp"],
                "source": "cowrie",
                "src_ip": row["src_ip"],
                "attacker_role": row.get("attacker_role", "unknown"),
                "event_type": row["event_type"],
                "event_category": row.get("event_category", "other"),
                "service": "SSH/Telnet",
                "detail": row.get("input") or row.get("message") or ""
            }
            timeline_records.append(record)
    
    # Process Dionaea connections
    if "dionaea" in data:
        for _, row in data["dionaea"].iterrows():
            record = {
                "timestamp": row["timestamp"],
                "source": "dionaea",
                "src_ip": row["src_ip"],
                "attacker_role": row.get("attacker_role", "unknown"),
                "event_type": "connection",
                "event_category": "connection",
                "service": row.get("service", "unknown"),
                "detail": f"Port {row.get('dst_port', 'unknown')}"
            }
            timeline_records.append(record)
    
    # Process Dionaea logins
    if "logins" in data:
        for _, row in data["logins"].iterrows():
            username = row.get("username", "")
            password = row.get("password", "")
            record = {
                "timestamp": row["timestamp"],
                "source": "dionaea",
                "src_ip": row["src_ip"],
                "attacker_role": row.get("attacker_role", "unknown"),
                "event_type": "login_attempt",
                "event_category": "authentication",
                "service": row.get("service", "unknown"),
                "detail": f"{username}:{password}"
            }
            timeline_records.append(record)
    
    # Process Dionaea downloads
    if "downloads" in data:
        for _, row in data["downloads"].iterrows():
            record = {
                "timestamp": row["timestamp"],
                "source": "dionaea",
                "src_ip": row["src_ip"],
                "attacker_role": row.get("attacker_role", "unknown"),
                "event_type": "malware_download",
                "event_category": "file_transfer",
                "service": "HTTP",
                "detail": row.get("md5_hash", "")[:16] if row.get("md5_hash") else ""
            }
            timeline_records.append(record)
    
    # Create DataFrame and normalize timestamps
    timeline_df = pd.DataFrame(timeline_records)
    
    # Convert all timestamps to timezone-naive for consistent comparison
    timeline_df["timestamp"] = pd.to_datetime(timeline_df["timestamp"], utc=True)
    timeline_df["timestamp"] = timeline_df["timestamp"].dt.tz_localize(None)
    
    timeline_df = timeline_df.sort_values("timestamp").reset_index(drop=True)
    
    return timeline_df


def identify_attack_sessions(timeline_df, window_seconds=CORRELATION_WINDOW):
    """
    Group events into attack sessions based on source IP and time proximity.
    Events from the same IP within the time window are considered part of the same session.
    """
    
    if timeline_df.empty:
        return timeline_df
    
    timeline_df = timeline_df.sort_values(["src_ip", "timestamp"]).reset_index(drop=True)
    
    session_ids = []
    current_session = 0
    prev_ip = None
    prev_time = None
    
    for _, row in timeline_df.iterrows():
        current_ip = row["src_ip"]
        current_time = row["timestamp"]
        
        # Start new session if IP changed or time gap exceeded
        if prev_ip != current_ip:
            current_session += 1
        elif prev_time is not None and pd.notna(current_time) and pd.notna(prev_time):
            time_diff = (current_time - prev_time).total_seconds()
            if time_diff > window_seconds:
                current_session += 1
        
        session_ids.append(current_session)
        prev_ip = current_ip
        prev_time = current_time
    
    timeline_df["session_id"] = session_ids
    
    # Re-sort by timestamp for chronological view
    timeline_df = timeline_df.sort_values("timestamp").reset_index(drop=True)
    
    return timeline_df


def analyze_cross_honeypot_activity(timeline_df):
    """
    Identify attackers that targeted both honeypots.
    This shows attack patterns that span multiple services.
    """
    
    results = {
        "multi_honeypot_ips": [],
        "cowrie_only_ips": [],
        "dionaea_only_ips": [],
        "attack_patterns": []
    }
    
    # Group by source IP
    ip_groups = timeline_df.groupby("src_ip")
    
    for ip, group in ip_groups:
        sources = group["source"].unique()
        
        if len(sources) > 1:
            # This IP attacked both honeypots
            results["multi_honeypot_ips"].append({
                "ip": ip,
                "role": group["attacker_role"].iloc[0],
                "cowrie_events": len(group[group["source"] == "cowrie"]),
                "dionaea_events": len(group[group["source"] == "dionaea"]),
                "first_seen": group["timestamp"].min(),
                "last_seen": group["timestamp"].max(),
                "services_targeted": group["service"].nunique()
            })
        elif "cowrie" in sources:
            results["cowrie_only_ips"].append(ip)
        else:
            results["dionaea_only_ips"].append(ip)
    
    return results


def generate_attack_sequence(timeline_df, src_ip):
    """
    Generate the attack sequence for a specific IP address.
    Shows the chronological order of actions taken by the attacker.
    """
    
    ip_events = timeline_df[timeline_df["src_ip"] == src_ip].copy()
    ip_events = ip_events.sort_values("timestamp")
    
    sequence = []
    for _, row in ip_events.iterrows():
        step = {
            "time": row["timestamp"],
            "honeypot": row["source"],
            "action": row["event_type"],
            "service": row["service"],
            "detail": row["detail"][:50] if row["detail"] else ""
        }
        sequence.append(step)
    
    return sequence


def calculate_attack_statistics(timeline_df):
    """Calculate summary statistics for the correlated data."""
    
    stats = {
        "total_events": len(timeline_df),
        "unique_ips": timeline_df["src_ip"].nunique(),
        "unique_sessions": timeline_df["session_id"].nunique() if "session_id" in timeline_df.columns else 0,
        "time_range": {
            "start": timeline_df["timestamp"].min(),
            "end": timeline_df["timestamp"].max()
        },
        "events_by_source": timeline_df["source"].value_counts().to_dict(),
        "events_by_category": timeline_df["event_category"].value_counts().to_dict(),
        "events_by_role": timeline_df["attacker_role"].value_counts().to_dict(),
        "services_targeted": timeline_df["service"].value_counts().to_dict()
    }
    
    return stats


def export_correlated_data(timeline_df, cross_activity, stats):
    """Export all correlated data to CSV files."""
    
    # Export unified timeline
    timeline_path = os.path.join(PROCESSED_DIR, "unified_timeline.csv")
    timeline_df.to_csv(timeline_path, index=False)
    print(f"Saved: {timeline_path}")
    
    # Export multi-honeypot attackers
    if cross_activity["multi_honeypot_ips"]:
        multi_df = pd.DataFrame(cross_activity["multi_honeypot_ips"])
        multi_path = os.path.join(PROCESSED_DIR, "multi_honeypot_attackers.csv")
        multi_df.to_csv(multi_path, index=False)
        print(f"Saved: {multi_path}")
    
    # Export session summary
    if "session_id" in timeline_df.columns:
        session_summary = timeline_df.groupby("session_id").agg({
            "timestamp": ["min", "max"],
            "src_ip": "first",
            "attacker_role": "first",
            "source": lambda x: ",".join(x.unique()),
            "event_type": "count"
        }).reset_index()
        session_summary.columns = ["session_id", "start_time", "end_time", 
                                    "src_ip", "attacker_role", "honeypots", "event_count"]
        session_path = os.path.join(PROCESSED_DIR, "attack_sessions.csv")
        session_summary.to_csv(session_path, index=False)
        print(f"Saved: {session_path}")
    
    return timeline_path


def main():
    """Main function to run log correlation analysis."""
    
    print("=" * 60)
    print("Log Correlation Engine")
    print("=" * 60)
    
    # Load processed data
    print("\n[1/5] Loading processed data...")
    data = load_processed_data()
    
    if not data:
        print("Error: No processed data found. Run process_data.py first.")
        return
    
    # Build unified timeline
    print("\n[2/5] Building unified timeline...")
    timeline_df = build_unified_timeline(data)
    print(f"Created timeline with {len(timeline_df)} events")
    
    # Identify attack sessions
    print("\n[3/5] Identifying attack sessions...")
    timeline_df = identify_attack_sessions(timeline_df)
    print(f"Identified {timeline_df['session_id'].nunique()} attack sessions")
    
    # Analyze cross-honeypot activity
    print("\n[4/5] Analyzing cross-honeypot activity...")
    cross_activity = analyze_cross_honeypot_activity(timeline_df)
    
    print(f"  Multi-honeypot attackers: {len(cross_activity['multi_honeypot_ips'])}")
    print(f"  Cowrie-only attackers: {len(cross_activity['cowrie_only_ips'])}")
    print(f"  Dionaea-only attackers: {len(cross_activity['dionaea_only_ips'])}")
    
    # Calculate statistics
    stats = calculate_attack_statistics(timeline_df)
    
    # Export results
    print("\n[5/5] Exporting correlated data...")
    export_correlated_data(timeline_df, cross_activity, stats)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Correlation Summary")
    print("=" * 60)
    print(f"\nTotal correlated events: {stats['total_events']}")
    print(f"Unique source IPs: {stats['unique_ips']}")
    print(f"Attack sessions: {stats['unique_sessions']}")
    print(f"\nEvents by honeypot:")
    for source, count in stats["events_by_source"].items():
        print(f"  {source}: {count}")
    print(f"\nEvents by attacker role:")
    for role, count in stats["events_by_role"].items():
        print(f"  {role}: {count}")
    
    # Show multi-honeypot attacker details
    if cross_activity["multi_honeypot_ips"]:
        print(f"\nMulti-honeypot attackers:")
        for attacker in cross_activity["multi_honeypot_ips"]:
            print(f"  {attacker['ip']} ({attacker['role']}): "
                  f"{attacker['cowrie_events']} Cowrie + {attacker['dionaea_events']} Dionaea events")
    
    print(f"\nOutput saved to: {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
