#!/usr/bin/env python3
"""
Weekly Market Analyzer for IG Trading Bot
Long-term ETF analysis with trend and risk assessment
Runs every Friday at 17:00 UAE time
"""

import pandas as pd
import json
import logging
import sys
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    TG_BOT_TOKEN, TG_CHAT_ID, EMA_SHORT_PERIOD, EMA_LONG_PERIOD,
    STATE_FILE, LOG_FILE, DEFAULT_ASSETS, IG_BASE_URL
)

# Import yfinance
try:
    import yfinance as yf
except ImportError:
    raise ImportError("yfinance is required. Install with: pip install yfinance")


class WeeklyAnalyzer:
    """Analyzes ETFs weekly for long-term trading decisions"""
    
    def __init__(self):
        self.etfs = ['SPY', 'QQQ', 'VTI', 'VXUS', 'BND']
        self.results = {}
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging to file"""
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def should_run(self) -> bool:
        """Check if it's Friday after 17:00 UAE time (UTC+4)"""
        now = datetime.now()
        # Friday = 4 (Monday=0), hour >= 17 UAE = 13 UTC
        is_friday = now.weekday() == 4
        is_after_5pm = now.hour >= 13  # 17:00 UAE = 13:00 UTC
        
        if not (is_friday and is_after_5pm):
            self.logger.info(f"Not time to run: {now.strftime('%A %H:%M')}")
            return False
        return True
        
    def fetch_yahoo_data(self, symbol: str, max_retries: int = 3) -> Optional[pd.DataFrame]:
        """
        Fetch historical data from Yahoo Finance using yfinance
        Returns DataFrame with Close prices or None on failure
        """
        for attempt in range(max_retries):
            try:
                # Use yfinance instead of direct HTTP requests
                ticker = yf.Ticker(symbol)
                df = ticker.history(period="2y")
                
                if df.empty:
                    raise ValueError(f"No data returned for {symbol}")
                
                # Standardize columns
                df = df.reset_index()
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values('Date')
                
                self.logger.info(f"Fetched {len(df)} days of data for {symbol}")
                return df
                
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(min(2 ** attempt, 60))
                else:
                    self.logger.error(f"Failed to fetch {symbol} after {max_retries} attempts")
                    return None
                    
    def calculate_ema(self, prices: pd.Series, period: int) -> float:
        """Calculate EMA for given period. Returns 0 if insufficient data."""
        if len(prices) < period:
            return 0.0
        return prices.ewm(span=period, adjust=False).mean().iloc[-1]
        
    def calculate_trend(self, df: pd.DataFrame) -> Tuple[str, float, float]:
        """
        Determine trend based on EMA crossover
        Returns: (trend_status, ema_short, ema_long)
        """
        ema50 = self.calculate_ema(df['Close'], EMA_SHORT_PERIOD)
        ema200 = self.calculate_ema(df['Close'], EMA_LONG_PERIOD)
        
        # Handle edge case where EMA200 is 0 or very small
        if ema200 == 0 or abs(ema200) < 0.01:
            return "NEUTRAL 🟡", ema50, ema200
        
        if ema50 > ema200 * 1.02:  # 2% buffer
            trend = "BULLISH 🟢"
        elif ema50 < ema200 * 0.98:
            trend = "BEARISH 🔴"
        else:
            trend = "NEUTRAL 🟡"
            
        return trend, ema50, ema200
        
    def calculate_volatility(self, df: pd.DataFrame) -> float:
        """Calculate annualized volatility"""
        returns = df['Close'].pct_change().dropna()
        if len(returns) < 30:
            return 0.0
        daily_vol = returns.std()
        annual_vol = daily_vol * (252 ** 0.5)  # sqrt(252) trading days
        return round(annual_vol * 100, 2)  # Return as percentage
        
    def calculate_52week_position(self, df: pd.DataFrame) -> Tuple[float, float, float]:
        """
        Calculate position relative to 52-week high/low
        Returns: (current_price, high_52w, low_52w)
        """
        last_year = df.tail(252)  # Approx 252 trading days
        high_52w = last_year['High'].max() if 'High' in last_year.columns else last_year['Close'].max()
        low_52w = last_year['Low'].min() if 'Low' in last_year.columns else last_year['Close'].min()
        current = df['Close'].iloc[-1]
        return current, high_52w, low_52w
        
    def get_recommendation(self, trend: str, volatility: float, 
                          current: float, high_52w: float) -> str:
        """
        Generate recommendation based on analysis
        BUY: Bullish trend + reasonable valuation
        HOLD: Neutral trend or high valuation
        REDUCE: Bearish trend or very high valuation
        """
        distance_from_high = (high_52w - current) / high_52w * 100
        
        if "BULLISH" in trend and distance_from_high < 10 and volatility < 25:
            return "BUY ✅"
        elif "BEARISH" in trend or distance_from_high > 20 or volatility > 35:
            return "REDUCE ⚠️"
        else:
            return "HOLD ⏸️"
            
    def analyze_etf(self, symbol: str) -> Optional[Dict]:
        """Analyze a single ETF"""
        self.logger.info(f"Analyzing {symbol}...")
        
        df = self.fetch_yahoo_data(symbol)
        if df is None:
            return None
            
        try:
            # Calculate metrics
            trend, ema50, ema200 = self.calculate_trend(df)
            volatility = self.calculate_volatility(df)
            current, high_52w, low_52w = self.calculate_52week_position(df)
            
            # Calculate distance from 52-week high
            distance_from_high = round((high_52w - current) / high_52w * 100, 2)
            
            recommendation = self.get_recommendation(
                trend, volatility, current, high_52w
            )
            
            return {
                'symbol': symbol,
                'price': round(current, 2),
                'trend': trend,
                'ema50': round(ema50, 2),
                'ema200': round(ema200, 2),
                'volatility': f"{volatility}%",
                '52w_high': round(high_52w, 2),
                '52w_low': round(low_52w, 2),
                'distance_from_high': f"{distance_from_high}%",
                'recommendation': recommendation,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            return None
            
    def send_telegram_report(self):
        """Send analysis results to Telegram"""
        if not self.results:
            self.logger.warning("No results to send")
            return
            
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        message = f"📊 *Weekly ETF Analysis - {date_str}*\n\n"
        message += "*Long-Term Growth Strategy*\n\n"
        
        for symbol, data in self.results.items():
            if data is None:
                message += f"❌ *{symbol}*: Data unavailable\n\n"
                continue
                
            message += f"📈 *{symbol}* - ${data['price']}\n"
            message += f"   Trend: {data['trend']}\n"
            message += f"   Volatility: {data['volatility']}\n"
            message += f"   From 52W High: {data['distance_from_high']}\n"
            message += f"   *Recommendation: {data['recommendation']}*\n\n"
        
        # Overall market outlook
        bullish_count = sum(1 for r in self.results.values() if r and "BULLISH" in r['trend'])
        bearish_count = sum(1 for r in self.results.values() if r and "BEARISH" in r['trend'])
        
        if bullish_count > bearish_count:
            outlook = "🟢 Cautiously Optimistic"
        elif bearish_count > bullish_count:
            outlook = "🔴 Defensive"
        else:
            outlook = "🟡 Neutral/Mixed"
            
        message += f"*Market Outlook:* {outlook}\n\n"
        message += "_Next analysis: Next Friday 17:00 UAE_"
        
        try:
            url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
            payload = {
                'chat_id': TG_CHAT_ID,
                'text': message,
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            self.logger.info("Telegram report sent successfully")
        except Exception as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
            
    def save_state(self):
        """Save analysis results to JSON"""
        state = {
            'last_analysis': datetime.now().isoformat(),
            'results': self.results
        }
        try:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)
            self.logger.info(f"State saved to {STATE_FILE}")
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
            
    def load_state(self) -> Optional[Dict]:
        """Load previous analysis results"""
        try:
            if STATE_FILE.exists():
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
        return None
        
    def run(self, force: bool = False):
        """
        Run weekly analysis
        Set force=True to run regardless of day/time
        """
        self.logger.info("=" * 50)
        self.logger.info("Starting Weekly Analyzer")
        
        if not force and not self.should_run():
            self.logger.info("Skipping - not scheduled time")
            return
            
        # Analyze all ETFs
        for symbol in self.etfs:
            result = self.analyze_etf(symbol)
            self.results[symbol] = result
            time.sleep(1)  # Be nice to Yahoo Finance API
            
        # Send report and save state
        self.send_telegram_report()
        self.save_state()
        
        self.logger.info("Weekly analysis complete")
        self.logger.info("=" * 50)


def main():
    """Entry point"""
    import argparse
    parser = argparse.ArgumentParser(description='Weekly ETF Analysis')
    parser.add_argument('--force', action='store_true', 
                       help='Run regardless of schedule')
    args = parser.parse_args()
    
    analyzer = WeeklyAnalyzer()
    analyzer.run(force=args.force)


if __name__ == '__main__':
    main()
