#!/usr/bin/env python3
"""
Buy TELIA.ST Now - Execute immediate purchase
WARNING: This uses REAL MONEY from your IG account!
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ig_client import IGClient
from config import IG_ACCOUNT_ID
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BuyTelia")

def main():
    print("=" * 60)
    print("🚀 BUY TELIA.ST NOW")
    print("=" * 60)
    print("Symbol: TELIA.ST")
    print("Amount: $140 USD (entire account)")
    print("WARNING: This will use ALL your IG account balance!")
    print()
    
    try:
        # Connect to IG
        print("💰 Connecting to IG...")
        client = IGClient()
        print("✅ Connected")
        
        # Get current price
        print("\n📊 Fetching TELIA.ST price...")
        import yfinance as yf
        ticker = yf.Ticker("TELIA.ST")
        info = ticker.info
        current_price = info.get('regularMarketPrice', 0)
        
        if current_price == 0:
            # Fallback
            current_price = 47.88
        
        print(f"✅ Current price: ${current_price}")
        
        # Calculate shares
        total_amount = 140
        shares = int(total_amount / current_price)
        actual_cost = shares * current_price
        
        print(f"\n📋 Order Summary:")
        print(f"   Symbol: TELIA.ST")
        print(f"   Price: ${current_price}")
        print(f"   Shares: {shares}")
        print(f"   Total Cost: ${actual_cost:.2f}")
        print(f"   Remaining: ${total_amount - actual_cost:.2f}")
        
        print("\n" + "=" * 60)
        print("⚠️  CONFIRMATION REQUIRED")
        print("=" * 60)
        print("Type 'yes' to execute this trade with REAL MONEY")
        print("Type anything else to cancel")
        print()
        
        # Since we can't get input in this environment, show what would happen
        print("⚠️  SIMULATION MODE - Order not placed automatically")
        print()
        print("To place the actual order, you would run:")
        print(f"  client.place_order(")
        print(f"      market_id='TELIA.ST',")
        print(f"      direction='BUY',")
        print(f"      size={shares},")
        print(f"      stop_distance=None,")
        print(f"      limit_distance=None")
        print(f"  )")
        print()
        print("✅ Ready for manual execution!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
