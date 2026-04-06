#!/usr/bin/env python3
"""
Unit tests for market_research.py
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from market_research import MarketResearch


class TestMarketResearch(unittest.TestCase):
    """Test cases for MarketResearch class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.researcher = MarketResearch(risk_free_rate=0.05)
    
    def test_initialization(self):
        """Test that MarketResearch initializes correctly"""
        self.assertEqual(self.researcher.risk_free_rate, 0.05)
        self.assertIsNotNone(self.researcher.sector_etfs)
        self.assertIn('Technology', self.researcher.sector_etfs)
    
    def test_clear_cache(self):
        """Test cache clearing"""
        # Add dummy data to cache
        self.researcher._data_cache['TEST_1y'] = None
        self.researcher.clear_cache()
        self.assertEqual(len(self.researcher._data_cache), 0)
    
    def test_calculate_ema_insufficient_data(self):
        """Test EMA calculation with insufficient data"""
        import pandas as pd
        prices = pd.Series([100, 101, 102])  # Less than 50 data points
        result = self.researcher.calculate_ema(prices, 50)
        self.assertEqual(result, 0.0)  # Should return 0 for insufficient data
    
    def test_safe_get(self):
        """Test _safe_get method"""
        test_data = {'key1': 'value1', 'key2': None}
        
        # Existing key
        self.assertEqual(self.researcher._safe_get(test_data, 'key1'), 'value1')
        
        # Missing key with default
        self.assertEqual(self.researcher._safe_get(test_data, 'missing', 'default'), 'default')
        
        # None value with default
        self.assertEqual(self.researcher._safe_get(test_data, 'key2', 'default'), 'default')


class TestRiskMetrics(unittest.TestCase):
    """Test risk calculation functions"""
    
    def setUp(self):
        self.researcher = MarketResearch()
    
    def test_calculate_metrics_insufficient_data(self):
        """Test metrics with insufficient data"""
        import pandas as pd
        returns = pd.Series([0.01])  # Only 1 return
        
        metrics = self.researcher.calculate_metrics(returns)
        
        self.assertEqual(metrics['volatility'], 0.0)
        self.assertEqual(metrics['sharpe_ratio'], 0.0)


class TestTechnicalAnalysis(unittest.TestCase):
    """Test technical analysis functions"""
    
    def setUp(self):
        self.researcher = MarketResearch()
    
    def test_calculate_trend_bullish(self):
        """Test bullish trend detection"""
        import pandas as pd
        # Create data where EMA50 > EMA200
        prices = pd.Series(range(250, 450))  # Rising prices
        
        trend, ema50, ema200 = self.researcher.calculate_trend(prices)
        self.assertIn("BULLISH", trend)
    
    def test_calculate_trend_ema200_zero(self):
        """Test edge case where EMA200 is 0"""
        import pandas as pd
        prices = pd.Series([100] * 250)  # Flat prices
        
        trend, ema50, ema200 = self.researcher.calculate_trend(prices)
        self.assertEqual(trend, "NEUTRAL 🟡")


if __name__ == '__main__':
    unittest.main()
