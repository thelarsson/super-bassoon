#!/usr/bin/env python3
"""
Debug IG API connection
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import requests
from config import IG_API_KEY, IG_IDENTIFIER, IG_PASSWORD, IG_ACCOUNT_ID, IG_BASE_URL

print(f"Base URL: {IG_BASE_URL}")
print(f"API Key: {IG_API_KEY[:15]}...")
print(f"Username: {IG_IDENTIFIER}")
print(f"Account ID: {IG_ACCOUNT_ID}")
print()

# Step 1: Authenticate
print("Step 1: Authenticating...")
url = f"{IG_BASE_URL}/session"
headers = {'X-IG-API-KEY': IG_API_KEY}
payload = {
    "identifier": IG_IDENTIFIER,
    "password": IG_PASSWORD
}

try:
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Text: {response.text[:500]}")
    
    if response.ok:
        data = response.json()
        print(f"\n✅ Authenticated!")
        print(f"Token: {data.get('token', 'N/A')[:20]}...")
        
        # Step 2: Get account info
        print("\nStep 2: Getting account info...")
        token = data.get('token')
        headers['Authorization'] = f'Bearer {token}'
        
        account_url = f"{IG_BASE_URL}/accounts"
        acc_response = requests.get(account_url, headers=headers)
        print(f"Status: {acc_response.status_code}")
        print(f"Text: {acc_response.text[:1000]}")
        
    else:
        print(f"\n❌ Authentication failed: {response.text}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
