#!/usr/bin/env python3
"""
Monthly Performance Analyzer for IG Trading Bot
Uses local LLM to analyze trades, compare to market, and recommend code updates
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import httpx

sys.path.insert(0, str(Path(__file__).parent))
from config import TG_BOT_TOKEN, TG_CHAT_ID, STATE_FILE, LOG_FILE
from notifier import Notifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MonthlyAnalyzer")


class MonthlyPerformanceAnalyzer:
    """Analyzes monthly trading performance using LLM"""
    
    def __init__(self):
        self.notifier = Notifier()
        self.analysis_file = Path(__file__).parent.parent / 'data' / 'monthly_analysis.json'
        
    def collect_trade_data(self) -> Dict[str, Any]:
        """Collect all trades from the past month"""
        logger.info("Collecting trade data...")
        
        # Load bot state
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
        else:
            state = {}
        
        # Load positions history
        positions_file = Path(__file__).parent.parent / 'data' / 'positions.json'
        if positions_file.exists():
            with open(positions_file, 'r') as f:
                positions = json.load(f)
        else:
            positions = {}
        
        # Calculate metrics
        total_trades = len(positions)
        realized_pnl = sum(p.get('realized_pnl', 0) for p in positions.values())
        unrealized_pnl = sum(p.get('unrealized_pnl', 0) for p in positions.values())
        
        # Count buy/sell
        buys = sum(1 for p in positions.values() if p.get('action') == 'BUY')
        sells = sum(1 for p in positions.values() if p.get('action') == 'SELL')
        
        return {
            'month': datetime.now().strftime('%Y-%m'),
            'total_trades': total_trades,
            'buys': buys,
            'sells': sells,
            'realized_pnl': realized_pnl,
            'unrealized_pnl': unrealized_pnl,
            'positions': positions,
            'state': state
        }
    
    def get_market_benchmark(self) -> Dict[str, float]:
        """Get market benchmark data (S&P 500, OMXS30)"""
        logger.info("Fetching market benchmarks...")
        
        # Placeholder - would fetch actual data from Yahoo Finance
        # For now, using simulated data
        return {
            'SPY_return': 0.025,  # 2.5%
            'OMXS30_return': 0.018,  # 1.8%
            'market_sentiment': 'BULLISH'
        }
    
    def analyze_with_qwen(self, trade_data: Dict, market_data: Dict) -> str:
        """Use local Qwen model to analyze performance"""
        logger.info("Analyzing with Qwen...")
        
        prompt = f"""You are a senior trading analyst and code reviewer.

Analyze this IG Trading Bot's monthly performance:

TRADING DATA:
- Month: {trade_data['month']}
- Total Trades: {trade_data['total_trades']}
- Buys: {trade_data['buys']}
- Sells: {trade_data['sells']}
- Realized P&L: ${trade_data['realized_pnl']:.2f}
- Unrealized P&L: ${trade_data['unrealized_pnl']:.2f}

MARKET BENCHMARK:
- S&P 500 Return: {market_data['SPY_return']:.2%}
- OMXS30 Return: {market_data['OMXS30_return']:.2%}
- Market Sentiment: {market_data['market_sentiment']}

Provide analysis in this format:

1. PERFORMANCE SUMMARY
   - Overall return vs market
   - Win/loss ratio
   - Risk-adjusted performance

2. STRATEGY EFFECTIVENESS
   - Was DCA timing good?
   - Were stop-loss/take-profit levels appropriate?
   - Asset selection quality

3. MARKET COMPARISON
   - Did we beat S&P 500?
   - Did we beat OMXS30?
   - Risk vs reward analysis

4. CODE RECOMMENDATIONS
   - Should we adjust DCA_AMOUNT?
   - Should we change MAX_POSITION_PCT?
   - Should we modify stop-loss/take-profit?
   - Any other code improvements

5. ACTION ITEMS
   - Specific changes to implement
   - Priority level (High/Medium/Low)

Keep it practical and actionable for long-term growth trading."""
        
        try:
            response = httpx.post(
                'http://127.0.0.1:11434/api/generate',
                json={
                    'model': 'qwen2.5:14b',
                    'prompt': prompt,
                    'stream': False,
                    'options': {'temperature': 0.3, 'num_ctx': 8192}
                },
                timeout=180
            )
            
            return response.json().get('response', 'Analysis failed')
            
        except Exception as e:
            logger.error(f"Qwen analysis failed: {e}")
            return f"Error: {e}"
    
    def generate_report(self, analysis: str, trade_data: Dict) -> str:
        """Generate formatted Telegram report"""
        
        month_name = datetime.now().strftime('%B %Y')
        
        report = f"""📊 *IG Trading Bot - Monthly Performance Report*

🗓️ {month_name}

💰 *Trading Summary:*
• Total Trades: {trade_data['total_trades']}
• Realized P&L: ${trade_data['realized_pnl']:.2f}
• Unrealized P&L: ${trade_data['unrealized_pnl']:.2f}

📈 *LLM Analysis & Recommendations:*

{analysis}

_This analysis was generated using local Qwen2.5:14b model_
_Next report: End of next month_"""
        
        return report
    
    def save_analysis(self, analysis: str, trade_data: Dict):
        """Save analysis to file"""
        data = {
            'generated_at': datetime.now().isoformat(),
            'month': trade_data['month'],
            'trade_data': trade_data,
            'analysis': analysis
        }
        
        # Load existing or create new
        if self.analysis_file.exists():
            with open(self.analysis_file, 'r') as f:
                all_analysis = json.load(f)
        else:
            all_analysis = {'reports': []}
        
        all_analysis['reports'].append(data)
        
        with open(self.analysis_file, 'w') as f:
            json.dump(all_analysis, f, indent=2)
        
        logger.info(f"Analysis saved to {self.analysis_file}")
    
    def run(self):
        """Run monthly analysis"""
        logger.info("=" * 60)
        logger.info("STARTING MONTHLY PERFORMANCE ANALYSIS")
        logger.info("=" * 60)
        
        # 1. Collect data
        trade_data = self.collect_trade_data()
        market_data = self.get_market_benchmark()
        
        # 2. Analyze with Qwen
        analysis = self.analyze_with_qwen(trade_data, market_data)
        
        # 3. Generate report
        report = self.generate_report(analysis, trade_data)
        
        # 4. Send to Telegram
        self.notifier.send_telegram_message(report)
        logger.info("Report sent to Telegram")
        
        # 5. Save analysis
        self.save_analysis(analysis, trade_data)
        
        logger.info("Monthly analysis complete!")
        logger.info("=" * 60)


def main():
    """Entry point"""
    analyzer = MonthlyPerformanceAnalyzer()
    analyzer.run()


if __name__ == '__main__':
    main()
