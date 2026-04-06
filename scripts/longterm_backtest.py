#!/usr/bin/env python3
"""
longterm_backtest.py - IMPROVED VERSION

Backtest engine for long-term investment strategies.
Simulates DCA vs Lump Sum vs Buy-and-Hold on historical ETF data.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time

# Optional matplotlib import
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Charts will not be generated.")


class LongTermBacktest:
    """
    Backtest engine for long-term investment strategies.
    
    Strategies:
    - DCA: Dollar Cost Averaging (monthly fixed amount)
    - Lump Sum: Invest all at start
    - Buy and Hold: Simple holding comparison
    """

    def __init__(self, etf_list: List[str], start_date: str, end_date: str, 
                 weights: Optional[List[float]] = None):
        """
        Initialize the backtest engine.

        Args:
            etf_list: List of ETF tickers (e.g., ['SPY', 'QQQ'])
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            weights: Optional weights for each ETF (must sum to 1.0). 
                    If None, equal weighting is used.
        """
        self.etf_list = etf_list
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.data: Dict[str, pd.DataFrame] = {}
        self.results: Dict[str, any] = {}
        self.fee_rate = 0.001  # 0.1% per trade
        
        # Set weights
        if weights:
            if len(weights) != len(etf_list):
                raise ValueError("Weights must match number of ETFs")
            if abs(sum(weights) - 1.0) > 0.001:
                raise ValueError("Weights must sum to 1.0")
            self.weights = weights
        else:
            self.weights = [1.0 / len(etf_list)] * len(etf_list)
        
        # Create directories for output
        os.makedirs('reports', exist_ok=True)
        os.makedirs('data', exist_ok=True)

    def fetch_historical_data(self, max_retries: int = 3) -> None:
        """
        Fetch historical OHLCV data from Yahoo Finance.
        Includes retry logic for network issues.
        """
        print(f"Fetching data for {self.etf_list}...")
        
        for etf in self.etf_list:
            for attempt in range(max_retries):
                try:
                    df = yf.download(etf, start=self.start_date, 
                                    end=self.end_date, progress=False)
                    
                    if df.empty:
                        raise ValueError(f"No data returned for {etf}")
                    
                    # Handle MultiIndex columns (yfinance sometimes returns MultiIndex)
                    if isinstance(df.columns, pd.MultiIndex):
                        df = df.xs(etf, level=1, axis=1)
                    
                    # Handle different column naming (yfinance changed format)
                    # Flatten MultiIndex if present
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.droplevel(1)
                    
                    # Rename columns to standard format
                    col_map = {}
                    for col in df.columns:
                        if 'Adj Close' in str(col) or 'adj close' in str(col).lower():
                            col_map[col] = 'Adj Close'
                        elif 'Close' in str(col):
                            col_map[col] = 'Close'
                        elif 'Open' in str(col):
                            col_map[col] = 'Open'
                        elif 'High' in str(col):
                            col_map[col] = 'High'
                        elif 'Low' in str(col):
                            col_map[col] = 'Low'
                        elif 'Volume' in str(col):
                            col_map[col] = 'Volume'
                    
                    if col_map:
                        df = df.rename(columns=col_map)
                    
                    # If no Adj Close, use Close
                    if 'Adj Close' not in df.columns and 'Close' in df.columns:
                        df['Adj Close'] = df['Close']
                    
                    # Select only needed columns
                    required_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
                    available_cols = [col for col in required_cols if col in df.columns]
                    df = df[available_cols]
                    df.index = pd.to_datetime(df.index)
                    
                    self.data[etf] = df
                    print(f"✓ Fetched {len(df)} rows for {etf}")
                    break
                    
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed for {etf}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise Exception(f"Failed to fetch {etf} after {max_retries} attempts")

    def run_dca_simulation(self, monthly_amount: float) -> Dict[str, any]:
        """
        Simulate Dollar Cost Averaging strategy.
        Invests fixed amount monthly on first trading day.

        Args:
            monthly_amount: Amount to invest each month

        Returns:
            Dict with simulation results
        """
        if not self.data:
            self.fetch_historical_data()

        print(f"Running DCA Simulation: ${monthly_amount}/month...")
        
        # Get actual trading days from first ETF
        primary_etf = self.etf_list[0]
        trading_days = self.data[primary_etf].index
        
        # Find first trading day of each month
        monthly_investment_dates = []
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # Find first trading day of this month
            month_start = current_date.replace(day=1)
            valid_days = trading_days[trading_days >= month_start]
            
            if len(valid_days) > 0:
                first_trading_day = valid_days[0]
                if first_trading_day <= self.end_date:
                    monthly_investment_dates.append(first_trading_day)
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        print(f"Investment dates: {len(monthly_investment_dates)} months")

        # Initialize portfolio tracking for each ETF
        portfolio = {etf: {'units': 0.0, 'invested': 0.0} for etf in self.etf_list}
        total_invested = 0.0
        
        # Simulate DCA
        for inv_date in monthly_investment_dates:
            for i, etf in enumerate(self.etf_list):
                try:
                    # Get price on investment date
                    etf_data = self.data[etf]
                    price_data = etf_data.loc[:inv_date, 'Adj Close']
                    
                    if len(price_data) == 0:
                        continue
                    
                    price = price_data.iloc[-1]
                    
                    # Calculate investment for this ETF (weighted)
                    etf_allocation = monthly_amount * self.weights[i]
                    investment_net = etf_allocation * (1 - self.fee_rate)
                    units_bought = investment_net / price
                    
                    portfolio[etf]['units'] += units_bought
                    portfolio[etf]['invested'] += etf_allocation
                    total_invested += etf_allocation
                    
                except Exception as e:
                    print(f"Warning: Could not invest in {etf} on {inv_date}: {e}")
                    continue

        # Calculate final values
        final_values = {}
        total_final_value = 0.0
        
        for etf in self.etf_list:
            final_price = self.data[etf]['Adj Close'].iloc[-1]
            final_value = portfolio[etf]['units'] * final_price
            final_values[etf] = {
                'units': portfolio[etf]['units'],
                'final_value': final_value,
                'invested': portfolio[etf]['invested']
            }
            total_final_value += final_value

        # Calculate metrics
        profit_loss = total_final_value - total_invested
        roi = (profit_loss / total_invested) * 100 if total_invested > 0 else 0
        
        dca_results = {
            "strategy": "DCA",
            "monthly_amount": monthly_amount,
            "total_invested": round(total_invested, 2),
            "final_value": round(total_final_value, 2),
            "profit_loss": round(profit_loss, 2),
            "roi_percent": round(roi, 2),
            "num_months": len(monthly_investment_dates),
            "by_etf": final_values
        }
        
        self.results['dca'] = dca_results
        return dca_results

    def run_lump_sum_simulation(self, total_amount: float) -> Dict[str, any]:
        """
        Simulate lump sum investment at start.

        Args:
            total_amount: Amount to invest at start

        Returns:
            Dict with simulation results
        """
        if not self.data:
            self.fetch_historical_data()

        print(f"Running Lump Sum Simulation: ${total_amount}...")
        
        portfolio = {}
        
        for i, etf in enumerate(self.etf_list):
            try:
                # Get price on first trading day
                first_price = self.data[etf]['Adj Close'].iloc[0]
                
                # Weighted allocation
                etf_allocation = total_amount * self.weights[i]
                investment_net = etf_allocation * (1 - self.fee_rate)
                units = investment_net / first_price
                
                # Final value
                final_price = self.data[etf]['Adj Close'].iloc[-1]
                final_value = units * final_price
                
                portfolio[etf] = {
                    'units': units,
                    'invested': etf_allocation,
                    'final_value': final_value,
                    'first_price': first_price,
                    'final_price': final_price
                }
                
            except Exception as e:
                print(f"Error in lump sum simulation for {etf}: {e}")
                raise

        total_final = sum(p['final_value'] for p in portfolio.values())
        profit_loss = total_final - total_amount
        roi = (profit_loss / total_amount) * 100
        
        lump_results = {
            "strategy": "Lump Sum",
            "total_amount": total_amount,
            "final_value": round(total_final, 2),
            "profit_loss": round(profit_loss, 2),
            "roi_percent": round(roi, 2),
            "by_etf": portfolio
        }
        
        self.results['lump_sum'] = lump_results
        return lump_results

    def calculate_metrics(self, returns: pd.Series) -> Dict[str, float]:
        """
        Calculate risk-adjusted performance metrics.

        Args:
            returns: Series of daily returns

        Returns:
            Dict with metrics
        """
        if len(returns) < 2:
            return {
                "volatility": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "annualized_return": 0.0
            }
        
        # Annualized volatility
        volatility = returns.std() * np.sqrt(252)
        
        # Annualized return
        total_return = (returns + 1).prod() - 1
        num_years = len(returns) / 252
        annualized_return = (1 + total_return) ** (1 / num_years) - 1 if num_years > 0 else 0
        
        # Sharpe ratio (handle zero volatility)
        if volatility == 0 or np.isnan(volatility):
            sharpe = 0.0
        else:
            risk_free_daily = 0.02 / 252  # Assume 2% annual risk-free
            sharpe = (annualized_return - 0.02) / volatility
        
        # Maximum drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        return {
            "volatility": round(volatility * 100, 2),  # As percentage
            "sharpe_ratio": round(sharpe, 2),
            "max_drawdown": round(max_drawdown * 100, 2),  # As percentage
            "annualized_return": round(annualized_return * 100, 2)  # As percentage
        }

    def compare_strategies(self) -> Dict[str, any]:
        """
        Compare DCA vs Lump Sum vs Buy and Hold.

        Returns:
            Dict with comparison results
        """
        if 'dca' not in self.results or 'lump_sum' not in self.results:
            raise ValueError("Run simulations first")
        
        dca = self.results['dca']
        lump = self.results['lump_sum']
        
        comparison = {
            "dca": {
                "total_invested": dca['total_invested'],
                "final_value": dca['final_value'],
                "roi": dca['roi_percent']
            },
            "lump_sum": {
                "total_invested": lump['total_amount'],
                "final_value": lump['final_value'],
                "roi": lump['roi_percent']
            },
            "winner": "DCA" if dca['final_value'] > lump['final_value'] else "Lump Sum",
            "value_difference": round(abs(dca['final_value'] - lump['final_value']), 2)
        }
        
        self.results['comparison'] = comparison
        return comparison

    def export_results(self, filename: str = "backtest_results.json") -> str:
        """
        Export results to JSON file.

        Args:
            filename: Output filename

        Returns:
            Path to saved file
        """
        output_path = os.path.join('reports', filename)
        
        export_data = {
            "metadata": {
                "etf_list": self.etf_list,
                "weights": self.weights,
                "start_date": self.start_date.strftime('%Y-%m-%d'),
                "end_date": self.end_date.strftime('%Y-%m-%d'),
                "generated_at": datetime.now().isoformat()
            },
            "results": self.results
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Results exported to {output_path}")
        return output_path


# --- Example Usage ---
if __name__ == "__main__":
    # Example backtest
    etfs = ["SPY", "QQQ", "VTI"]
    
    backtest = LongTermBacktest(
        etf_list=etfs,
        start_date="2020-01-01",
        end_date="2024-01-01",
        weights=[0.4, 0.3, 0.3]  # 40% SPY, 30% QQQ, 30% VTI
    )
    
    # Run simulations
    dca_results = backtest.run_dca_simulation(monthly_amount=500)
    lump_results = backtest.run_lump_sum_simulation(total_amount=24000)  # Same total
    
    # Compare
    comparison = backtest.compare_strategies()
    
    print("\n" + "="*50)
    print("BACKTEST RESULTS")
    print("="*50)
    print(f"\nDCA Strategy:")
    print(f"  Total Invested: ${dca_results['total_invested']:,.2f}")
    print(f"  Final Value: ${dca_results['final_value']:,.2f}")
    print(f"  ROI: {dca_results['roi_percent']:.2f}%")
    
    print(f"\nLump Sum Strategy:")
    print(f"  Total Invested: ${lump_results['total_amount']:,.2f}")
    print(f"  Final Value: ${lump_results['final_value']:,.2f}")
    print(f"  ROI: {lump_results['roi_percent']:.2f}%")
    
    print(f"\nWinner: {comparison['winner']}")
    print(f"Difference: ${comparison['value_difference']:,.2f}")
    
    # Export
    backtest.export_results()
