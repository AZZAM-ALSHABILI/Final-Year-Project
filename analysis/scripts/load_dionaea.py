# Load and process Dionaea honeypot SQLite database.

import sqlite3
import pandas as pd
from datetime import datetime
from config import DIONAEA_DB, ATTACKER_IPS


def load_dionaea_connections(db_path=DIONAEA_DB):
    """Load connections table from Dionaea SQLite database."""
    conn = sqlite3.connect(db_path)
    
    query = """
    SELECT 
        connection,
        connection_timestamp,
        connection_protocol,
        remote_host,
        remote_port,
        local_port,
        connection_type
    FROM connections
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df


def load_dionaea_logins(db_path=DIONAEA_DB):
    """Load logins table joined with connections for timestamp and IP."""
    conn = sqlite3.connect(db_path)
    
    query = """
    SELECT 
        l.login,
        l.connection,
        l.login_username as username,
        l.login_password as password,
        c.connection_timestamp,
        c.connection_protocol as protocol,
        c.remote_host as src_ip,
        c.local_port as dst_port
    FROM logins l
    JOIN connections c ON l.connection = c.connection
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df


def load_dionaea_downloads(db_path=DIONAEA_DB):
    """Load downloads table joined with connections."""
    conn = sqlite3.connect(db_path)
    
    query = """
    SELECT 
        d.download,
        d.connection,
        d.download_url as url,
        d.download_md5_hash as md5_hash,
        c.connection_timestamp,
        c.connection_protocol as protocol,
        c.remote_host as src_ip
    FROM downloads d
    JOIN connections c ON d.connection = c.connection
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df


def process_dionaea_connections(df):
    """Process raw Dionaea connection data."""
    
    # Convert Unix timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["connection_timestamp"], unit="s", errors="coerce")
    
    # Add hour column for time analysis
    df["hour"] = df["timestamp"].dt.hour
    
    # Rename columns for consistency
    df = df.rename(columns={
        "connection_protocol": "protocol",
        "remote_host": "src_ip",
        "remote_port": "src_port",
        "local_port": "dst_port"
    })
    
    # Map source IP to attacker role
    df["attacker_role"] = df["src_ip"].map(ATTACKER_IPS).fillna("unknown")
    
    # Map port to service name
    df["service"] = df["dst_port"].apply(map_port_to_service)
    
    # Drop the original timestamp column
    df = df.drop(columns=["connection_timestamp"], errors="ignore")
    
    return df


def process_dionaea_logins(df):
    """Process Dionaea login data."""
    
    # Convert Unix timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["connection_timestamp"], unit="s", errors="coerce")
    df["hour"] = df["timestamp"].dt.hour
    
    # Map source IP to attacker role
    df["attacker_role"] = df["src_ip"].map(ATTACKER_IPS).fillna("unknown")
    
    # Map port to service
    df["service"] = df["dst_port"].apply(map_port_to_service)
    
    df = df.drop(columns=["connection_timestamp"], errors="ignore")
    
    return df


def process_dionaea_downloads(df):
    """Process Dionaea download data."""
    
    # Convert Unix timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["connection_timestamp"], unit="s", errors="coerce")
    df["hour"] = df["timestamp"].dt.hour
    
    # Map source IP to attacker role
    df["attacker_role"] = df["src_ip"].map(ATTACKER_IPS).fillna("unknown")
    
    df = df.drop(columns=["connection_timestamp"], errors="ignore")
    
    return df


def map_port_to_service(port):
    """Map common ports to service names."""
    port_map = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        80: "HTTP",
        443: "HTTPS",
        445: "SMB",
        1433: "MSSQL",
        1723: "PPTP",
        3306: "MySQL",
        5060: "SIP"
    }
    return port_map.get(port, f"Port-{port}")


def get_dionaea_dataframe():
    """Main function to load and process Dionaea connection data."""
    print("Loading Dionaea database...")
    df = load_dionaea_connections()
    print(f"Loaded {len(df)} connections")
    
    print("Processing data...")
    df = process_dionaea_connections(df)
    print(f"Created DataFrame with {len(df)} records")
    
    return df


def get_dionaea_logins():
    """Load and process Dionaea login data."""
    print("Loading Dionaea logins...")
    df = load_dionaea_logins()
    print(f"Loaded {len(df)} logins")
    
    df = process_dionaea_logins(df)
    return df


def get_dionaea_downloads():
    """Load and process Dionaea download data."""
    print("Loading Dionaea downloads...")
    df = load_dionaea_downloads()
    print(f"Loaded {len(df)} downloads")
    
    df = process_dionaea_downloads(df)
    return df


if __name__ == "__main__":
    # Test connections
    df = get_dionaea_dataframe()
    print("\nConnections sample:")
    print(df.head())
    
    # Test logins
    logins = get_dionaea_logins()
    print("\nLogins sample:")
    print(logins.head())
    
    # Test downloads
    downloads = get_dionaea_downloads()
    print("\nDownloads sample:")
    print(downloads.head())
