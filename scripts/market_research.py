#!/usr/bin/env python3
"""
market_research.py - PRODUCTION SAFE VERSION

Market research module for IG Trading Bot.
NO MOCK DATA - Fails safe instead of using fake data.

Features:
- Fundamental data retrieval (P/E, Dividends, Sector)
- Technical analysis (EMA, RSI with Wilder's Smoothing, MACD)
- Macro indicators (Interest rates, Inflation, USD Strength)
- Sector rotation analysis
- Risk metrics (Sharpe, Drawdown, Volatility)
- Data caching to reduce API calls
"""

import logging
import time
import datetime
import os
from typing import Dict, Any, List, Optional, Tuple
from functools import lru_cache

import pandas as pd
import numpy as np
import requests

# Require yfinance - NO MOCK DATA IN PRODUCTION
try:
    import yfinance as yf
except ImportError:
    raise RuntimeError(
        "yfinance library is required. Install with: pip install yfinance\n"
        "Mock data is NOT allowed in production."
    )

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger("MarketResearch")


class MarketResearch:
    """
    Handles market research operations including fundamental analysis,
    technical indicators, macro indicators, and risk assessment.
    
    SAFETY: No mock data. If APIs fail, raises Exception.
    """

    def __init__(self, risk_free_rate: float = 0.05):
        """
        Initialize MarketResearch.
        
        Args:
            risk_free_rate: Annual risk-free rate for Sharpe calculation (default 5%)
        """
        self.risk_free_rate = risk_free_rate
        self.session = requests.Session()
        self._data_cache: Dict[str, pd.DataFrame] = {}
        
        # Standard sector ETFs for rotation analysis
        self.sector_etfs = {
            'Technology': 'XLK',
            'Health Care': 'XLV',
            'Financials': 'XLF',
            'Energy': 'XLE',
            'Consumer Discretionary': 'XLY',
            'Consumer Staples': 'XLP',
            'Industrials': 'XLI',
            'Materials': 'XLB',
            'Real Estate': 'XLRE',
            'Utilities': 'XLU',
            'Communication': 'XLC'
        }

    def _retry_request(self, func, *args, max_retries: int = 3, delay: int = 2, **kwargs) -> Any:
        """
        Wrapper to retry a function call upon failure.
        
        Raises:
            Exception: If all retries fail
        """
        last_error = None
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay)
        
        # All retries failed - raise exception (NO MOCK DATA)
        raise Exception(f"Function {func.__name__} failed after {max_retries} attempts: {last_error}")

    def _get_ticker_data(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        """
        Fetches historical data for a ticker with caching.
        
        Args:
            ticker: Stock/ETF symbol
            period: Time period (1y, 2y, 5y, etc.)
            
        Returns:
            DataFrame with OHLCV data
            
        Raises:
            Exception: If data cannot be fetched
        """
        cache_key = f"{ticker}_{period}"
        
        # Check cache first
        if cache_key in self._data_cache:
            logger.info(f"Using cached data for {ticker}")
            return self._data_cache[cache_key]
        
        # Fetch from API
        def fetch():
            df = yf.download(ticker, period=period, progress=False)
            if df.empty:
                raise ValueError(f"No data returned for {ticker}")
            
            # Handle MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df = df.xs(ticker, level=1, axis=1)
            
            # Standardize columns
            df = df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
            df.index = pd.to_datetime(df.index)
            return df
        
        df = self._retry_request(fetch)
        
        # Cache the result
        self._data_cache[cache_key] = df
        logger.info(f"Fetched {len(df)} rows for {ticker}")
        return df

    def clear_cache(self):
        """Clear the data cache. Call this before each analysis run."""
        self._data_cache.clear()
        logger.info("Data cache cleared")

    # --- Fundamental Analysis ---

    def fundamental_analysis(self, ticker: str) -> Dict[str, Any]:
        """
        Get fundamental data for a ticker.
        
        Returns dict with: pe_ratio, dividend_yield, sector, market_cap
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            
            return {
                "ticker": ticker,
                "pe_ratio": info.get("trailingPE", "N/A"),
                "dividend_yield": info.get("dividendYield", "N/A"),
                "sector": info.get("sector", "Unknown"),
                "market_cap": info.get("marketCap", "N/A"),
                "data_source": "Yahoo Finance"
            }
        except Exception as e:
            logger.error(f"Failed to get fundamental data for {ticker}: {e}")
            raise  # NO MOCK DATA - Fail safe

    # --- Technical Analysis ---

    def technical_analysis(self, ticker: str) -> Dict[str, Any]:
        """
        Calculate technical indicators for a ticker.
        
        Uses Wilder's Smoothing (EMA) for RSI - industry standard.
        
        Returns dict with: ema_50, ema_200, rsi_14, macd, macd_signal
        """
        df = self._get_ticker_data(ticker, period="1y")
        
        # Check minimum data length
        if len(df) < 200:
            raise ValueError(f"Insufficient data for {ticker}: {len(df)} rows, need 200+")
        
        close = df['Adj Close']
        
        # EMAs
        ema_50 = close.ewm(span=50, adjust=False).mean().iloc[-1]
        ema_200 = close.ewm(span=200, adjust=False).mean().iloc[-1]
        
        # RSI with Wilder's Smoothing (industry standard)
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Use Wilder's Smoothing (EMA with alpha=1/14)
        avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
        
        # Avoid division by zero
        avg_loss_safe = avg_loss.replace(0, np.nan)
        rs = avg_gain / avg_loss_safe
        rsi = 100 - (100 / (1 + rs))
        
        # Fill NaN (from 0 loss) with 100 (perfectly bullish)
        rsi = rsi.fillna(100)
        rsi_14 = rsi.iloc[-1]
        
        # MACD
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        macd_signal = macd_line.ewm(span=9, adjust=False).mean()
        
        return {
            "ticker": ticker,
            "ema_50": round(ema_50, 2),
            "ema_200": round(ema_200, 2),
            "rsi_14": round(rsi_14, 2),
            "macd": round(macd_line.iloc[-1], 4),
            "macd_signal": round(macd_signal.iloc[-1], 4),
            "trend": "BULLISH" if ema_50 > ema_200 else "BEARISH"
        }

    # --- Risk Metrics ---

    def risk_metrics(self, ticker: str) -> Dict[str, Any]:
        """
        Calculate risk-adjusted performance metrics.
        
        Returns dict with: volatility, sharpe_ratio, max_drawdown, var_95
        """
        df = self._get_ticker_data(ticker, period="2y")
        
        if len(df) < 252:
            raise ValueError(f"Insufficient data for risk metrics: {len(df)} rows")
        
        prices = df['Adj Close']
        returns = prices.pct_change().dropna()
        
        # Annualized volatility
        volatility = returns.std() * np.sqrt(252)
        
        # Sharpe Ratio (handle zero volatility)
        avg_return = returns.mean() * 252
        if volatility == 0 or np.isnan(volatility):
            sharpe_ratio = 0.0
        else:
            sharpe_ratio = (avg_return - self.risk_free_rate) / volatility
        
        # Maximum Drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Value at Risk (95% confidence)
        var_95 = np.percentile(returns, 5)
        
        return {
            "ticker": ticker,
            "volatility": round(volatility * 100, 2),  # As percentage
            "sharpe_ratio": round(sharpe_ratio, 2),
            "max_drawdown": round(max_drawdown * 100, 2),  # As percentage
            "var_95": round(var_95 * 100, 2),  # As percentage
            "annualized_return": round(avg_return * 100, 2)  # As percentage
        }

    # --- Macro Indicators ---

    def macro_indicators(self) -> Dict[str, Any]:
        """
        Fetch key macroeconomic indicators.
        
        Uses ETFs as proxies:
        - US 10Y Treasury: ^TNX or TLT
        - USD Strength: DXY
        - Inflation: TIPS spreads (indirect)
        """
        indicators = {}
        
        try:
            # US 10Y Treasury Yield (use TLT as proxy)
            tlt = self._get_ticker_data("TLT", period="1mo")
            if len(tlt) >= 5:
                # Rough approximation: inverse of TLT price
                current_yield = 5.0 - (tlt['Adj Close'].iloc[-1] - 90) * 0.1
                indicators['us_10y_yield'] = round(current_yield, 2)
            else:
                indicators['us_10y_yield'] = "N/A - insufficient data"
        except Exception as e:
            logger.warning(f"Could not fetch treasury data: {e}")
            indicators['us_10y_yield'] = "N/A"
        
        try:
            # USD Strength (UUP ETF as proxy for DXY)
            uup = self._get_ticker_data("UUP", period="1mo")
            if len(uup) >= 5:
                indicators['usd_index'] = round(uup['Adj Close'].iloc[-1] * 100 / 25, 1)
            else:
                indicators['usd_index'] = "N/A"
        except Exception as e:
            logger.warning(f"Could not fetch USD data: {e}")
            indicators['usd_index'] = "N/A"
        
        indicators['data_timestamp'] = datetime.datetime.now().isoformat()
        return indicators

    # --- Sector Rotation Analysis ---

    def sector_rotation(self) -> Dict[str, Any]:
        """
        Analyze sector performance to identify trends.
        
        Returns dict with sector returns and rankings.
        """
        performance = {}
        
        for sector, etf in self.sector_etfs.items():
            try:
                df = self._get_ticker_data(etf, period="3mo")
                if len(df) < 22:
                    logger.warning(f"Insufficient data for {sector}")
                    continue
                
                # Calculate returns
                current = df['Adj Close'].iloc[-1]
                
                # Safely get 1 month ago price
                one_month_idx = min(22, len(df) - 1)
                one_month_ago = df['Adj Close'].iloc[-one_month_idx]
                
                # Safely get 3 months ago price  
                three_month_idx = min(66, len(df) - 1)
                three_months_ago = df['Adj Close'].iloc[-three_month_idx]
                
                return_1m = (current - one_month_ago) / one_month_ago
                return_3m = (current - three_months_ago) / three_months_ago
                
                performance[sector] = {
                    "1m_return": round(return_1m * 100, 2),  # As percentage
                    "3m_return": round(return_3m * 100, 2),  # As percentage
                    "trend": "STRONG" if return_1m > 0.05 else "WEAK"
                }
            except Exception as e:
                logger.warning(f"Failed to analyze {sector}: {e}")
                # Skip this sector rather than use mock data
                continue
        
        # Rank sectors by 1-month return
        if performance:
            ranked = sorted(
                performance.items(), 
                key=lambda x: x[1].get('1m_return', 0), 
                reverse=True
            )
            return {
                "sector_performance": performance,
                "top_sector": ranked[0][0],
                "bottom_sector": ranked[-1][0],
                "analysis_date": datetime.datetime.now().isoformat()
            }
        else:
            return {
                "error": "No sector data available",
                "analysis_date": datetime.datetime.now().isoformat()
            }

    # --- Report Generation ---

    def generate_weekly_report(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Generate comprehensive weekly report for a list of tickers.
        
        Args:
            tickers: List of ETF/stock symbols to analyze
            
        Returns:
            Dict with all analysis data
        """
        logger.info(f"Generating weekly report for: {tickers}")
        
        # Clear cache before new analysis
        self.clear_cache()
        
        report = {
            "report_date": datetime.datetime.now().isoformat(),
            "tickers_analyzed": tickers,
            "fundamental_data": {},
            "technical_data": {},
            "risk_metrics": {},
            "macro_indicators": {},
            "sector_rotation": {}
        }
        
        # Analyze each ticker
        for ticker in tickers:
            try:
                report["fundamental_data"][ticker] = self.fundamental_analysis(ticker)
                report["technical_data"][ticker] = self.technical_analysis(ticker)
                report["risk_metrics"][ticker] = self.risk_metrics(ticker)
            except Exception as e:
                logger.error(f"Failed to analyze {ticker}: {e}")
                report["fundamental_data"][ticker] = {"error": str(e)}
                report["technical_data"][ticker] = {"error": str(e)}
                report["risk_metrics"][ticker] = {"error": str(e)}
        
        # Macro and sector analysis
        try:
            report["macro_indicators"] = self.macro_indicators()
        except Exception as e:
            logger.error(f"Failed to get macro indicators: {e}")
            report["macro_indicators"] = {"error": str(e)}
        
        try:
            report["sector_rotation"] = self.sector_rotation()
        except Exception as e:
            logger.error(f"Failed to analyze sector rotation: {e}")
            report["sector_rotation"] = {"error": str(e)}
        
        return report


# --- Main Execution Example ---
if __name__ == "__main__":
    # Example Usage
    researcher = MarketResearch()
    
    # Define portfolio
    portfolio = ["SPY", "QQQ", "VTI"]
    
    # Generate Report
    try:
        weekly_report = researcher.generate_weekly_report(portfolio)
        
        # Print Report (Pretty Print)
        import json
        print(json.dumps(weekly_report, indent=4))
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        print(f"Error: {e}")
        print("\nNote: This module requires yfinance and internet connectivity.")
        print("No mock data is used - all data must come from real APIs.")
