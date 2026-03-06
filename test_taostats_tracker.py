#!/usr/bin/env python3
"""
Unit tests for the Taostats Wallet Activity Tracker
"""

import unittest
from datetime import datetime, timezone
from taostats_tracker import TaostatsTracker, parse_datetime, load_wallets
import tempfile
import os


class TestTaostatsTracker(unittest.TestCase):
    """Test cases for TaostatsTracker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = TaostatsTracker()
    
    def test_initialization(self):
        """Test tracker initialization."""
        self.assertEqual(self.tracker.base_url, "https://dash.taostats.io/api")
        self.assertIsNone(self.tracker.api_key)
        
        # Test with custom base URL
        custom_tracker = TaostatsTracker(base_url="https://custom.api.com")
        self.assertEqual(custom_tracker.base_url, "https://custom.api.com")
        
        # Test with API key
        key_tracker = TaostatsTracker(api_key="test_key")
        self.assertEqual(key_tracker.api_key, "test_key")
        self.assertEqual(
            key_tracker.session.headers.get("Authorization"),
            "Bearer test_key"
        )
    
    def test_filter_by_time_range(self):
        """Test time range filtering."""
        start_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_time = datetime(2024, 1, 31, tzinfo=timezone.utc)
        
        activities = [
            {"timestamp": "2024-01-15T10:00:00Z", "type": "stake"},
            {"timestamp": "2024-02-15T10:00:00Z", "type": "stake"},  # Outside range
            {"timestamp": "2024-01-20T10:00:00Z", "type": "unstake"},
            {"time": 1704751200, "type": "stake"},  # 2024-01-09
        ]
        
        filtered = self.tracker.filter_by_time_range(
            activities, start_time, end_time
        )
        
        # Should include 3 activities within range
        self.assertEqual(len(filtered), 3)
    
    def test_format_activity(self):
        """Test activity formatting."""
        wallet = "5TestWallet123456789"
        activity = {
            "timestamp": "2024-01-15T10:00:00Z",
            "block_number": 12345,
            "balance_staked": 1000000,
            "balance_free": 5000000,
            "type": "stake"
        }
        
        formatted = self.tracker.format_activity(activity, wallet)
        
        self.assertEqual(formatted["wallet"], wallet)
        self.assertEqual(formatted["type"], "stake")
        self.assertEqual(formatted["block"], 12345)
        self.assertEqual(formatted["balance_staked"], 1000000)
        self.assertEqual(formatted["balance_free"], 5000000)


class TestParseDatetime(unittest.TestCase):
    """Test cases for parse_datetime function."""
    
    def test_date_only(self):
        """Test parsing date only."""
        result = parse_datetime("2024-01-15")
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 15)
    
    def test_datetime_with_time(self):
        """Test parsing datetime with time."""
        result = parse_datetime("2024-01-15 14:30:00")
        self.assertEqual(result.hour, 14)
        self.assertEqual(result.minute, 30)
    
    def test_iso_format(self):
        """Test parsing ISO format."""
        result = parse_datetime("2024-01-15T14:30:00Z")
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.hour, 14)
    
    def test_invalid_date(self):
        """Test parsing invalid date raises error."""
        with self.assertRaises(ValueError):
            parse_datetime("invalid-date")


class TestLoadWallets(unittest.TestCase):
    """Test cases for load_wallets function."""
    
    def test_comma_separated(self):
        """Test loading comma-separated wallets."""
        wallets = load_wallets("addr1, addr2, addr3")
        self.assertEqual(len(wallets), 3)
        self.assertEqual(wallets, ["addr1", "addr2", "addr3"])
    
    def test_single_wallet(self):
        """Test loading single wallet."""
        wallets = load_wallets("single_wallet_address")
        self.assertEqual(len(wallets), 1)
        self.assertEqual(wallets[0], "single_wallet_address")
    
    def test_from_file(self):
        """Test loading wallets from file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("# Comment line\n")
            f.write("wallet1\n")
            f.write("wallet2\n")
            f.write("\n")  # Empty line
            f.write("wallet3\n")
            temp_path = f.name
        
        try:
            wallets = load_wallets(temp_path)
            self.assertEqual(len(wallets), 3)
            self.assertEqual(wallets, ["wallet1", "wallet2", "wallet3"])
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()
