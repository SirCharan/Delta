#!/usr/bin/env python3
"""
Quick test to confirm India endpoint works with your API credentials

This script uses the official Delta Exchange Python client to test connectivity
and basic functionality with the India endpoint. It verifies:
1. API credentials are valid
2. Can fetch USDT balance
3. Can fetch live orders
"""

# Import the official Delta Exchange REST client
from delta_rest_client import DeltaRestClient

# API credentials - In production, these should be loaded from environment variables
API_KEY = "OIG5ggif59gm7ZHJjquBA7cIZF0At7"
API_SECRET = "idFFiuukXBfi5SdYne4nHx1mntfbV60YL9UU9SOSmpJwpgErGYgigNDD5XQO"

print("🇮🇳 Testing Delta Exchange INDIA endpoint...")

# Initialize the Delta Exchange client with India endpoint
delta_client = DeltaRestClient(
    base_url='https://api.india.delta.exchange',  # India-specific endpoint
    api_key=API_KEY,
    api_secret=API_SECRET
)

try:
    # Test 1: Get USDT balance (asset ID 5)
    # This verifies basic API connectivity and authentication
    balance = delta_client.get_balances(5)  # USDT asset ID
    print("✅ SUCCESS! Your API credentials work with India endpoint!")
    print(f"USDT Balance: {balance}")
    
    # Test 2: Get live orders
    # This verifies trading API access and order management
    orders = delta_client.get_live_orders()
    print(f"✅ Live orders work too! Found {len(orders)} orders")
    
    print("\n🎉 CONCLUSION: Use https://api.india.delta.exchange for all your API calls!")
    
except Exception as e:
    # Handle any API errors
    print(f"❌ Failed: {e}")
    print("Check your API key permissions in Delta Exchange India dashboard")