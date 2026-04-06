import datetime
from config import STATE_FILE, LOG_FILE
import logging
from position_manager import PositionManager
from strategy import Strategy
from ig_client import IGClient
from notifier import Notifier

def initialize_logging():
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

def daily_checks(pm):
    current_date = date.today()
    if pm.dca_logic(current_date):
        # Implement DCA logic here
        pass
    for position in pm.get_positions():
        pm.check_stop_losses_and_take_profits(position, current_date)

def monthly_tasks(pm):
    current_month_start = datetime.date(date.today().year, date.today().month, 1)
    if (date.today() - current_month_start).days >= 30:  # Assuming a month has at least 30 days
        pm.rebalancing()

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

    except Exception as e:
        logging.error(f"An error occurred: {e}")