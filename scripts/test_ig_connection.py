#!/usr/bin/env python3
"""
Test IG API connection
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ig_client import IGClient
from config import IG_API_KEY, IG_IDENTIFIER, IG_PASSWORD, IG_ACCOUNT_ID

def test_connection():
    print("Testing IG API Connection...")
    print(f"API Key: {IG_API_KEY[:10]}...")
    print(f"Username: {IG_IDENTIFIER}")
    print(f"Account ID: {IG_ACCOUNT_ID}")
    print()
    
    try:
        client = IGClient()
        print("✅ Successfully connected to IG API!")
        
        # Get account info
        account_info = client.get_account_info()
        print(f"\nAccount Info:")
        print(f"  Balance: {account_info}")
        
        # Get positions
        positions = client.get_positions()
        print(f"\nCurrent Positions:")
        if positions:
            for pos in positions:
                print(f"  {pos}")
        else:
            print("  No open positions")
            
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
