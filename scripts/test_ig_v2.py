#!/usr/bin/env python3
"""
Test IG API connection v2
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from ig_client import IGClient

print("Creating IGClient...")
client = IGClient()
print("✅ Connected!")

print("\nGetting account info...")
url = f"{client.base_url}/accounts"
response = client.session.get(url, headers=client.headers)
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Text length: {len(response.text)}")
print(f"\nFirst 1000 chars:")
print(response.text[:1000])
