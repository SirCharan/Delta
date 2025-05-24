#!/usr/bin/env python3
"""
Complete test script for Delta Exchange API - All fixes applied

This script provides a comprehensive test suite for the Delta Exchange API,
including market data, trading, and account management endpoints.
It implements proper authentication, error handling, and logging.
"""

# Standard library imports
import requests  # For making HTTP requests
import json     # For JSON data handling
import hmac     # For HMAC signature generation
import hashlib  # For SHA256 hashing
import time     # For timestamp generation
import logging  # For detailed logging
from urllib.parse import urlencode  # For URL parameter encoding

# Configure logging with timestamp, level, and message format
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for maximum verbosity
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeltaExchangeAPITester:
    """
    Main class for testing Delta Exchange API endpoints.
    Handles authentication, request signing, and API communication.
    """
    
    def __init__(self):
        """
        Initialize the API tester with credentials and base URL.
        Note: In production, these should be loaded from environment variables.
        """
        self.api_key = "OIG5ggif59gm7ZHJjquBA7cIZF0At7"
        self.api_secret = "idFFiuukXBfi5SdYne4nHx1mntfbV60YL9UU9SOSmpJwpgErGYgigNDD5XQO"
        self.base_url = "https://api.india.delta.exchange"  # India endpoint!

    def _generate_signature(self, method, endpoint, query_string="", payload="", skip_detailed_logging=False):
        """
        Generate HMAC-SHA256 signature for API authentication.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint path
            query_string (str): URL query parameters
            payload (str): Request body for POST/PUT requests
            skip_detailed_logging (bool): Whether to skip detailed logging
            
        Returns:
            tuple: (signature, timestamp)
        """
        timestamp = str(int(time.time()))
            
        # Create signature data following Delta Exchange format:
        # method + timestamp + path + query_string + body
        signature_data = method + timestamp + endpoint + query_string + payload
        
        # Log signature generation details if not skipped
        if not skip_detailed_logging:
            logger.debug(f"Signature generation:")
            logger.debug(f"  Method: {method}")
            logger.debug(f"  Endpoint: {endpoint}")
            logger.debug(f"  Query String: {query_string}")
            logger.debug(f"  Payload: {payload}")
            logger.debug(f"  Timestamp: {timestamp}")
            logger.debug(f"  Signature data: {signature_data}")
            
        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if not skip_detailed_logging:
            logger.debug(f"  Generated signature: {signature}")
        
        return signature, timestamp

    def _make_request(self, method, endpoint, params=None, data=None):
        """
        Make an authenticated request to the Delta Exchange API.
        
        Args:
            method (str): HTTP method (GET, POST, PUT)
            endpoint (str): API endpoint path
            params (dict): Query parameters for GET requests
            data (dict): Request body for POST/PUT requests
            
        Returns:
            requests.Response or None: API response or None if request failed
        """
        url = f"{self.base_url}{endpoint}"
        
        # Skip detailed logging for large data endpoints
        skip_detailed_logging = endpoint in ["/v2/products", "/v2/tickers"]
        
        # Prepare query string and payload
        query_string = ""
        payload = ""
        
        # Handle GET request parameters
        if method == "GET" and params:
            query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
            url += query_string
            if not skip_detailed_logging:
                logger.debug(f"GET request with params: {query_string}")
        # Handle POST/PUT request data
        elif method in ["POST", "PUT"] and data:
            payload = json.dumps(data, separators=(',', ':'))  # Compact JSON
            if not skip_detailed_logging:
                logger.debug(f"POST/PUT request with data: {data}")
        
        if not skip_detailed_logging:
            logger.info(f"Making {method} request to: {url}")
        
        # Generate authentication signature
        signature, timestamp = self._generate_signature(method, endpoint, query_string, payload, skip_detailed_logging)
        
        # Prepare request headers
        headers = {
            'api-key': self.api_key,
            'signature': signature,
            'timestamp': timestamp,
            'Content-Type': 'application/json',
            'User-Agent': 'python-3.10'  # Required by Delta Exchange API
        }
        
        if not skip_detailed_logging:
            logger.debug(f"Request headers: {dict(headers)}")
        
        # Make the HTTP request
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=headers, data=payload, timeout=30)
            elif method == "PUT":
                response = requests.put(url, headers=headers, data=payload, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Log response details
            if not skip_detailed_logging:
                logger.info(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")
                # Only log response content for non-large endpoints
                if len(response.text) < 1000:
                    logger.debug(f"Response content: {response.text}")
                else:
                    logger.debug(f"Response content: [Large response - {len(response.text)} characters]")
            
            # Handle error responses
            if response.status_code >= 400:
                logger.error(f"Request failed with status {response.status_code}")
                logger.error(f"Error response: {response.text}")
                
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        logger.error(f"Error details: {error_data['error']}")
                    if 'errors' in error_data:
                        logger.error(f"Error list: {error_data['errors']}")
                    if 'message' in error_data:
                        logger.error(f"Error message: {error_data['message']}")
                except:
                    logger.error("Could not parse error response as JSON")
                
            return response
            
        except requests.exceptions.Timeout:
            logger.error("Request timed out")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected request error: {e}")
            return None

    def test_all_endpoints(self):
        """
        Test all major Delta Exchange API endpoints.
        This method runs through a series of tests for different API functionalities:
        1. Products endpoint (public)
        2. Ticker endpoint (public)
        3. Wallet balances (private)
        4. Positions (private)
        5. Orders (private)
        6. Order placement (trading)
        """
        logger.info("=== Delta Exchange API Test Started ===")
        logger.info(f"API Key: {self.api_key[:10]}...{self.api_key[-5:]}")
        logger.info(f"API Secret: {self.api_secret[:10]}...{self.api_secret[-5:]}")
        logger.info(f"Base URL: {self.base_url}")
        
        # Test 1: Get Products (Public endpoint)
        logger.info("\n=== PRODUCTS TEST ===")
        response = self._make_request("GET", "/v2/products")
        if response and response.status_code == 200:
            try:
                # Log raw response for debugging
                logger.debug(f"Raw response: {response.text}")
                
                # Parse JSON response
                products_data = response.json()
                
                # Log data structure
                logger.debug(f"Parsed data type: {type(products_data)}")
                logger.debug(f"Parsed data: {products_data}")
                
                # Extract products list from response
                if isinstance(products_data, dict) and 'result' in products_data:
                    products_list = products_data['result']
                else:
                    products_list = products_data
                
                logger.info(f"✅ Products API - SUCCESS")
                logger.info(f"Found {len(products_list)} products")
                
                # Find BTCUSDT product for later tests
                btcusdt_product = None
                for product in products_list:
                    if isinstance(product, dict) and product.get('symbol') == 'BTCUSDT':
                        btcusdt_product = product
                        break
                
                if btcusdt_product:
                    logger.info(f"BTCUSDT Product ID: {btcusdt_product['id']}")
                else:
                    logger.warning("BTCUSDT product not found in the response")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse response as JSON: {e}")
                return
            except Exception as e:
                logger.error(f"Error processing products data: {e}")
                return
        else:
            logger.error("❌ Products API - FAILED")
            return

        # Test 2: Get Ticker (Public endpoint)
        logger.info("\n=== TICKER TEST ===")
        response = self._make_request("GET", "/v2/tickers/BTCUSDT")
        if response and response.status_code == 200:
            ticker_data = response.json()
            logger.info(f"✅ Ticker API - SUCCESS")
            logger.info(f"BTCUSDT Price: ${ticker_data.get('close', 'N/A')}")
        else:
            logger.error("❌ Ticker API - FAILED")

        # Test 3: Get Wallet Balances (Private endpoint)
        logger.info("\n=== WALLET BALANCES TEST ===")
        logger.info("Attempting to fetch wallet balances...")
        response = self._make_request("GET", "/v2/wallet/balances")
        if response and response.status_code == 200:
            balance_data = response.json()
            logger.info("✅ Wallet Balances - SUCCESS")
            logger.info(f"Balance data: {json.dumps(balance_data, indent=2)}")
        else:
            logger.error("❌ Wallet balances test failed")

        # Test 4: Get Positions (Private endpoint)
        logger.info("\n=== POSITIONS TEST ===")
        logger.info("Attempting to fetch positions...")
        response = self._make_request("GET", "/v2/positions")
        if response and response.status_code == 200:
            positions_data = response.json()
            logger.info("✅ Positions API - SUCCESS")
            logger.info(f"Positions: {len(positions_data.get('result', []))}")
        else:
            logger.error("❌ Positions test failed")

        # Test 5: Get Orders (Private endpoint)
        logger.info("\n=== ORDERS TEST ===")
        logger.info("Attempting to fetch orders with state: all...")
        response = self._make_request("GET", "/v2/orders")
        if response and response.status_code == 200:
            orders_data = response.json()
            logger.info("✅ Orders API - SUCCESS")
            logger.info(f"Orders: {len(orders_data.get('result', []))}")
        else:
            logger.error("❌ Orders test failed")

        # Test 6: Place Order (Trading endpoint)
        if btcusdt_product:
            logger.info("\n=== ORDER PLACEMENT TEST ===")
            
            # Calculate test order price (50% below market to avoid execution)
            current_price = ticker_data.get('close', 100000)
            test_price = round(current_price * 0.5, 1)
            
            logger.info("Attempting to place order:")
            logger.info(f"  Product ID: {btcusdt_product['id']}")
            logger.info(f"  Side: buy")
            logger.info(f"  Size: 1")
            logger.info(f"  Price: {test_price}")
            
            # Prepare order data
            order_data = {
                'product_id': btcusdt_product['id'],
                'side': 'buy',
                'size': 1,
                'order_type': 'limit',
                'time_in_force': 'gtc',
                'limit_price': str(test_price)
            }
            
            # Place the order
            response = self._make_request("POST", "/v2/orders", data=order_data)
            if response and response.status_code == 200:
                order_result = response.json()
                logger.info("✅ Order Placement - SUCCESS!")
                logger.info(f"Order Result: {json.dumps(order_result, indent=2)}")
                
                # Cancel the test order
                order_id = order_result.get('result', {}).get('id')
                if order_id:
                    logger.info(f"Attempting to cancel order {order_id}...")
                    cancel_response = self._make_request("DELETE", f"/v2/orders/{order_id}")
                    if cancel_response and cancel_response.status_code == 200:
                        logger.info("✅ Order cancelled successfully")
                    else:
                        logger.warning("⚠️ Could not cancel order")
            else:
                logger.error("❌ Order placement failed")
                if response:
                    logger.error(f"No response received for order placement")

        logger.info("\n=== API Test Completed ===")

    def place_specific_order(self):
        """
        Place a specific test order for ETHUSD.
        This method demonstrates how to place a limit order for ETHUSD at a specific price.
        """
        logger.info("\n=== PLACING SPECIFIC ORDER ===")
        
        # Get all products to find ETHUSD
        response = self._make_request("GET", "/v2/products")
        if not response or response.status_code != 200:
            logger.error("Failed to get products")
            return
            
        try:
            # Parse products data
            products_data = response.json()
            if isinstance(products_data, dict) and 'result' in products_data:
                products_list = products_data['result']
            else:
                products_list = products_data
                
            # Find ETHUSD product
            ethusd_product = None
            for product in products_list:
                if isinstance(product, dict):
                    symbol = product.get('symbol', '')
                    logger.debug(f"Found product: {symbol}")
                    if symbol == 'ETHUSD':
                        ethusd_product = product
                        break
                    
            if not ethusd_product:
                logger.error("ETHUSD product not found in available products")
                logger.info("Available products:")
                for product in products_list:
                    if isinstance(product, dict):
                        logger.info(f"  - {product.get('symbol', 'Unknown')}")
                return
                
            # Log product details
            logger.info(f"Found ETHUSD product:")
            logger.info(f"  ID: {ethusd_product.get('id')}")
            logger.info(f"  Symbol: {ethusd_product.get('symbol')}")
            logger.info(f"  Contract Type: {ethusd_product.get('contract_type')}")
            logger.info(f"  Base Currency: {ethusd_product.get('base_currency')}")
            logger.info(f"  Quote Currency: {ethusd_product.get('quote_currency')}")
                
            # Prepare order data
            order_data = {
                'product_id': ethusd_product['id'],
                'side': 'buy',
                'size': 1,
                'order_type': 'limit_order',
                'time_in_force': 'gtc',
                'limit_price': '1000'
            }
            
            # Log order details
            logger.info("Placing order with parameters:")
            logger.info(f"  Product: ETHUSD")
            logger.info(f"  Side: buy")
            logger.info(f"  Size: 0.01 ETH (1 contract)")
            logger.info(f"  Price: $1000")
            
            # Place the order
            response = self._make_request("POST", "/v2/orders", data=order_data)
            
            if response and response.status_code == 200:
                order_result = response.json()
                logger.info("✅ Order placed successfully!")
                logger.info(f"Order details: {json.dumps(order_result, indent=2)}")
                
                # Store order ID for potential cancellation
                order_id = order_result.get('result', {}).get('id')
                if order_id:
                    logger.info(f"Order ID: {order_id}")
                    logger.info("Note: You may want to cancel this order if it doesn't execute")
            else:
                logger.error("❌ Failed to place order")
                if response:
                    logger.error(f"Error response: {response.text}")
                    
        except Exception as e:
            logger.error(f"Error placing order: {e}")

def main():
    """
    Main entry point for the test suite.
    Creates an instance of DeltaExchangeAPITester and runs all tests.
    """
    tester = DeltaExchangeAPITester()
    tester.test_all_endpoints()
    tester.place_specific_order()

if __name__ == "__main__":
    main()