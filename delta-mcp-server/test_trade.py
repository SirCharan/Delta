#!/usr/bin/env python3
"""
Quick test to verify Delta Exchange API credentials and find product ID
Run this first before attempting any trading
"""

import requests
import json
import hmac
import hashlib
import time

def test_delta_exchange():
    # Your credentials
    API_KEY = "OIG5ggif59gm7ZHJjquBA7cIZF0At7"
    API_SECRET = "idFFiuukXBfi5SdYne4nHx1mntfbV60YL9UU9SOSmpJwpgErGYgigNDD5XQO"
    BASE_URL = "https://api.india.delta.exchange"
    
    print("🔍 Testing Delta Exchange API...")
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:]}")
    print(f"Base URL: {BASE_URL}")
    
    # Test 1: Public endpoint (should always work)
    print("\n📊 Testing public products endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/v2/products")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Found {len(products)} products")
            
            # Look for ETHUSD products
            eth_products = [p for p in products if 'ETH' in p.get('symbol', '') and 'USD' in p.get('symbol', '')]
            print(f"\n🎯 ETHUSD products found:")
            for product in eth_products:
                print(f"   ID: {product.get('id')}, Symbol: {product.get('symbol')}, Type: {product.get('contract_type')}")
            
            # Check for product ID 3136 specifically
            product_3136 = next((p for p in products if p.get('id') == 3136), None)
            if product_3136:
                print(f"\n✅ Product ID 3136 found: {product_3136.get('symbol')} ({product_3136.get('contract_type')})")
            else:
                print(f"\n❌ Product ID 3136 not found")
                
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Private endpoint (authentication test)
    print("\n🔐 Testing authentication...")
    try:
        timestamp = str(int(time.time()))
        method = "GET"
        endpoint = "/v2/wallet/balances"
        
        # Generate signature
        signature_data = method + timestamp + endpoint
        signature = hmac.new(
            API_SECRET.encode('utf-8'),
            signature_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'api-key': API_KEY,
            'signature': signature,
            'timestamp': timestamp,
            'Content-Type': 'application/json',
            'User-Agent': 'python-3.10'
        }
        
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Authentication successful!")
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed!")
            print("🔧 ACTION NEEDED:")
            print("   1. Check API key has trading permissions")
            print("   2. Verify API key is active")
            print("   3. Check if IP whitelisting is required")
            return False
        else:
            print(f"❌ Unexpected error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_delta_exchange()
    if success:
        print("\n🎉 API is ready for trading!")
    else:
        print("\n🚨 Fix authentication before proceeding with trading!")