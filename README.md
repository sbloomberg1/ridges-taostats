# Taostats Wallet Activity Tracker

A Python script that queries the Taostats API to track wallet staking/unstaking activity over a configurable time period.

## Features

- Track multiple wallets simultaneously
- Configurable time range (absolute dates or relative days)
- Multiple output formats: table, CSV, JSON
- Support for Taostats API key authentication
- Automatic endpoint detection and failover
- Balance history tracking for staking analysis

## Installation

1. Install Python 3.8 or higher
2. Install required dependencies:
   ```bash
   pip install requests
   ```

## Usage

### Basic Usage

Track wallet activity for the last 7 days:
```bash
python taostats_tracker.py --wallets <wallet_address> --days 7
```

Track multiple wallets from a file:
```bash
python taostats_tracker.py --wallets wallets.txt --days 30
```

### Time Range Options

**Option 1: Relative time (days)**
```bash
python taostats_tracker.py --wallets wallets.txt --days 30
```

**Option 2: Absolute date range**
```bash
python taostats_tracker.py --wallets wallets.txt --start 2024-01-01 --end 2024-12-31
```

**Option 3: With time**
```bash
python taostats_tracker.py --wallets wallets.txt --start "2024-01-01 00:00:00" --end "2024-01-31 23:59:59"
```

### Output Formats

**Table format (default):**
```bash
python taostats_tracker.py --wallets wallets.txt --days 7 --format table
```

**CSV output:**
```bash
python taostats_tracker.py --wallets wallets.txt --days 7 --format csv --output results.csv
```

**JSON output:**
```bash
python taostats_tracker.py --wallets wallets.txt --days 7 --format json --output results.json
```

### Advanced Options

**Use custom API URL:**
```bash
python taostats_tracker.py --wallets wallets.txt --days 7 --api-url https://custom.taostats.io/api
```

**With API key (if required):**
```bash
python taostats_tracker.py --wallets wallets.txt --days 7 --api-key YOUR_API_KEY
```

## Wallet Input Format

The script accepts wallet addresses in two ways:

1. **Comma-separated list:**
   ```bash
   python taostats_tracker.py --wallets "5C4hrfjw9...,5D5QK3sQs5..." --days 7
   ```

2. **File with one address per line:**
   ```bash
   python taostats_tracker.py --wallets wallets.txt --days 7
   ```

   Example `wallets.txt`:
   ```
   # My wallets
   5C4hrfjw9DjXZTzV3MwzrrAr9P1MJhSrvWGWqi1eSuyUpnhM
   5D5QK3sQs5uD9n7U3gFh8RKMj9j2J2VJkV7m9YcT4hH5tR6
   ```

## Date/Time Formats

The following date/time formats are supported:
- `YYYY-MM-DD` (e.g., 2024-01-01)
- `YYYY-MM-DD HH:MM` (e.g., 2024-01-01 14:30)
- `YYYY-MM-DD HH:MM:SS` (e.g., 2024-01-01 14:30:00)
- `YYYY-MM-DDTHH:MM:SS` (e.g., 2024-01-01T14:30:00)
- `YYYY-MM-DDTHH:MM:SSZ` (e.g., 2024-01-01T14:30:00Z)

All times are interpreted as UTC.

## Output Fields

The script outputs the following fields for each activity:

| Field | Description |
|-------|-------------|
| wallet | Wallet address |
| type | Activity type (staking_balance, etc.) |
| amount | Staked amount (in rao/tao units) |
| timestamp | ISO 8601 timestamp |
| block | Block number |
| extrinsic_id | Transaction/extrinsic ID |
| validator | Validator hotkey (if applicable) |
| netuid | Subnet ID (if applicable) |
| balance_free | Free balance |
| balance_staked | Staked balance |

## API Endpoints

The script attempts to connect to the following Taostats API endpoints in order:
1. `/api/account/{wallet}/history` - Balance history
2. `/api/wallet/{wallet}/staking` - Staking activity
3. `/api/account/{wallet}/staking` - Account staking
4. `/api/staking/history` - General staking history
5. `/api/wallet/{wallet}/activity` - Wallet activity

## Examples

### Example 1: Track single wallet for 30 days
```bash
python taostats_tracker.py --wallets 5C4hrfjw9DjXZTzV3MwzrrAr9P1MJhSrvWGWqi1eSuyUpnhM --days 30
```

### Example 2: Export to CSV
```bash
python taostats_tracker.py --wallets wallets.txt --start 2024-01-01 --end 2024-03-01 --format csv --output q1_staking.csv
```

### Example 3: JSON output for programmatic processing
```bash
python taostats_tracker.py --wallets wallets.txt --days 7 --format json | jq '.[] | {wallet, amount, timestamp}'
```

## Troubleshooting

**API returns 404 or 500 errors:**
- The Taostats API endpoints may have changed
- Try updating the `--api-url` parameter
- Check if API key is required

**No activities found:**
- Verify the wallet address is correct
- Check that the time range includes activity
- Try extending the time range

**Rate limiting:**
- Add delays between requests (modify script)
- Use API key if available

## License

MIT License - Feel free to modify and distribute.
