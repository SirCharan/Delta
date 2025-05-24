#!/usr/bin/env python3
import asyncio
import os
from dotenv import load_dotenv
from delta_rest_client import DeltaRestClient

load_dotenv()

async def test_connection():
    """Test Delta Exchange connection"""
    try:
        client = DeltaRestClient(
            base_url=os.getenv('DELTA_BASE_URL'),
            api_key=os.getenv('DELTA_API_KEY'),
            api_secret=os.getenv('DELTA_API_SECRET')
        )
        
        # Test basic connection
        assets = client.get_assets()
        print(f"✅ Connection successful! Found {len(assets)} assets")
        
        # Test getting a product (Bitcoin futures typically have product_id around 1-100)
        try:
            product = client.get_product(1)  # Adjust this ID based on available products
            print(f"✅ Product details retrieved: {product.get('symbol', 'Unknown')}")
        except Exception as e:
            print(f"⚠️  Could not get product details: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())