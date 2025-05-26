#!/usr/bin/env python3
"""
Test script to debug the verification function
"""

import requests
import json

BASE_URL = "https://api.india.delta.exchange"

def test_verification():
    """Test the verification logic step by step"""
    print("🔐 Testing verification logic...")
    
    try:
        # Test with public endpoint first
        response = requests.get(f"{BASE_URL}/v2/products", timeout=10)
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ JSON parsing successful")
                print(f"📊 Type of response: {type(data)}")
                
                # Show the structure of the response
                if isinstance(data, dict):
                    print(f"📋 Response keys: {list(data.keys())}")
                    
                    # Check if there's a 'result' key containing the products
                    if 'result' in data:
                        products = data['result']
                        print(f"📊 Type of data['result']: {type(products)}")
                        
                        if isinstance(products, list):
                            print(f"✅ Found products list with {len(products)} items")
                            
                            # Find product 3136
                            product_3136 = None
                            for i, product in enumerate(products):
                                if isinstance(product, dict) and product.get('id') == 3136:
                                    product_3136 = product
                                    print(f"🎯 Found product 3136 at index {i}")
                                    break
                            
                            if product_3136:
                                print(f"✅ Product 3136 found: {product_3136.get('symbol')} - {product_3136.get('description')}")
                                print("🎉 Verification should return True")
                                return True
                            else:
                                print("❌ Product ID 3136 not found!")
                                # Show first few products for debugging
                                print("Available products (first 5):")
                                for i, product in enumerate(products[:5]):
                                    if isinstance(product, dict):
                                        print(f"  {product.get('id')}: {product.get('symbol')}")
                                return False
                        else:
                            print(f"❌ data['result'] is not a list: {type(products)}")
                            return False
                    else:
                        print(f"❌ No 'result' key found in response")
                        print(f"📄 First 200 chars of response: {str(data)[:200]}...")
                        return False
                else:
                    print(f"❌ Response is not a dict: {type(data)}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {e}")
                return False
                
        else:
            print(f"❌ API connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    result = test_verification()
    print(f"\n🔍 Final result: {result}")
    print(f"🔍 Result type: {type(result)}") 