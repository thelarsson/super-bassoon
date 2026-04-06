import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import STATE_FILE, LOG_FILE
import logging
from position_manager import PositionManager
from strategy import Strategy
from notifier import Notifier

# IGClient is imported when needed to avoid circular imports

def initialize_logging():
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

def daily_checks(pm):
    current_date = datetime.date.today()
    if pm.dca_logic(current_date):
        # Implement DCA logic here
        pass
    # Note: get_positions needs to be called on position_manager instance
    positions = pm.positions  # Access positions dict directly
    for symbol, position in positions.items():
        pm.check_stop_losses_and_take_profits(symbol, current_date)

def monthly_tasks(pm):
    current_month_start = datetime.date(datetime.date.today().year, datetime.date.today().month, 1)
    if (datetime.date.today() - current_month_start).days >= 30:
        # Rebalancing logic here if needed
        pass

if __name__ == '__main__':
    initialize_logging()
    logging.info("Starting IG Trading Bot")

    try:
        position_manager = PositionManager()
        strategy = Strategy()
        notifier = Notifier()

        daily_checks(position_manager)
        monthly_tasks(position_manager)

        # Save state and positions
        position_manager.save_positions()
        logging.info("IG Trading Bot completed successfully")

    except Exception as e:
        logging.error(f"An error occurred: {e}")