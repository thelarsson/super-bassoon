#!/bin/bash
# Setup cron jobs for IG Trading Bot
# Run this script to install scheduled tasks

echo "Setting up cron jobs for IG Trading Bot..."

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create cron entries
CRON_JOBS="
# IG Trading Bot - Daily check at 08:00 UAE (04:00 UTC)
0 4 * * * cd $SCRIPT_DIR && python3 scripts/main.py >> logs/cron_daily.log 2>&1

# IG Trading Bot - Weekly analysis Friday 17:00 UAE (13:00 UTC)
0 13 * * 5 cd $SCRIPT_DIR && python3 scripts/weekly_analyzer.py >> logs/cron_weekly.log 2>&1

# IG Trading Bot - Monthly backtest (1st of month at 09:00 UAE)
0 5 1 * * cd $SCRIPT_DIR && python3 scripts/longterm_backtest.py >> logs/cron_monthly.log 2>&1
"

# Add to crontab
echo "$CRON_JOBS" | crontab -

echo "Cron jobs installed!"
echo ""
echo "Current crontab:"
crontab -l
echo ""
echo "Logs will be saved to: $SCRIPT_DIR/logs/"
