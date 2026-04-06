import requests
from config import TG_BOT_TOKEN, TG_CHAT_ID

class Notifier:
    def send_dca_purchase_notification(self, asset, amount):
        message = f"Monthly DCA purchase: {asset} - €{amount}"
        self.send_telegram_message(message)

    def send_stop_loss_take_profit_alert(self, asset, action):
        message = f"{action.capitalize()} triggered for {asset}"
        self.send_telegram_message(message)

    def send_weekly_portfolio_summary(self):
        # Implement portfolio summary logic here
        pass

    def send_rebalancing_alert(self):
        # Implement rebalancing alert logic here
        pass

    def send_telegram_message(self, message):
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TG_CHAT_ID,
            'text': message
        }
        response = requests.post(url, json=payload)
        if not response.ok:
            print(f"Failed to send telegram message: {response.text}")

# Example usage
if __name__ == '__main__':
    notifier = Notifier()
    notifier.send_dca_purchase_notification('SPY', 500)