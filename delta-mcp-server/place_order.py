#!/usr/bin/env python3
"""
Direct script to place an order on Delta Exchange
This bypasses the MCP server and directly places the order
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

# API Credentials from environment variables
API_KEY = os.getenv("DELTA_API_KEY")
API_SECRET = os.getenv("DELTA_API_SECRET")
BASE_URL = "https://api.india.delta.exchange"

def generate_signature(method, endpoint, query_string="", payload=""):
    timestamp = str(int(time.time()))
    signature_data = method + timestamp + endpoint + query_string + payload
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        signature_data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature, timestamp

def place_order():
    # Order parameters
    order_data = {
        "product_id": 3136,  # ETHUSDT perpetual
        "side": "buy",
        "size": "1",  # 1 contract (0.01 ETH)
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
    
    # Make request
    response = requests.post(
        f"{BASE_URL}{endpoint}",
        headers=headers,
        data=payload,
        timeout=30
    )
    
    print(f"Response Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ Order placed successfully!")
        result = response.json()
        if 'result' in result:
            order = result['result']
            print(f"Order ID: {order.get('id')}")
            print(f"Status: {order.get('state')}")
    else:
        print("\n❌ Order failed!")
        try:
            error = response.json()
            print(f"Error: {error}")
        except:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    print("Placing order on Delta Exchange...")
    print(f"Product: ETHUSDT (ID: 176)")
    print(f"Side: BUY")
    print(f"Size: 1 contract (0.01 ETH)")
    print(f"Limit Price: $1000")
    print(f"Order Type: Limit Order")
    print("-" * 50)
    
    place_order()