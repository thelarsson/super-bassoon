#!/usr/bin/env python3
"""
strategy.py
===========
Long-term growth strategy with automatic asset discovery.
Integrates DiscoveryEngine for dynamic asset selection.
"""

import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import DCA_AMOUNT, DCA_DAY, MAX_POSITION_PCT, MAX_POSITIONS
from discovery_engine import DiscoveryEngine
import logging

logger = logging.getLogger("Strategy")


class Strategy:
    """
    Long-term growth strategy using Dollar-Cost Averaging (DCA)
    with automatic asset discovery and selection.
    """

    def __init__(self):
        """Initialize strategy with discovery engine."""
        self.discovery = DiscoveryEngine()
        self.top_assets: List[Dict] = []
        logger.info("Strategy initialized with DiscoveryEngine")

    def should_buy_today(self, current_date: Optional[date] = None) -> bool:
        """
        Check if today is DCA day (configured day of month).
        
        Args:
            current_date: Date to check (defaults to today)
            
        Returns:
            bool: True if should buy today
        """
        if current_date is None:
            current_date = date.today()
        
        target_day = int(os.getenv('DCA_DAY', DCA_DAY))
        return current_date.day == target_day

    def get_assets_to_buy(self, n: int = MAX_POSITIONS) -> List[Dict]:
        """
        Get top N assets to buy based on discovery engine analysis.
        Runs discovery if not already done.
        
        Args:
            n: Number of assets to return
            
        Returns:
            List[Dict]: Top assets with buy recommendation
        """
        logger.info("Getting assets to buy...")
        
        # Get top assets from discovery
        all_top = self.discovery.get_top_assets(n * 2)  # Get extra for filtering
        
        # Filter for BUY recommendation only
        buy_assets = [a for a in all_top if a['recommendation'] == 'BUY']
        
        # If not enough BUY assets, take top ones anyway
        if len(buy_assets) < n:
            logger.warning(f"Only {len(buy_assets)} BUY assets found. Using top assets.")
            buy_assets = all_top[:n]
        else:
            buy_assets = buy_assets[:n]
        
        self.top_assets = buy_assets
        logger.info(f"Selected {len(buy_assets)} assets for purchase")
        return buy_assets

    def calculate_position_size(self, total_amount: float, num_assets: int) -> float:
        """
        Calculate amount to invest per asset.
        
        Args:
            total_amount: Total DCA amount
            num_assets: Number of assets to buy
            
        Returns:
            float: Amount per asset
        """
        if num_assets == 0:
            return 0
        return total_amount / num_assets

    def generate_buy_plan(self) -> Dict:
        """
        Generate complete buy plan for DCA execution.
        
        Returns:
            Dict: Buy plan with assets, amounts, and rationale
        """
        logger.info("Generating buy plan...")
        
        # Get assets to buy
        assets = self.get_assets_to_buy()
        
        if not assets:
            logger.error("No assets found to buy!")
            return {"error": "No assets available"}
        
        # Calculate amounts
        total_amount = float(os.getenv('DCA_AMOUNT', DCA_AMOUNT))
        amount_per_asset = self.calculate_position_size(total_amount, len(assets))
        
        # Build buy plan
        plan = {
            "date": datetime.now().isoformat(),
            "total_amount": total_amount,
            "num_assets": len(assets),
            "amount_per_asset": round(amount_per_asset, 2),
            "assets": []
        }
        
        for asset in assets:
            plan["assets"].append({
                "symbol": asset['symbol'],
                "name": asset['name'],
                "price": asset['price'],
                "trend": asset['trend'],
                "score": asset['score'],
                "recommendation": asset['recommendation'],
                "amount_to_invest": round(amount_per_asset, 2)
            })
        
        logger.info(f"Buy plan generated: {len(assets)} assets, ${amount_per_asset:.2f} each")
        return plan

    def screen_market(self) -> Dict:
        """
        Perform market screening and return summary.
        
        Returns:
            Dict: Market summary
        """
        return self.discovery.screen_market()


# Example usage
if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("IG Trading Bot - Strategy Test")
    print("=" * 60)
    
    strategy = Strategy()
    
    # Test 1: Check if today is DCA day
    today = date.today()
    is_dca_day = strategy.should_buy_today(today)
    print(f"\n1. DCA Day Check:")
    print(f"   Today: {today}")
    print(f"   DCA Day: {DCA_DAY}")
    print(f"   Is DCA Day: {is_dca_day}")
    
    # Test 2: Get assets to buy
    print(f"\n2. Asset Discovery:")
    assets = strategy.get_assets_to_buy(3)
    for i, asset in enumerate(assets, 1):
        print(f"   {i}. {asset['symbol']} - {asset['name']}")
        print(f"      Price: ${asset['price']} | Trend: {asset['trend']}")
        print(f"      Score: {asset['score']} | Rec: {asset['recommendation']}")
    
    # Test 3: Generate buy plan
    print(f"\n3. Buy Plan:")
    plan = strategy.generate_buy_plan()
    if "error" not in plan:
        print(f"   Total: ${plan['total_amount']}")
        print(f"   Split: ${plan['amount_per_asset']:.2f} x {plan['num_assets']} assets")
        for asset in plan['assets']:
            print(f"      - {asset['symbol']}: ${asset['amount_to_invest']}")
    
    print("\n" + "=" * 60)
