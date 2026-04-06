IG Trading Bot

A professional trading bot for long-term growth with IG.com. Focuses on Dollar-Cost Averaging (DCA) and trend following with ETFs and blue-chip stocks.

Important: This bot trades cash equities (real stocks/ETFs), NOT CFDs or leveraged products.
🎯 Strategy

    Dollar-Cost Averaging (DCA): Invests fixed amount monthly regardless of price
    Trend Analysis: Uses EMA 50/200 to identify market trends
    Risk Management: Hard stop-loss (-10%), take-profit (+25%)
    Sector Diversification: Up to 5 different assets, max 20% per position

📁 File Structure

ig-trading-bot/
├── scripts/
│   ├── config.py              # Configuration and settings
│   ├── ig_client.py           # IG API wrapper
│   ├── main.py                # Main program (entry point)
│   ├── strategy.py            # DCA and trend strategy
│   ├── position_manager.py    # Portfolio management
│   ├── notifier.py            # Telegram notifications
│   ├── weekly_analyzer.py     # Weekly analysis (Fri 17:00)
│   ├── market_research.py     # Market analysis and research
│   ├── longterm_backtest.py   # Historical backtesting
│   └── pdf_generator.py       # PDF report generation
├── .env.template              # Environment variables template
├── .env                       # Your API keys (create this)
├── reports/                   # Generated reports
├── data/                      # Saved data and state
└── logs/                      # Log files

🚀 Installation
1. Prerequisites

# Python 3.8+
python3 --version

# Install dependencies
pip install -r requirements.txt

2. Required Python Packages

Create requirements.txt:

requests>=2.28.0
pandas>=1.5.0
numpy>=1.23.0
python-dotenv>=0.20.0
yfinance>=0.2.0
fpdf2>=2.7.0
matplotlib>=3.6.0

Install:

pip install -r requirements.txt

3. Configuration

    Copy the template:

cp .env.template .env

    Fill in your credentials in .env:

# IG API (from IG Labs)
IG_API_KEY=your_api_key
IG_IDENTIFIER=your_username
IG_PASSWORD=your_password
IG_ACCOUNT_ID=your_account_id

# Telegram (from @BotFather)
TG_BOT_TOKEN=your_bot_token
TG_CHAT_ID=your_chat_id

# Trading settings
DCA_AMOUNT=2500              # AED per month
DCA_DAY=1                    # Day of month
MAX_POSITION_PCT=20          # Max % per asset
STOP_LOSS_PERCENTAGE=-10     # Stop-loss level
TAKE_PROFIT_PERCENTAGE=25    # Take-profit level

4. IG Account

    Create IG account at ig.com
    Enable API access (IG Labs)
    Start with DEMO mode (USE_DEMO=true)

🎮 Usage
Manual Run

cd scripts

# Run main program
python3 main.py

# Run weekly analysis
python3 weekly_analyzer.py

# Run backtest
python3 longterm_backtest.py

Scheduled Run (Cron)

Add to crontab:

# Open crontab
crontab -e

# Daily check (08:00 UAE)
0 4 * * * cd /path/to/ig-trading-bot && python3 scripts/main.py >> logs/cron_daily.log 2>&1

# Weekly analysis (Friday 17:00 UAE)
0 13 * * 5 cd /path/to/ig-trading-bot && python3 scripts/weekly_analyzer.py >> logs/weekly.log 2>&1

📊 Features
1. DCA (Dollar-Cost Averaging)

    Invests fixed amount monthly
    Removes emotional decisions
    Works well over long time (years)

2. Trend Analysis

    EMA 50/200 crossover
    BULLISH/BEARISH/NEUTRAL signals
    Used to adjust DCA timing

3. Risk Management

    Stop-loss: -10% (protects against large losses)
    Take-profit: +25% (locks in gains)
    Max position: 20% per asset (diversification)
    Trailing stops: Protects profits as price rises

