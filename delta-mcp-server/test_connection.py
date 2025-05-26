# Save as test_connection.py
import requests
import json
import hmac
import hashlib
import time

def test_delta_connection():
    api_key = "OIG5ggif59gm7ZHJjquBA7cIZF0At7"
    api_secret = "idFFiuukXBfi5SdYne4nHx1mntfbV60YL9UU9SOSmpJwpgErGYgigNDD5XQO"
    base_url = "https://api.india.delta.exchange"
    
    # Test public endpoint (no auth required)
    response = requests.get(f"{base_url}/v2/products")
    print(f"Public endpoint test: {response.status_code}")
    
    if response.status_code == 200:
        products = response.json()
        print(f"Found {len(products)} products")
        
        # Find ETHUSD product
        for product in products:
            if product.get('symbol') == 'ETHUSD' and product.get('id') == 3136:
                print(f"Found ETHUSD with ID 3136: {product}")
                break
    
    # Test private endpoint (auth required)
    timestamp = str(int(time.time()))
    method = "GET"
    endpoint = "/v2/wallet/balances"
    
    signature_data = method + timestamp + endpoint
    signature = hmac.new(
        api_secret.encode('utf-8'),
        signature_data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        'api-key': api_key,
        'signature': signature,
        'timestamp': timestamp,
        'Content-Type': 'application/json',
        'User-Agent': 'python-3.10'
    }
    
    response = requests.get(f"{base_url}{endpoint}", headers=headers)
    print(f"Private endpoint test: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_delta_connection()