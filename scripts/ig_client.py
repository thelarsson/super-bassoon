import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import timedelta
from config import IG_API_KEY, IG_IDENTIFIER, IG_PASSWORD, IG_ACCOUNT_ID, USE_DEMO, IG_BASE_URL
from time import sleep

class IGClient:
    def __init__(self):
        self.base_url = IG_BASE_URL
        self.session = requests.Session()
        self.headers = {'X-IG-API-KEY': IG_API_KEY}
        self.authenticate()

    def authenticate(self):
        url = f"{self.base_url}/session"
        payload = {
            "identifier": IG_IDENTIFIER,
            "password": IG_PASSWORD
        }
        response = self.session.post(url, headers=self.headers, json=payload)
        if not response.ok:
            raise Exception(f"Authentication failed: {response.text}")
        
        # IG uses CST and X-SECURITY-TOKEN headers, not Bearer token
        cst = response.headers.get('CST')
        security_token = response.headers.get('X-SECURITY-TOKEN')
        
        if cst:
            self.headers['CST'] = cst
        if security_token:
            self.headers['X-SECURITY-TOKEN'] = security_token

    def get_account_info(self):
        url = f"{self.base_url}/accounts"
        response = self.session.get(url, headers=self.headers)
        if not response.ok:
            raise Exception(f"Failed to get account info: {response.text}")
        return response.json()

    def get_positions(self):
        url = f"{self.base_url}/positions"
        params = {'dealId': IG_ACCOUNT_ID}
        response = self.session.get(url, headers=self.headers, params=params)
        return response.json().get('positions', [])

    def place_order(self, market_id, direction, size, stop_distance=None, limit_distance=None):
        url = f"{self.base_url}/deals"
        payload = {
            "dealReference": "test",
            "direction": direction,
            "epic": market_id,
            "expiry": "",
            "level": 0.0,
            "orderType": "MARKET",
            "size": size,
            "currencyCode": "GBP",
            "forceOpen": True
        }
        if stop_distance:
            payload['guaranteedStop'] = False
            payload['stopLevel'] = stop_distance
        if limit_distance:
            payload['limitDistance'] = limit_distance

        response = self.session.post(url, headers=self.headers, json=payload)
        return response.json()

    def search_market(self, epic):
        url = f"{self.base_url}/markets/{epic}"
        response = self.session.get(url, headers=self.headers)
        if not response.ok:
            raise Exception(f"Market lookup failed: {response.text}")
        return response.json().get('market', {})

    def rate_limit(self):
        sleep(1)  # Simple rate limiting

# Example usage
if __name__ == '__main__':
    client = IGClient()
    print(client.get_account_info())