4. Weekly Analysis

    Runs every Friday 17:00 UAE
    Analyzes all ETFs
    Sends Telegram summary
    Saves state to JSON

5. Backtesting

    Tests strategies on historical data (5-10 years)
    Compares DCA vs Lump Sum
    Shows returns, volatility, max drawdown

6. PDF Reports

    Professional weekly reports
    Backtest results
    Portfolio summaries

🛡️ Safety
Important Safety Features:

    No mock data - If API is down, bot stops (no trading on fake data)
    Demo mode default - Always start with test account
    Validation - All orders validated before sending
    Max limits - Hard limits for positions and losses
    Logging - All events logged for audit

Risks to be Aware of:

    Market risk: Stocks can lose value
    Liquidity risk: Some ETFs may have low trading volume
    API risk: IG or Yahoo Finance may be unavailable
    Technical risk: Bugs in code (test thoroughly in demo!)

📈 Assets
Default ETFs:

    SPY - S&P 500 (broad US market)
    QQQ - Nasdaq 100 (tech-heavy)
    VTI - Total Stock Market (entire US)
    VXUS - International stocks
    BND - Bond fund

Blue-chip stocks:

    AAPL - Apple
    MSFT - Microsoft
    GOOGL - Alphabet (Google)

🔧 Configuration Options
In .env file:
Variable 	Default 	Description
DCA_AMOUNT 	2500 	Monthly investment (AED)
DCA_DAY 	1 	Which day of month
MAX_POSITION_PCT 	20 	Max % per asset
MAX_POSITIONS 	5 	Max number of assets
STOP_LOSS 	-10 	Stop-loss %
TAKE_PROFIT 	25 	Take-profit %
TRAILING_STOP 	true 	Enable trailing stop
REBALANCE_FREQUENCY 	monthly 	Rebalancing: monthly/quarterly
📝 Example Telegram Notifications
DCA Purchase:

📈 Monthly DCA Purchase

AAPL: $500 @ $175.50
Units: 2.85
Portfolio: 18% → 20%

Stop-loss:

🚨 Stop-loss Triggered

MSFT sold @ $320.50
Entry: $340.00
Loss: -5.7%

Action: Funds returned to cash

Weekly Summary:

📊 Weekly Analysis - 2024-01-15

SPY: 🟢 BULLISH - HOLD
QQQ: 🟢 BULLISH - REDUCE (High RSI)
VTI: 🟡 NEUTRAL - HOLD

Market Outlook: Cautiously Optimistic
Action: Maintain positions

🧪 Testing
Before live trading:

    Demo account - Run at least 1 month in demo
    Backtest - Test on 5-10 years of history
    Unit tests - Run tests:

python3 -m pytest tests/

Manual tests:

# Test weekly analysis
python3 scripts/weekly_analyzer.py --force

# Test backtest
python3 scripts/longterm_backtest.py

# Test PDF
python3 scripts/pdf_generator.py

📚 Resources

    IG API Documentation
    Yahoo Finance Python
    Pandas Documentation

⚠️ Disclaimer

Important: This is an experimental trading bot. Use at your own risk.

    No guarantees for returns
    Losses can exceed investment (theoretically, minimal with stop-loss)
    Always test in demo mode first
    Monitor regularly - First weeks especially
    Have a plan for when things go wrong

🔧 Troubleshooting
Common Issues:

"IG API authentication failed"

    Check credentials in .env
    Verify API access is enabled on IG

"No data returned for ETF"

    Check ticker symbol
    Yahoo Finance may be down

"Telegram message failed"

    Check bot token
    Verify chat ID

"ImportError: No module named yfinance"

    Run: pip install yfinance

🤝 Contributing

This is a personal project, but improvements are welcome!
📄 License

MIT License - See LICENSE file
Contact

For questions or support, contact via Telegram bot.

Last Updated: 2026-04-06 Version: 1.0.0 Creators: Qwen2.5:14b, GLM-5:cloud & Claude
