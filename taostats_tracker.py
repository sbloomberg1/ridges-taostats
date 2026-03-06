#!/usr/bin/env python3
"""
Taostats API Wallet Staking/Unstaking Activity Tracker

This script queries the Taostats API to track staking and unstaking activity
for a list of wallets over a configurable time period.
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)


class TaostatsTracker:
    """Tracker for wallet staking/unstaking activity via Taostats API."""
    
    DEFAULT_BASE_URL = "https://dash.taostats.io/api"
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the tracker.
        
        Args:
            api_key: Optional API key for authentication
            base_url: Base URL for the Taostats API
        """
        self.api_key = api_key
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "TaostatsTracker/1.0",
            "Accept": "application/json"
        })
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"
    
    def get_staking_activity(
        self, 
        wallet_address: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> list:
        """
        Get staking/unstaking activity for a wallet.
        
        Args:
            wallet_address: The wallet address to query
            start_time: Start of the time range
            end_time: End of the time range
            
        Returns:
            List of activity records
        """
        # Convert datetimes to timestamps
        start_ts = int(start_time.timestamp())
        end_ts = int(end_time.timestamp())
        
        # Try multiple possible endpoint patterns
        endpoints_to_try = [
            f"{self.base_url}/account/{wallet_address}/history",
            f"{self.base_url}/wallet/{wallet_address}/staking",
            f"{self.base_url}/account/{wallet_address}/staking",
            f"{self.base_url}/staking/history",
            f"{self.base_url}/wallet/{wallet_address}/activity",
        ]
        
        params = {
            "address": wallet_address,
            "start": start_ts,
            "end": end_ts,
            "type": "staking"
        }
        
        last_error = None
        for endpoint in endpoints_to_try:
            try:
                response = self.session.get(endpoint, params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    # Handle different response formats
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict):
                        return data.get("data", data.get("results", data.get("items", [])))
                    return []
                elif response.status_code != 404:
                    # Only track non-404 errors
                    last_error = f"HTTP {response.status_code}: {response.text[:200]}"
            except Exception as e:
                last_error = str(e)
                continue
        
        if last_error:
            print(f"Warning: Could not fetch data for {wallet_address}: {last_error}")
        return []
    
    def filter_by_time_range(
        self, 
        activities: list, 
        start_time: datetime, 
        end_time: datetime
    ) -> list:
        """
        Filter activities by time range.
        
        Args:
            activities: List of activity records
            start_time: Start of the time range
            end_time: End of the time range
            
        Returns:
            Filtered list of activities
        """
        filtered = []
        for activity in activities:
            # Try to extract timestamp from various field names
            timestamp = None
            for field in ["timestamp", "time", "created_at", "block_time", "date"]:
                if field in activity:
                    ts = activity[field]
                    if isinstance(ts, (int, float)):
                        timestamp = datetime.fromtimestamp(ts, tz=timezone.utc)
                    elif isinstance(ts, str):
                        try:
                            timestamp = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        except ValueError:
                            continue
                    break
            
            if timestamp and start_time <= timestamp <= end_time:
                activity["_parsed_time"] = timestamp.isoformat()
                filtered.append(activity)
                
        return filtered
    
    def format_activity(self, activity: dict, wallet_address: str) -> dict:
        """
        Format activity record for output.
        
        Args:
            activity: Raw activity record
            wallet_address: Wallet address
            
        Returns:
            Formatted activity record
        """
        # Extract balance information if available
        staked = activity.get("balance_staked", 0)
        staked_alpha = activity.get("balance_staked_alpha_as_tao", staked)
        staked_root = activity.get("balance_staked_root", 0)
        total_staked = staked_alpha + staked_root
        
        # Determine activity type based on available fields
        act_type = "balance_snapshot"
        if "balance_staked" in activity:
            act_type = "staking_balance"
        if activity.get("type"):
            act_type = activity.get("type")
        
        return {
            "wallet": wallet_address,
            "type": act_type,
            "amount": total_staked if total_staked else activity.get("amount", activity.get("value", "N/A")),
            "timestamp": activity.get("_parsed_time", activity.get("timestamp", activity.get("time", "N/A"))),
            "block": activity.get("block", activity.get("block_number", "N/A")),
            "extrinsic_id": activity.get("extrinsic_id", activity.get("tx_hash", "N/A")),
            "validator": activity.get("validator", activity.get("hotkey", "N/A")),
            "netuid": activity.get("netuid", activity.get("subnet", "N/A")),
            "balance_free": activity.get("balance_free", "N/A"),
            "balance_staked": activity.get("balance_staked", "N/A"),
            "raw_data": activity
        }


def parse_datetime(date_string: str) -> datetime:
    """Parse a datetime string in various formats."""
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_string, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    
    # Try ISO format
    try:
        return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
    except ValueError:
        pass
    
    raise ValueError(f"Unable to parse date: {date_string}. Use YYYY-MM-DD format.")


def load_wallets(wallet_input: str) -> list:
    """Load wallet addresses from file or comma-separated string."""
    wallets = []
    
    # Try to read as file first
    try:
        with open(wallet_input, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    wallets.append(line)
        return wallets
    except FileNotFoundError:
        pass
    
    # Treat as comma-separated list
    wallets = [w.strip() for w in wallet_input.split(",") if w.strip()]
    return wallets


def output_results(activities: list, output_format: str, output_file: Optional[str] = None):
    """Output results in the specified format."""
    if output_format == "json":
        output = json.dumps(activities, indent=2)
        if output_file:
            with open(output_file, "w") as f:
                f.write(output)
            print(f"Results saved to {output_file}")
        else:
            print(output)
    
    elif output_format == "csv":
        if not activities:
            print("No activities found.")
            return
        
        fieldnames = ["wallet", "type", "amount", "timestamp", "block", "extrinsic_id", "validator", "netuid"]
        
        if output_file:
            with open(output_file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for activity in activities:
                    writer.writerow({k: activity.get(k, "N/A") for k in fieldnames})
            print(f"Results saved to {output_file}")
        else:
            import io
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for activity in activities:
                writer.writerow({k: activity.get(k, "N/A") for k in fieldnames})
            print(output.getvalue())
    
    else:  # table format
        if not activities:
            print("No activities found.")
            return
        
        print("\n" + "="*120)
        print(f"{'Wallet':<50} {'Type':<12} {'Amount':<20} {'Timestamp':<25} {'Block':<10}")
        print("="*120)
        
        for activity in activities:
            wallet = activity.get("wallet", "N/A")[:48]
            act_type = activity.get("type", "N/A")[:10]
            amount = str(activity.get("amount", "N/A"))[:18]
            timestamp = activity.get("timestamp", "N/A")[:23]
            block = str(activity.get("block", "N/A"))[:8]
            print(f"{wallet:<50} {act_type:<12} {amount:<20} {timestamp:<25} {block:<10}")
        
        print("="*120)
        print(f"Total activities: {len(activities)}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Track wallet staking/unstaking activity via Taostats API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --wallets wallets.txt --start 2024-01-01 --end 2024-12-31
  %(prog)s --wallets 5C4hrfjw... --start "2024-01-01 00:00:00" --end "2024-12-31 23:59:59"
  %(prog)s --wallets wallets.txt --start 2024-01-01 --days 30 --format csv --output results.csv
        """
    )
    
    parser.add_argument(
        "--wallets", "-w",
        required=True,
        help="Path to file containing wallet addresses (one per line) or comma-separated list"
    )
    
    parser.add_argument(
        "--start", "-s",
        help="Start date/time (e.g., 2024-01-01 or 2024-01-01T00:00:00)"
    )
    
    parser.add_argument(
        "--end", "-e",
        help="End date/time (e.g., 2024-12-31 or 2024-12-31T23:59:59)"
    )
    
    parser.add_argument(
        "--days", "-d",
        type=int,
        help="Number of days to look back (alternative to --start)"
    )
    
    parser.add_argument(
        "--api-key", "-k",
        help="API key for Taostats API (if required)"
    )
    
    parser.add_argument(
        "--api-url",
        default="https://dash.taostats.io/api",
        help="Base URL for Taostats API (default: %(default)s)"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: %(default)s)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file path (optional, prints to stdout if not specified)"
    )
    
    args = parser.parse_args()
    
    # Validate time arguments
    if args.days:
        end_time = datetime.now(timezone.utc)
        from datetime import timedelta
        start_time = end_time - timedelta(days=args.days)
    elif args.start and args.end:
        start_time = parse_datetime(args.start)
        end_time = parse_datetime(args.end)
    else:
        parser.error("Either --days or both --start and --end must be specified")
    
    if start_time > end_time:
        parser.error("Start time must be before end time")
    
    # Load wallets
    wallets = load_wallets(args.wallets)
    if not wallets:
        parser.error("No wallet addresses provided")
    
    print(f"Tracking {len(wallets)} wallet(s)")
    print(f"Time range: {start_time.isoformat()} to {end_time.isoformat()}")
    print(f"API URL: {args.api_url}")
    print("-" * 60)
    
    # Initialize tracker
    tracker = TaostatsTracker(api_key=args.api_key, base_url=args.api_url)
    
    # Fetch and process activities
    all_activities = []
    for wallet in wallets:
        print(f"Fetching activity for {wallet}...", end=" ", flush=True)
        try:
            activities = tracker.get_staking_activity(wallet, start_time, end_time)
            print(f"found {len(activities)} records")
            
            filtered = tracker.filter_by_time_range(activities, start_time, end_time)
            
            for activity in filtered:
                formatted = tracker.format_activity(activity, wallet)
                all_activities.append(formatted)
        except Exception as e:
            print(f"ERROR: {e}")
            continue
    
    # Output results
    print(f"\nTotal activities found: {len(all_activities)}")
    output_results(all_activities, args.format, args.output)


if __name__ == "__main__":
    main()
