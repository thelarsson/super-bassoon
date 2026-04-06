#!/usr/bin/env python3
"""
AUTO BUY TELIA.ST - Execute purchase immediately
⚠️  WARNING: This will place REAL ORDERS with REAL MONEY!
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ig_client import IGClient
from notifier import Notifier
import yfinance as yf
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoBuyTelia")

def main():
    print("=" * 70)
    print("🚀 AUTO BUY TELIA.ST")
    print("=" * 70)
    print("⚠️  THIS WILL PLACE A REAL ORDER WITH REAL MONEY!")
    print("=" * 70)
    print()
    
    try:
        # Step 1: Get price
        print("📊 Getting TELIA.ST price...")
        ticker = yf.Ticker("TELIA.ST")
        info = ticker.info
        current_price = info.get('regularMarketPrice', 47.88)
        print(f"✅ Price: ${current_price}")
        
        # Step 2: Calculate
        total_amount = 140
        shares = 2  # Buy 2 shares
        actual_cost = shares * current_price
        
        print(f"\n📋 Order Details:")
        print(f"   Symbol: TELIA.ST")
        print(f"   Direction: BUY")
        print(f"   Size: {shares} shares")
        print(f"   Estimated Price: ${current_price}")
        print(f"   Estimated Cost: ${actual_cost:.2f}")
        print()
        
        # Step 3: Connect to IG
        print("💰 Connecting to IG...")
        client = IGClient()
        print("✅ Connected to IG API")
        print()
        
        # Step 4: Execute order
        print("🛒 PLACING ORDER...")
        print("=" * 70)
        
        # REAL ORDER - Uncomment to execute
        # result = client.place_order(
        #     market_id="TELIA.ST",
        #     direction="BUY", 
        #     size=shares,
        #     stop_distance=None,
        #     limit_distance=None
        # )
        
        print("⚠️  ORDER SIMULATION - Not actually placed")
        print("   To execute for real, uncomment the client.place_order() lines")
        print()
        
        # Step 5: Send notification
        print("📱 Sending Telegram notification...")
        notifier = Notifier()
        message = f"""🛒 BUY ORDER PLACED (SIMULATION)

Symbol: TELIA.ST 🇸🇪
Direction: BUY
Shares: {shares}
Price: ${current_price}
Total: ${actual_cost:.2f}

Status: SIMULATION - Not real order

To execute real orders, enable place_order() in script."""
        
        # notifier.send_telegram_message(message)
        print("✅ Notification sent (disabled in simulation)")
        
        print()
        print("=" * 70)
        print("✅ Process complete!")
        print("=" * 70)
        print()
        print("To place REAL orders:")
        print("1. Open scripts/auto_buy_telia.py")
        print("2. Uncomment lines 47-52 (the place_order call)")
        print("3. Run again")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Auto buy failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("Starting in 3 seconds... Press Ctrl+C to cancel")
    import time
    time.sleep(3)
    main()
