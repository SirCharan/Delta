#!/usr/bin/env python3
"""
Direct ETHUSD Order Placement Script
This bypasses the MCP server and places the order directly using your working API credentials
"""

import requests
import json
import hmac
import hashlib
import time

def place_ethusd_order():
    # Your working API credentials
    API_KEY = "OIG5ggif59gm7ZHJjquBA7cIZF0At7"
    API_SECRET = "idFFiuukXBfi5SdYne4nHx1mntfbV60YL9UU9SOSmpJwpgErGYgigNDD5XQO"
    
    # CRITICAL: Use the URL from your .env file (not the India endpoint)
    BASE_URL = "https://api.india.delta.exchange"
    
    # Order parameters for ETHUSD
    order_data = {
        "product_id": 3136,        # ETHUSD product ID you specified
        "side": "buy",             # Buy order
        "size": "1",               # 1 contract
        "order_type": "limit_order", # Limit order type
        "time_in_force": "gtc",    # Good till cancelled
        "limit_price": "1000"      # $1000 limit price
    }
    
    print("🚀 Delta Exchange - Placing ETHUSD Order")
    print("=" * 50)
    print(f"📍 Base URL: {BASE_URL}")
    print(f"🎯 Product ID: {order_data['product_id']}")
    print(f"📊 Side: {order_data['side']}")
    print(f"📏 Size: {order_data['size']} contract")
    print(f"💰 Limit Price: ${order_data['limit_price']}")
    print(f"⏰ Order Type: {order_data['order_type']}")
    print("=" * 50)
    
    try:
        # Prepare request
        endpoint = "/v2/orders"
        method = "POST"
        payload = json.dumps(order_data, separators=(',', ':'))
        timestamp = str(int(time.time()))
        
        # Generate signature (Delta Exchange format)
        signature_data = method + timestamp + endpoint + payload
        signature = hmac.new(
            API_SECRET.encode('utf-8'),
            signature_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Prepare headers
        headers = {
            'api-key': API_KEY,
            'signature': signature,
            'timestamp': timestamp,
            'Content-Type': 'application/json',
            'User-Agent': 'python-3.10'
        }
        
        print("📤 Sending order request...")
        print(f"🔗 URL: {BASE_URL}{endpoint}")
        print(f"📋 Headers: {dict((k, v if k != 'api-key' else f'{v[:10]}...{v[-5:]}') for k, v in headers.items())}")
        print(f"📦 Payload: {payload}")
        
        # Make the request
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            headers=headers,
            data=payload,
            timeout=30
        )
        
        print(f"\n📬 Response received:")
        print(f"🏷️  Status Code: {response.status_code}")
        print(f"📄 Response Body: {response.text}")
        
        # Handle response
        if response.status_code == 200:
            result = response.json()
            print("\n🎉 SUCCESS! ORDER PLACED!")
            print("=" * 50)
            
            if 'result' in result:
                order_info = result['result']
                print(f"📋 Order ID: {order_info.get('id', 'N/A')}")
                print(f"📊 Status: {order_info.get('state', 'N/A')}")
                print(f"🎯 Product: {order_info.get('product_id', 'N/A')}")
                print(f"📏 Size: {order_info.get('size', 'N/A')}")
                print(f"💰 Price: ${order_info.get('limit_price', 'N/A')}")
                print(f"⏰ Time in Force: {order_info.get('time_in_force', 'N/A')}")
            
            print(f"\n📝 Full Response:")
            print(json.dumps(result, indent=2))
            
        elif response.status_code == 400:
            print("\n❌ ORDER FAILED - Bad Request")
            try:
                error = response.json()
                print(f"📝 Error Details: {json.dumps(error, indent=2)}")
                
                # Provide specific guidance based on error
                error_str = str(error).lower()
                if 'product_id' in error_str:
                    print("\n🔧 POSSIBLE FIX:")
                    print("   - Product ID 3136 might be invalid or not available")
                    print("   - Run get_products to find the correct ETHUSD product ID")
                elif 'insufficient' in error_str:
                    print("\n🔧 POSSIBLE FIX:")
                    print("   - Check your account balance")
                    print("   - Ensure you have sufficient funds for this trade")
                elif 'price' in error_str:
                    print("\n🔧 POSSIBLE FIX:")
                    print("   - Limit price $1000 might be too far from market price")
                    print("   - Check current ETHUSD price and adjust limit price")
                    
            except:
                print(f"📝 Raw Error: {response.text}")
                
        elif response.status_code == 401:
            print("\n❌ ORDER FAILED - Authentication Error")
            print("🔧 This should not happen since you confirmed API works")
            print("   - Check if you're using the correct base URL")
            print("   - Verify API key permissions are still active")
            
        elif response.status_code == 404:
            print("\n❌ ORDER FAILED - Endpoint Not Found")
            print("🔧 POSSIBLE FIX:")
            print("   - Check if the base URL is correct")
            print("   - Verify the endpoint path /v2/orders exists")
            
        else:
            print(f"\n❌ ORDER FAILED - HTTP {response.status_code}")
            print(f"📝 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ REQUEST ERROR: {e}")
        print("🔧 Check your internet connection and try again")
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print("🔧 Please check the error details above")

if __name__ == "__main__":
    place_ethusd_order()