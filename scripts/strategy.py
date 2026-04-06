import pandas as pd
from datetime import date, timedelta
from config import EMA_SHORT_PERIOD, EMA_LONG_PERIOD, TREND_THRESHOLD, DEFAULT_ASSETS
import requests

class Strategy:
    def __init__(self):
        self.client = IGClient()

    def dca_logic(self, current_date):
        if current_date.day == int(os.getenv('DCA_DAY')):
            return True
        return False

    def trend_analyzer(self, market_id):
        data = self.get_historical_data(market_id)
        ema_short = pd.Series.ewm(data['close'], span=EMA_SHORT_PERIOD).mean()
        ema_long = pd.Series.ewm(data['close'], span=EMA_LONG_PERIOD).mean()

        trend_strength = (ema_short - ema_long) / data['close']
        if abs(trend_strength[-1]) > TREND_THRESHOLD:
            return 'STRONG'
        else:
            return 'WEAK'

    def rebalancing(self, current_date):
        # Rebalancing logic here
        pass

    def get_historical_data(self, market_id):
        url = f"{self.client.base_url}/prices/{market_id}"
        response = self.client.session.get(url)
        data = response.json()
        return pd.DataFrame(data['prices'])

# Example usage
if __name__ == '__main__':
    strategy = Strategy()
    print(strategy.dca_logic(date.today()))