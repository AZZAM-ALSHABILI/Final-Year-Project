#Load and process Cowrie honeypot JSON logs.

import json
import pandas as pd
from datetime import datetime
from config import COWRIE_LOG, ATTACKER_IPS


def load_cowrie_logs(filepath=COWRIE_LOG):
    """Read Cowrie JSON log file and return list of events."""
    events = []
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    event = json.loads(line)
                    events.append(event)
                except json.JSONDecodeError:
                    continue
    
    return events


def process_cowrie_events(events):
    """Process raw events into a structured DataFrame."""
    records = []
    
    for event in events:
        record = {
            "timestamp": event.get("timestamp"),
            "event_type": event.get("eventid", ""),
            "src_ip": event.get("src_ip"),
            "src_port": event.get("src_port"),
            "dst_port": event.get("dst_port"),
            "session": event.get("session"),
            "username": event.get("username"),
            "password": event.get("password"),
            "input": event.get("input"),
            "message": event.get("message"),
            "protocol": event.get("protocol"),
            "shasum": event.get("shasum"),
            "destfile": event.get("destfile")
        }
        records.append(record)
    
    df = pd.DataFrame(records)
    
    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    
    # Add hour column for time analysis
    df["hour"] = df["timestamp"].dt.hour
    
    # Map source IP to attacker role
    df["attacker_role"] = df["src_ip"].map(ATTACKER_IPS).fillna("unknown")
    
    # Categorize event types
    df["event_category"] = df["event_type"].apply(categorize_event)
    
    return df


def categorize_event(event_type):
    """Categorize Cowrie events into broader categories."""
    if pd.isna(event_type):
        return "other"
    
    event_type = str(event_type).lower()
    
    if "login" in event_type:
        return "authentication"
    elif "command" in event_type:
        return "command"
    elif "session" in event_type:
        return "session"
    elif "client" in event_type:
        return "client_info"
    elif "download" in event_type:
        return "file_transfer"
    else:
        return "other"


def get_cowrie_dataframe():
    """Main function to load and process Cowrie data."""
    print("Loading Cowrie logs...")
    events = load_cowrie_logs()
    print(f"Loaded {len(events)} events")
    
    print("Processing events...")
    df = process_cowrie_events(events)
    print(f"Created DataFrame with {len(df)} records")
    
    return df


if __name__ == "__main__":
    df = get_cowrie_dataframe()
    print("\nSample data:")
    print(df.head())
    print("\nColumns:", df.columns.tolist())
    print("\nEvent categories:")
    print(df["event_category"].value_counts())
    print("\nFile downloads:")
    downloads = df[df["event_type"] == "cowrie.session.file_download"]
    print(f"Total: {len(downloads)}")
