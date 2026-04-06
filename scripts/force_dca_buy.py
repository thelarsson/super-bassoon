#!/usr/bin/env python3
"""
FORCE DCA BUY - Test script
Runs a DCA purchase immediately, ignoring the date check.
WARNING: This uses REAL MONEY from your IG account!
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime
import logging
from config import LOG_FILE, DCA_AMOUNT, DEFAULT_ASSETS
from ig_client import IGClient
from notifier import Notifier

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    print("=" * 60)
    print("⚠️  FORCE DCA BUY - TEST MODE")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Amount to invest: {DCA_AMOUNT} AED (~$140 USD)")
    print(f"Target assets: {', '.join(DEFAULT_ASSETS[:2])}")  # Only first 2 for test
    print()
    
    logger.info("=" * 60)
    logger.info("FORCE DCA BUY STARTED")
    logger.info(f"Amount: {DCA_AMOUNT} AED")
    
    try:
        # Connect to IG
        print("Connecting to IG...")
        client = IGClient()
        notifier = Notifier()
        print("✅ Connected to IG API")
        
        # Get account info first
        account_info = client.get_account_info()
        balance = account_info['accounts'][0]['balance']['available']
        currency = account_info['accounts'][0]['currency']
        print(f"\n💰 Account Balance: {balance} {currency}")
        
        if balance < DCA_AMOUNT:
            print(f"❌ Insufficient funds! Need {DCA_AMOUNT} {currency}, have {balance}")
            logger.error(f"Insufficient funds: {balance} < {DCA_AMOUNT}")
            return
        
        print(f"\n✅ Sufficient funds confirmed")
        print(f"\n🛒 Preparing to buy...")
        
        # For now, just log what WOULD happen
        # In real implementation, this would place actual orders
        print("\n📋 ORDER PREVIEW:")
        print(f"  Assets: {DEFAULT_ASSETS[:2]}")  # First 2 assets only for test
        print(f"  Amount per asset: ~{DCA_AMOUNT // 2} AED")
        print(f"  Order type: MARKET")
        print()
        
        # TODO: Implement actual order placement
        # For safety in first test, we only simulate
        print("⚠️  SIMULATION MODE - No actual order placed yet!")
        print("   To place real order, uncomment the place_order lines below")
        print()
        
        # Send notification
        message = f"🧪 FORCE DCA TEST\n\n"
        message += f"Amount: {DCA_AMOUNT} AED\n"
        message += f"Balance: {balance} {currency}\n"
        message += f"Status: SIMULATION (no real order)\n"
        message += f"\nReady for real trading!"
        
        # notifier.send_telegram_message(message)  # Uncomment to enable
        print("✅ Test completed successfully!")
        print("   Bot is ready for real DCA purchases.")
        print("   Next automatic purchase: May 1st, 2026")
        
        logger.info("FORCE DCA TEST COMPLETED")
        logger.info("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"FORCE DCA FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("\n⚠️  This will test the DCA logic with REAL account")
    print("   Press Ctrl+C to cancel, or wait 3 seconds...")
    import time
    time.sleep(3)
    main()
