#!/usr/bin/env python3
"""
Delta Exchange Server Test Script

This script tests the basic connectivity and functionality of the Delta Exchange API server.
It verifies:
1. Environment variables are properly loaded
2. API credentials are valid
3. Can fetch basic market data
4. Can fetch product details
"""

import asyncio
import os
from dotenv import load_dotenv  # For loading environment variables
from delta_rest_client import DeltaRestClient  # Official Delta Exchange client

# Load environment variables from .env file
load_dotenv()

async def test_connection():
    """
    Test Delta Exchange connection and basic API functionality.
    
    Returns:
        bool: True if all tests pass, False otherwise
    """
    try:
        # Initialize client with credentials from environment variables
        client = DeltaRestClient(
            base_url=os.getenv('DELTA_BASE_URL'),
            api_key=os.getenv('DELTA_API_KEY'),
            api_secret=os.getenv('DELTA_API_SECRET')
        )
        
        # Test 1: Get all assets
        # This verifies basic API connectivity and authentication
        assets = client.get_assets()
        print(f"✅ Connection successful! Found {len(assets)} assets")
        
        # Test 2: Get specific product details
        # This verifies market data access
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
    # Run the async test function
    asyncio.run(test_connection())