#!/usr/bin/env python3
"""
IG Trading Bot Configuration
Long-term growth focus - Cash equities only
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# IG API Configuration
IG_API_KEY = os.getenv('IG_API_KEY')
IG_IDENTIFIER = os.getenv('IG_IDENTIFIER')
IG_PASSWORD = os.getenv('IG_PASSWORD')
IG_ACCOUNT_ID = os.getenv('IG_ACCOUNT_ID')

# IG API URLs
IG_DEMO_URL = "https://demo-api.ig.com/gateway/deal"
IG_LIVE_URL = "https://api.ig.com/gateway/deal"
USE_DEMO = os.getenv('USE_DEMO', 'true').lower() == 'true'
IG_BASE_URL = IG_DEMO_URL if USE_DEMO else IG_LIVE_URL

# Currency settings
CURRENCY_CODE = os.getenv('CURRENCY_CODE', 'AED')  # Default to AED for UAE

# Telegram Configuration
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

# Trading Parameters - Long Term Growth Focus
DCA_AMOUNT = float(os.getenv('DCA_AMOUNT', '500'))  # €500 monthly default
DCA_DAY = int(os.getenv('DCA_DAY', '1'))  # Day of month for DCA (1-31)
MAX_POSITION_PCT = float(os.getenv('MAX_POSITION_PCT', '20'))  # Max 20% per asset
MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', '5'))  # Max 5 positions
MIN_CASH_BUFFER = float(os.getenv('MIN_CASH_BUFFER', '1000'))  # Keep €1000 cash

# Technical Analysis
EMA_SHORT_PERIOD = int(os.getenv('EMA_SHORT_PERIOD', '50'))
EMA_LONG_PERIOD = int(os.getenv('EMA_LONG_PERIOD', '200'))
TREND_THRESHOLD = float(os.getenv('TREND_THRESHOLD', '0.02'))  # 2% trend confirmation

# Risk Management - Conservative for long-term
STOP_LOSS_PERCENTAGE = float(os.getenv('STOP_LOSS_PERCENTAGE', '-10'))
TAKE_PROFIT_PERCENTAGE = float(os.getenv('TAKE_PROFIT_PERCENTAGE', '25'))
TRAILING_STOP = os.getenv('TRAILING_STOP', 'true').lower() == 'true'
TRAILING_STOP_DISTANCE = float(os.getenv('TRAILING_STOP_DISTANCE', '10'))  # 10%

# Rebalancing
REBALANCE_FREQUENCY = os.getenv('REBALANCE_FREQUENCY', 'monthly')  # monthly or quarterly
REBALANCE_THRESHOLD = float(os.getenv('REBALANCE_THRESHOLD', '5'))  # 5% drift

# Assets to trade (major ETFs and blue chips)
DEFAULT_ASSETS = [
    'SPY',   # SPDR S&P 500 ETF
    'QQQ',   # Invesco QQQ ETF
    'VTI',   # Vanguard Total Stock Market ETF
    'VXUS',  # Vanguard Total International Stock ETF
    'BND',   # Vanguard Total Bond Market ETF
    'AAPL',  # Apple
    'MSFT',  # Microsoft
    'GOOGL', # Alphabet
]

# IG Market IDs (to be populated by search)
MARKET_IDS = {}

# State Files
STATE_FILE = Path(__file__).parent.parent / 'data' / 'bot_state.json'
POSITIONS_FILE = Path(__file__).parent.parent / 'data' / 'positions.json'
LOG_FILE = Path(__file__).parent.parent / 'logs' / 'ig_bot.log'

# Create directories
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Validate config
def validate_config():
    required = [IG_API_KEY, IG_IDENTIFIER, IG_PASSWORD, IG_ACCOUNT_ID]
    missing = [var for var in required if not var]
    if missing:
        raise ValueError(f"Missing required config: {missing}")
    print(f"✅ Config validated - Using {'DEMO' if USE_DEMO else 'LIVE'} account")

if __name__ == '__main__':
    validate_config()
