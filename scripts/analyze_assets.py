#!/usr/bin/env python3
"""
Quick asset analyzer - Run this to evaluate current assets
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from market_research import MarketResearch
import json

# Assets to evaluate
ASSETS = ['SPY', 'QQQ', 'VTI', 'VXUS', 'BND', 'AAPL', 'MSFT', 'GOOGL']

def main():
    print("=" * 60)
    print("ASSET ANALYSIS - Current Market Conditions")
    print("=" * 60)
    
    researcher = MarketResearch()
    results = {}
    
    for asset in ASSETS:
        print(f"\nAnalyzing {asset}...")
        try:
            # Get technical data
            tech = researcher.technical_analysis(asset)
            
            # Get fundamental data  
            fund = researcher.fundamental_analysis(asset)
            
            # Get risk metrics
            risk = researcher.risk_metrics(asset)
            
            results[asset] = {
                'trend': tech.get('trend', 'N/A'),
                'rsi': tech.get('rsi_14', 'N/A'),
                'price': tech.get('ema_50', 'N/A'),  # Using EMA50 as proxy
                'pe_ratio': fund.get('pe_ratio', 'N/A'),
                'sector': fund.get('sector', 'N/A'),
                'volatility': risk.get('volatility', 'N/A'),
                'sharpe': risk.get('sharpe_ratio', 'N/A'),
                'recommendation': 'BUY' if 'BULLISH' in str(tech.get('trend', '')) else 'HOLD'
            }
            
        except Exception as e:
            print(f"  Error analyzing {asset}: {e}")
            results[asset] = {'error': str(e)}
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for asset, data in results.items():
        if 'error' in data:
            print(f"\n{asset}: ERROR - {data['error']}")
        else:
            print(f"\n{asset}:")
            print(f"  Trend: {data['trend']}")
            print(f"  RSI: {data['rsi']}")
            print(f"  Volatility: {data['volatility']}%")
            print(f"  Sharpe: {data['sharpe']}")
            print(f"  Recommendation: {data['recommendation']}")
    
    # Save results
    with open('data/asset_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 60)
    print("Analysis complete! Results saved to data/asset_analysis.json")
    print("=" * 60)

if __name__ == '__main__':
    main()
