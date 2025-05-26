#!/usr/bin/env python3
"""
Direct ETHUSD Order Placement Script
Place the exact order you requested: Buy 1 ETHUSD perpetual at limit price 1000
"""

import requests
import json
import hmac
import hashlib
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Credentials
API_KEY = os.getenv("DELTA_API_KEY", "OIG5ggif59gm7ZHJjquBA7cIZF0At7")
API_SECRET = os.getenv("DELTA_API_SECRET", "idFFiuukXBfi5SdYne4nHx1mntfbV60YL9UU9SOSmpJwpgErGYgigNDD5XQO")
BASE_URL = "https://api.india.delta.exchange"

def generate_signature(method, endpoint, query_string="", payload=""):
    """Generate HMAC-SHA256 signature for Delta Exchange API"""
    timestamp = str(int(time.time()))
    signature_data = method + timestamp + endpoint + query_string + payload
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        signature_data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature, timestamp

def place_ethusd_order():
    """Place the exact order: Buy 1 ETHUSD perpetual at limit price 1000"""
    
    print("🚀 Placing ETHUSD Order...")
    print("=" * 50)
    print(f"Product ID: 3136 (ETHUSD Perpetual)")
    print(f"Side: BUY")
    print(f"Size: 1 contract")
    print(f"Limit Price: $1000")
    print(f"Order Type: Limit Order")
    print(f"Time in Force: GTC (Good Till Cancelled)")
    print("=" * 50)
    
    # Order parameters - exactly as you requested
    order_data = {
        "product_id": 3136,  # ETHUSD perpetual
        "side": "buy",
        "size": "1",
        "order_type": "limit_order",
        "time_in_force": "gtc",
        "limit_price": "1000"
    }
    
    # Prepare request
    endpoint = "/v2/orders"
    payload = json.dumps(order_data, separators=(',', ':'))
    signature, timestamp = generate_signature("POST", endpoint, "", payload)
    
    headers = {
        'api-key': API_KEY,
        'signature': signature,
        'timestamp': timestamp,
        'Content-Type': 'application/json',
        'User-Agent': 'python-3.10'
    }
    
    print(f"📡 Making request to: {BASE_URL}{endpoint}")
    print(f"📋 Payload: {payload}")
    
    try:
        # Place the order
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            headers=headers,
            data=payload,
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("\n🎉 SUCCESS! Order placed successfully!")
            result = response.json()
            
            if 'result' in result:
                order = result['result']
                print("\n📋 Order Details:")
                print(f"   Order ID: {order.get('id')}")
                print(f"   Status: {order.get('state')}")
                print(f"   Product: {order.get('product_symbol')}")
                print(f"   Side: {order.get('side')}")
                print(f"   Size: {order.get('size')}")
                print(f"   Limit Price: ${order.get('limit_price')}")
                print(f"   Created: {order.get('created_at')}")
                
                print(f"\n💰 Your order to BUY 1 ETHUSD contract at $1000 is now live!")
                print(f"🔗 Order ID {order.get('id')} is waiting for execution.")
                
            else:
                print(f"✅ Order submitted: {result}")
                
        elif response.status_code == 401:
            print("\n❌ Authentication Error!")
            print("🔧 Check your API credentials in the .env file")
            
        elif response.status_code == 400:
            print("\n❌ Bad Request!")
            try:
                error = response.json()
                print(f"Error details: {error}")
                if 'error' in error:
                    print(f"Error code: {error['error'].get('code')}")
                    print(f"Error message: {error['error'].get('message')}")
            except:
                print(f"Raw error: {response.text}")
                
        else:
            print(f"\n❌ Unexpected error (Status {response.status_code})")
            try:
                error = response.json()
                print(f"Error: {error}")
            except:
                print(f"Raw response: {response.text}")
                
    except requests.exceptions.Timeout:
        print("\n⏰ Request timed out")
    except requests.exceptions.ConnectionError:
        print("\n🌐 Connection error - check your internet connection")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")

def verify_credentials_first():
    """Quick verification that credentials work"""
    print("🔐 Verifying API credentials...")
    
    try:
        # Test with public endpoint first
        response = requests.get(f"{BASE_URL}/v2/products", timeout=10)
        print(f"📡 Response status: {response.status_code}")
        print(f"📄 Response content type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Check if response has the expected structure
                if not isinstance(data, dict):
                    print(f"❌ Expected dict response, got: {type(data)}")
                    return False
                
                # Check if 'result' key exists and contains the products list
                if 'result' not in data:
                    print(f"❌ No 'result' key found in response")
                    print(f"Available keys: {list(data.keys())}")
                    return False
                
                products = data['result']
                
                # Check if products is actually a list
                if not isinstance(products, list):
                    print(f"❌ Expected list of products in 'result', got: {type(products)}")
                    return False
                
                print(f"✅ API connection successful! Found {len(products)} products")
                
                # Find product 3136
                product_3136 = None
                for product in products:
                    if isinstance(product, dict) and product.get('id') == 3136:
                        product_3136 = product
                        break
                
                if product_3136:
                    print(f"✅ Product 3136 found: {product_3136.get('symbol')} - {product_3136.get('description')}")
                    return True
                else:
                    print("❌ Product ID 3136 not found!")
                    # Show first few products for debugging
                    print("Available products (first 5):")
                    for i, product in enumerate(products[:5]):
                        if isinstance(product, dict):
                            print(f"  {product.get('id')}: {product.get('symbol')}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {e}")
                print(f"Raw response: {response.text[:500]}...")
                return False
                
        else:
            print(f"❌ API connection failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Delta Exchange - ETHUSD Order Placement")
    print("=" * 60)
    
    # First verify connection and credentials
    if verify_credentials_first():
        print("\n" + "=" * 60)
        place_ethusd_order()
    else:
        print("\n🚨 Cannot proceed - fix connection issues first!")
    
    print("\n" + "=" * 60)
    print("Done!")