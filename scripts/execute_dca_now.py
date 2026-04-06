#!/usr/bin/env python3
"""
Execute DCA Buy Now - Force the monthly DCA purchase immediately
WARNING: This uses REAL MONEY from your IG account!
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from strategy import Strategy
from ig_client import IGClient
from config import IG_ACCOUNT_ID
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ExecuteDCA")

def main():
    print("=" * 60)
    print("🚀 FORCE DCA EXECUTION NOW")
    print("=" * 60)
    print("This will execute the DCA strategy immediately")
    print("using REAL MONEY from your IG account!")
    print()
    
    try:
        # Step 1: Generate buy plan
        print("📊 Step 1: Generating buy plan...")
        strategy = Strategy()
        buy_plan = strategy.generate_buy_plan()
        
        if "error" in buy_plan:
            print(f"❌ Error: {buy_plan['error']}")
            return
        
        print(f"\n✅ Buy plan generated:")
        print(f"   Total: ${buy_plan['total_amount']}")
        print(f"   Assets: {buy_plan['num_assets']}")
        print(f"   Per asset: ${buy_plan['amount_per_asset']:.2f}")
        
        print("\n📋 Assets to buy:")
        for asset in buy_plan['assets']:
            flag = '🇸🇪' if '.ST' in asset['symbol'] else '🇺🇸'
            print(f"   {flag} {asset['symbol']}: ${asset['amount_to_invest']}")
            print(f"      Price: ${asset['price']} | Trend: {asset['trend']}")
        
        # Step 2: Confirm
        print("\n" + "=" * 60)
        response = input("⚠️  Do you want to execute these trades? (yes/no): ")
        
        if response.lower() != 'yes':
            print("❌ Cancelled by user")
            return
        
        # Step 3: Execute trades
        print("\n💰 Step 2: Connecting to IG...")
        client = IGClient()
        print("✅ Connected to IG")
        
        print("\n🛒 Step 3: Placing orders...")
        for asset in buy_plan['assets']:
            symbol = asset['symbol']
            amount = asset['amount_to_invest']
            price = asset['price']
            
            # Calculate size (round down to whole shares)
            size = int(amount / price)
            if size < 1:
                print(f"   ⚠️  {symbol}: Cannot buy - price ${price} > amount ${amount}")
                continue
            
            print(f"\n   📝 {symbol}:")
            print(f"      Amount: ${amount}")
            print(f"      Price: ${price}")
            print(f"      Size: {size} shares")
            
            # TODO: Actually place order
            # For safety in first test, we simulate
            print(f"      ⚠️  SIMULATION - Order not placed yet")
            print(f"      To place real order, uncomment client.place_order()")
            
            # Real order would be:
            # client.place_order(
            #     market_id=symbol,
            #     direction="BUY",
            #     size=size,
            #     stop_distance=None,
            #     limit_distance=None
            # )
        
        print("\n" + "=" * 60)
        print("✅ DCA execution complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
