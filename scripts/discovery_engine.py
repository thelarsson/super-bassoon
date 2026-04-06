"""
discovery_engine.py
==================
Automatic Asset Discovery Engine for IG Trading Bot.

This module scans the market (US Stocks, ETFs) using Yahoo Finance
to find high-probability trading candidates based on trend strength,
liquidity, volatility, and momentum.

Author: AI Assistant
Version: 1.0.0
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DiscoveryEngine")


class DiscoveryEngine:
    """
    Automatically discovers and ranks tradeable assets based on technical criteria.
    
    Attributes:
        cache (Dict): In-memory cache for price data.
        candidates (List[Dict]): List of processed candidate assets.
    """

    def __init__(self, output_path: str = "discovered_assets.json"):
        """
        Initialize the DiscoveryEngine.
        
        Args:
            output_path (str): Path to save the resulting JSON asset list.
        """
        self.cache: Dict[str, pd.DataFrame] = {}
        self.candidates: List[Dict[str, Any]] = []
        self.output_path = Path(output_path)
        
        # Universe definitions
        self._sp500_tickers: List[str] = []
        self._nasdaq100_tickers: List[str] = []
        self._popular_etfs: List[str] = [
            "SPY", "QQQ", "DIA", "IWM", "EEM", "GLD", "SLV", 
            "TLT", "XLF", "XLE", "XLK", "XLV", "XLI", "XLY"
        ]
        
        # OMXS (Swedish market)
        self._omxs30_tickers: List[str] = [
            "ATCO-A.ST", "ATCO-B.ST", "ABB.ST", "ALFA.ST", "ASSA-B.ST",
            "AZN.ST", "BOL.ST", "ELUX-B.ST", "ERIC-B.ST", "ESSITY-B.ST",
            "EVO.ST", "GETI-B.ST", "HEXA-B.ST", "INVE-B.ST", "NDA-SE.ST",
            "SAND.ST", "SBB-B.ST", "SCA-B.ST", "SEB-A.ST", "SINCH.ST",
            "SKA-B.ST", "SKF-B.ST", "SWED-A.ST", "TEL2-B.ST", "TELIA.ST",
            "TIETOS.ST", "VOLCAR-B.ST", "VOLV-A.ST", "VOLV-B.ST", "SAGA-B.ST"
        ]
        self._swedish_etfs: List[str] = [
            "XACTOMX.ST",  # OMXS30 ETF
            "XACTS30.ST",  # OMXS30 ETF (alternative)
            "XACTNordic30.ST"  # Nordic 30
        ]
        
        logger.info("DiscoveryEngine initialized.")

    # --- Data Retrieval & Caching ---

    def _fetch_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Fetch historical data from Yahoo Finance with caching.
        
        Args:
            symbol (str): The ticker symbol.
            period (str): The period to fetch (e.g., '1y').
            
        Returns:
            Optional[pd.DataFrame]: OHLCV data or None if failed.
        """
        if symbol in self.cache:
            return self.cache[symbol]

        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, auto_adjust=True)
            
            if df.empty or len(df) < 200:
                logger.warning(f"Insufficient data for {symbol} (len={len(df)})")
                return None
            
            self.cache[symbol] = df
            return df
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None

    def _batch_fetch(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Efficiently fetch data for multiple symbols using threading.
        
        Args:
            symbols (List[str]): List of ticker symbols.
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of symbol -> DataFrame.
        """
        logger.info(f"Batch fetching data for {len(symbols)} assets...")
        results = {}
        
        # Using ThreadPoolExecutor for parallel IO
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_symbol = {executor.submit(self._fetch_data, sym): sym for sym in symbols}
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    if data is not None:
                        results[symbol] = data
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    
        return results

    # --- Universe Loading ---

    def _load_universe(self) -> List[str]:
        """
        Load the asset universe: S&P 500, Nasdaq 100, and major ETFs.
        Removes duplicates and invalid symbols.
        
        Returns:
            List[str]: Unique list of ticker symbols.
        """
        logger.info("Loading asset universe...")
        all_symbols = set()
        
        # 1. S&P 500 (Scraping from Wikipedia is standard, but fallback to static list if offline)
        try:
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            sp500_df = pd.read_html(url)[0]
            self._sp500_tickers = sp500_df['Symbol'].str.replace('.', '-').tolist()
            all_symbols.update(self._sp500_tickers)
            logger.info(f"Loaded {len(self._sp500_tickers)} S&P 500 stocks.")
        except Exception as e:
            logger.warning(f"Failed to scrape S&P 500: {e}. Using fallback.")
            # Fallback partial list
            self._sp500_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK-B']
            all_symbols.update(self._sp500_tickers)

        # 2. Nasdaq 100 (Using a subset of major tech typically present in S&P, 
        # but we add specific ETF QQQ members logic or just rely on intersection)
        # For simplicity, we rely on the intersection of major movers.
        
        # 3. Major ETFs
        all_symbols.update(self._popular_etfs)
        
        # 4. Swedish Market (OMXS)
        all_symbols.update(self._omxs30_tickers)
        all_symbols.update(self._swedish_etfs)
        logger.info(f"Added {len(self._omxs30_tickers)} OMXS30 stocks and {len(self._swedish_etfs)} Swedish ETFs.")
        
        # Filter out penny stocks preliminarily (we will check price later)
        return list(all_symbols)

    # --- Metric Calculations ---

    def _calculate_metrics(self, symbol: str, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Calculate technical indicators and scoring for a single asset.
        
        Metrics:
        - Trend Strength (EMA 50/200 crossover)
        - Volatility (Annualized)
        - Liquidity (Average Daily Volume $)
        - Momentum (1m, 3m returns)
        - Risk (Max Drawdown)
        
        Args:
            symbol (str): Ticker symbol.
            df (pd.DataFrame): Historical price data.
            
        Returns:
            Optional[Dict]: Dictionary of metrics or None if filters fail.
        """
        try:
            close = df['Close']
            volume = df['Volume']
            
            # 1. Basic Info
            current_price = close.iloc[-1]
            
            # Filter: Penny stocks (<$5)
            if current_price < 5:
                return None

            # 2. Moving Averages & Trend
            ema_50 = close.ewm(span=50, adjust=False).mean()
            ema_200 = close.ewm(span=200, adjust=False).mean()
            
            # Trend Strength: Distance between EMAs relative to price
            # Positive = Bullish, Negative = Bearish
            trend_dist = (ema_50.iloc[-1] - ema_200.iloc[-1]) / ema_200.iloc[-1]
            trend_strength_score = min(abs(trend_dist) * 1000, 100) # Normalize to 0-100
            
            # Trend Direction
            trend_direction = "BULLISH" if ema_50.iloc[-1] > ema_200.iloc[-1] else "BEARISH"
            
            # Filter: Trend Strength < 20% (Normalized score)
            # If the divergence is too small, the trend is weak.
            if trend_strength_score < 20:
                return None

            # 3. Volatility (Annualized)
            daily_returns = close.pct_change().dropna()
            volatility = daily_returns.std() * np.sqrt(252)
            
            # Filter: Volatility > 40% (0.40) is too high risk
            if volatility > 0.40:
                return None
            
            # 4. Liquidity (Average Daily Volume in $)
            avg_volume_usd = (volume.mean() * current_price)
            
            # Filter: Liquidity < $10M
            if avg_volume_usd < 10_000_000:
                return None

            # 5. Momentum
            # 1 Month Return
            price_1m_ago = close.iloc[-22] if len(close) > 22 else close.iloc[0]
            momentum_1m = (current_price - price_1m_ago) / price_1m_ago
            
            # 3 Month Return
            price_3m_ago = close.iloc[-66] if len(close) > 66 else close.iloc[0]
            momentum_3m = (current_price - price_3m_ago) / price_3m_ago

            # 6. Risk: Max Drawdown
            rolling_max = close.cummax()
            drawdown = (close - rolling_max) / rolling_max
            max_drawdown = drawdown.min() # Most negative value
            
            # 7. Sharpe Ratio (simplified, assuming risk-free rate ~ 0.02)
            risk_free_rate = 0.02
            annual_return = (1 + daily_returns.mean())**252 - 1
            sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility != 0 else 0

            # --- Composite Score ---
            # Logic: Higher is better.
            # We prioritize Trend, Momentum, and Liquidity. We penalize high volatility.
            
            # Normalize components to 0-100 scale roughly
            score = (
                trend_strength_score * 0.30 +               # Strong Trend
                (momentum_3m * 100 if momentum_3m > 0 else 0) * 0.20 + # Positive Momentum
                min(sharpe_ratio * 20, 20) +                # Risk Adjusted Return
                min(avg_volume_usd / 1e8, 10) * 10 +         # Liquidity bonus (capped)
                (1 - volatility) * 20                       # Stability bonus
            )
            
            # Round score
            final_score = round(max(0, min(100, score)), 2)

            return {
                "symbol": symbol,
                "name": yf.Ticker(symbol).info.get('shortName', 'N/A'),
                "price": round(current_price, 2),
                "trend": trend_direction,
                "trend_strength": round(trend_strength_score, 2),
                "volatility": round(volatility, 4),
                "liquidity_daily_usd": int(avg_volume_usd),
                "momentum_1m": round(momentum_1m, 4),
                "momentum_3m": round(momentum_3m, 4),
                "max_drawdown": round(max_drawdown, 4),
                "sharpe": round(sharpe_ratio, 2),
                "score": final_score,
                "recommendation": "BUY" if trend_direction == "BULLISH" and momentum_1m > 0 else "HOLD/AVOID"
            }

        except Exception as e:
            logger.error(f"Error calculating metrics for {symbol}: {e}")
            return None

    # --- Main Public Methods ---

    def discover_assets(self) -> List[Dict[str, Any]]:
        """
        Main discovery workflow. Loads universe, fetches data, calculates metrics,
        and ranks assets.
        
        Returns:
            List[Dict]: List of qualifying asset dictionaries.
        """
        # 1. Get Universe
        symbols = self._load_universe()
        
        # 2. Fetch Data (Batch)
        data_map = self._batch_fetch(symbols)
        
        # 3. Process Each Asset
        valid_assets = []
        for symbol, df in data_map.items():
            metrics = self._calculate_metrics(symbol, df)
            if metrics:
                valid_assets.append(metrics)
        
        # 4. Rank by Score
        valid_assets.sort(key=lambda x: x['score'], reverse=True)
        
        self.candidates = valid_assets
        logger.info(f"Discovery complete. Found {len(valid_assets)} qualifying assets.")
        return self.candidates

    def get_top_assets(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Returns the top N assets from the last discovery run.
        If cache is empty, triggers a new discovery.
        
        Args:
            n (int): Number of top assets to return.
            
        Returns:
            List[Dict]: Top N assets.
        """
        if not self.candidates:
            logger.info("No candidates in memory. Running discovery...")
            self.discover_assets()
            
        return self.candidates[:n]

    def update_asset_list(self) -> None:
        """
        Saves the discovered assets to a JSON file.
        """
        if not self.candidates:
            logger.warning("No assets to save.")
            return

        output_data = {
            "generated_at": datetime.now().isoformat(),
            "total_candidates": len(self.candidates),
            "top_assets": self.candidates[:10] # Save top 10 to file
        }

        try:
            with open(self.output_path, 'w') as f:
                json.dump(output_data, f, indent=4)
            logger.info(f"Asset list saved to {self.output_path}")
        except Exception as e:
            logger.error(f"Failed to save JSON: {e}")

    def screen_market(self) -> Dict[str, Any]:
        """
        Performs a daily market screening summary.
        
        Returns:
            Dict: Summary statistics of the market screen.
        """
        if not self.candidates:
            self.discover_assets()
            
        bullish_count = sum(1 for a in self.candidates if a['trend'] == 'BULLISH')
        avg_volatility = np.mean([a['volatility'] for a in self.candidates]) if self.candidates else 0
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_scanned": len(self._sp500_tickers) + len(self._popular_etfs),
            "qualifying_assets": len(self.candidates),
            "market_breadth": {
                "bullish_trends": bullish_count,
                "bearish_trends": len(self.candidates) - bullish_count
            },
            "average_volatility": round(avg_volatility, 4),
            "top_pick": self.candidates[0] if self.candidates else None
        }
        
        logger.info(f"Market Screen: {bullish_count} Bullish / {len(self.candidates)} Total Qualifying.")
        return summary


# --- Main Execution ---
if __name__ == "__main__":
    print("Starting IG Trading Bot Discovery Engine...")
    
    # Initialize Engine
    engine = DiscoveryEngine(output_path="selected_assets.json")
    
    # Run Discovery
    print("\n--- Running Asset Discovery ---")
    engine.discover_assets()
    
    # Get Top 5
    print("\n--- Top 5 Assets to Trade ---")
    top_assets = engine.get_top_assets(5)
    
    # Print results nicely
    for i, asset in enumerate(top_assets, 1):
        print(f"{i}. {asset['symbol']} ({asset['name']})")
        print(f"   Score: {asset['score']} | Trend: {asset['trend']} ({asset['trend_strength']})")
        print(f"   Price: ${asset['price']} | Volatility: {asset['volatility']:.2%}")
        print(f"   Recommendation: {asset['recommendation']}")
        print("-" * 40)
    
    # Save to file
    engine.update_asset_list()
    
    # Market Summary
    print("\n--- Market Screening Summary ---")
    summary = engine.screen_market()
    print(f"Total Scanned: {summary['total_scanned']}")
    print(f"Qualifying Candidates: {summary['qualifying_assets']}")
    print(f"Market Breadth (Bullish): {summary['market_breadth']['bullish_trends']}")
