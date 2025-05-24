#!/usr/bin/env python3
"""
Quick test to confirm India endpoint works with your API credentials
"""

from delta_rest_client import DeltaRestClient

# Your API credentials
API_KEY = "OIG5ggif59gm7ZHJjquBA7cIZF0At7"
API_SECRET = "idFFiuukXBfi5SdYne4nHx1mntfbV60YL9UU9SOSmpJwpgErGYgigNDD5XQO"

print("🇮🇳 Testing Delta Exchange INDIA endpoint...")

# Test India endpoint
delta_client = DeltaRestClient(
    base_url='https://api.india.delta.exchange',
    api_key=API_KEY,
    api_secret=API_SECRET
)

try:
    # Test with USDT (asset ID 5)
    balance = delta_client.get_balances(5)  # USDT asset ID
    print("✅ SUCCESS! Your API credentials work with India endpoint!")
    print(f"USDT Balance: {balance}")
    
    # Test live orders
    orders = delta_client.get_live_orders()
    print(f"✅ Live orders work too! Found {len(orders)} orders")
    
    print("\n🎉 CONCLUSION: Use https://api.india.delta.exchange for all your API calls!")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    print("Check your API key permissions in Delta Exchange India dashboard")