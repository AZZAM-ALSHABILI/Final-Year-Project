"""
Main data processing script for honeypot analysis.
Loads data from both Cowrie and Dionaea, processes it, and saves to CSV.
"""

import os
import sys

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import PROCESSED_DIR
from load_cowrie import get_cowrie_dataframe
from load_dionaea import get_dionaea_dataframe, get_dionaea_logins, get_dionaea_downloads


def main():
    """Main function to process all honeypot data."""
    
    print("=" * 50)
    print("Honeypot Data Processing")
    print("=" * 50)
    
    # Process Cowrie data
    print("\n[1/4] Processing Cowrie data...")
    try:
        cowrie_df = get_cowrie_dataframe()
        cowrie_output = os.path.join(PROCESSED_DIR, "cowrie_processed.csv")
        cowrie_df.to_csv(cowrie_output, index=False, escapechar='\\')
        print(f"Saved: {cowrie_output}")
    except Exception as e:
        print(f"Error processing Cowrie: {e}")
        cowrie_df = None
    
    # Process Dionaea connections
    print("\n[2/4] Processing Dionaea connections...")
    try:
        dionaea_df = get_dionaea_dataframe()
        dionaea_output = os.path.join(PROCESSED_DIR, "dionaea_processed.csv")
        dionaea_df.to_csv(dionaea_output, index=False)
        print(f"Saved: {dionaea_output}")
    except Exception as e:
        print(f"Error processing Dionaea connections: {e}")
        dionaea_df = None
    
    # Process Dionaea logins
    print("\n[3/4] Processing Dionaea logins...")
    try:
        logins_df = get_dionaea_logins()
        logins_output = os.path.join(PROCESSED_DIR, "dionaea_logins.csv")
        logins_df.to_csv(logins_output, index=False)
        print(f"Saved: {logins_output}")
    except Exception as e:
        print(f"Error processing Dionaea logins: {e}")
        logins_df = None
    
    # Process Dionaea downloads
    print("\n[4/4] Processing Dionaea downloads...")
    try:
        downloads_df = get_dionaea_downloads()
        downloads_output = os.path.join(PROCESSED_DIR, "dionaea_downloads.csv")
        downloads_df.to_csv(downloads_output, index=False)
        print(f"Saved: {downloads_output}")
    except Exception as e:
        print(f"Error processing Dionaea downloads: {e}")
        downloads_df = None
    
    # Print summary
    print("\n" + "=" * 50)
    print("Processing Complete")
    print("=" * 50)
    
    if cowrie_df is not None:
        print(f"\nCowrie Summary:")
        print(f"  Total events: {len(cowrie_df)}")
        print(f"  Unique source IPs: {cowrie_df['src_ip'].nunique()}")
        print(f"  Event types: {cowrie_df['event_category'].nunique()}")
        downloads = cowrie_df[cowrie_df['event_type'] == 'cowrie.session.file_download']
        print(f"  File downloads: {len(downloads)}")
    
    if dionaea_df is not None:
        print(f"\nDionaea Connections:")
        print(f"  Total connections: {len(dionaea_df)}")
        print(f"  Unique source IPs: {dionaea_df['src_ip'].nunique()}")
        print(f"  Protocols: {dionaea_df['protocol'].nunique()}")
    
    if logins_df is not None:
        print(f"\nDionaea Logins:")
        print(f"  Total login attempts: {len(logins_df)}")
        print(f"  Unique usernames: {logins_df['username'].nunique()}")
    
    if downloads_df is not None:
        print(f"\nDionaea Downloads:")
        print(f"  Total downloads: {len(downloads_df)}")
        print(f"  Unique MD5 hashes: {downloads_df['md5_hash'].nunique()}")
    
    print(f"\nOutput files saved to: {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
