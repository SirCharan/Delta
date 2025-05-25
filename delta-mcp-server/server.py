#!/usr/bin/env python3
"""
Delta Exchange MCP Server - Complete Fixed Version

This server provides a Model-Controller-Provider (MCP) interface for interacting with
the Delta Exchange API. 

IMPORTANT FIXES APPLIED:
1. Fixed CallToolResult format issues
2. Corrected API authentication headers
3. Added missing get_products endpoint
4. Using consistent India endpoint
5. Proper error handling
"""

import asyncio
import json
import logging
import hashlib
import hmac
import time
import os
from typing import Any, Sequence
import httpx

# MCP server imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("delta-mcp-server")

class DeltaExchangeAPI:
    """
    Delta Exchange API client for handling all API interactions.
    Implements authentication, request signing, and error handling.
    """
    
    def __init__(self):
        """
        Initialize the API client with credentials from environment variables.
        """
        # Load credentials from environment or use defaults
        self.api_key = os.getenv("DELTA_API_KEY", "OIG5ggif59gm7ZHJjquBA7cIZF0At7")
        self.api_secret = os.getenv("DELTA_API_SECRET", "idFFiuukXBfi5SdYne4nHx1mntfbV60YL9UU9SOSmpJwpgErGYgigNDD5XQO")
        
        # IMPORTANT: Use India endpoint consistently
        self.base_url = "https://api.india.delta.exchange"
        
        logger.info(f"Initialized Delta Exchange API client")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"API Key: {self.api_key[:10]}...{self.api_key[-5:]}")
        
    def _generate_signature(self, method: str, endpoint: str, query_string: str = "", payload: str = "") -> tuple[str, str]:
        """
        Generate HMAC-SHA256 signature for API authentication.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            query_string: URL query parameters
            payload: Request body for POST/PUT requests
            
        Returns:
            tuple: (signature, timestamp)
        """
        timestamp = str(int(time.time()))
        
        # Create signature data following Delta Exchange format:
        # method + timestamp + path + query_string + body
        signature_data = method + timestamp + endpoint + query_string + payload
        
        logger.debug(f"Signature data: {signature_data}")
        
        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature, timestamp
    
    async def _make_request(self, method: str, endpoint: str, params: dict = None, data: dict = None) -> dict:
        """
        Make an authenticated request to the Delta Exchange API.
        
        Args:
            method: HTTP method (GET, POST, PUT)
            endpoint: API endpoint path
            params: Query parameters for GET requests
            data: Request body for POST/PUT requests
            
        Returns:
            dict: API response or error information
        """
        url = f"{self.base_url}{endpoint}"
        
        # Prepare query string and payload
        query_string = ""
        payload = ""
        
        if method == "GET" and params:
            query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
            url += query_string
        elif method in ["POST", "PUT"] and data:
            payload = json.dumps(data, separators=(',', ':'))  # Compact JSON
        
        # Generate authentication signature
        signature, timestamp = self._generate_signature(method, endpoint, query_string, payload)
        
        # Prepare request headers with required User-Agent
        headers = {
            'api-key': self.api_key,
            'signature': signature,
            'timestamp': timestamp,
            'Content-Type': 'application/json',
            'User-Agent': 'python-3.10'  # REQUIRED by Delta Exchange API
        }
        
        logger.info(f"Making {method} request to: {url}")
        
        # Make async request
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                if method == "GET":
                    response = await client.get(url, headers=headers)
                elif method == "POST":
                    response = await client.post(url, headers=headers, content=payload)
                elif method == "PUT":
                    response = await client.put(url, headers=headers, content=payload)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                logger.info(f"Response status: {response.status_code}")
                
                # Handle error responses
                if response.status_code >= 400:
                    logger.error(f"Request failed with status {response.status_code}")
                    logger.error(f"Error response: {response.text}")
                    
                    try:
                        error_data = response.json()
                        if 'error' in error_data:
                            return {"error": error_data['error']}
                    except:
                        return {"error": {"code": "unknown_error", "message": response.text}}
                
                return response.json()
                
            except httpx.TimeoutException:
                logger.error("Request timed out")
                return {"error": {"code": "timeout", "message": "Request timed out"}}
            except Exception as e:
                logger.error(f"Request error: {e}")
                return {"error": {"code": "request_error", "message": str(e)}}

# Initialize the API client
delta_api = DeltaExchangeAPI()

# Create the MCP server instance
app = Server("delta-exchange")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List available tools for Delta Exchange API.
    Defines the schema and capabilities of each tool.
    
    Returns:
        list[Tool]: List of available API tools
    """
    return [
        Tool(
            name="get_assets",
            description="Get list of all available assets on Delta Exchange",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_ticker",
            description="Get current market ticker data for a trading symbol",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Trading symbol (e.g., BTCUSDT, ETHUSD)",
                    }
                },
                "required": ["symbol"],
            },
        ),
        Tool(
            name="get_products",
            description="Get list of all available trading products on Delta Exchange",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="place_order",
            description="Place a buy or sell order on Delta Exchange",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "integer",
                        "description": "Product ID of the trading instrument",
                    },
                    "size": {
                        "type": "string",
                        "description": "Order size/quantity (use string to avoid precision issues)",
                    },
                    "side": {
                        "type": "string",
                        "description": "Order side: 'buy' or 'sell'",
                        "enum": ["buy", "sell"],
                    },
                    "limit_price": {
                        "type": "string",
                        "description": "Limit price for the order (optional for market orders)",
                    },
                    "order_type": {
                        "type": "string",
                        "description": "Order type: 'market_order' or 'limit_order'",
                        "enum": ["market_order", "limit_order"],
                        "default": "limit_order",
                    },
                    "time_in_force": {
                        "type": "string",
                        "description": "Time in force: 'gtc', 'ioc', or 'fok'",
                        "enum": ["gtc", "ioc", "fok"],
                        "default": "gtc",
                    },
                },
                "required": ["product_id", "size", "side"],
            },
        ),
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> CallToolResult:
    """
    Handle tool calls for Delta Exchange API.
    
    Args:
        name: Name of the tool to call
        arguments: Tool-specific arguments
        
    Returns:
        CallToolResult: Result of the tool call
    """
    
    if name == "get_assets":
        try:
            # Get list of all assets
            result = await delta_api._make_request("GET", "/v2/assets")
            
            if "error" in result:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error getting assets: {result['error']}")],
                    isError=True,
                )
            
            # Handle different response formats
            if isinstance(result, list):
                assets = result
            elif isinstance(result, dict) and 'result' in result:
                assets = result['result']
            else:
                assets = []
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Available assets ({len(assets)} total):\n{json.dumps(assets, indent=2)}")],
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting assets: {str(e)}")],
                isError=True,
            )
    
    elif name == "get_ticker":
        try:
            # Get ticker data for a symbol
            symbol = arguments.get("symbol") if arguments else None
            if not symbol:
                return CallToolResult(
                    content=[TextContent(type="text", text="Symbol is required")],
                    isError=True,
                )
            
            result = await delta_api._make_request("GET", f"/v2/tickers/{symbol}")
            
            if "error" in result:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error getting ticker: {result['error']}")],
                    isError=True,
                )
            
            # Handle different response formats
            if isinstance(result, dict):
                if 'result' in result:
                    ticker_data = result['result']
                else:
                    ticker_data = result
            else:
                ticker_data = result
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Ticker data for {symbol}:\n{json.dumps(ticker_data, indent=2)}")],
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting ticker: {str(e)}")],
                isError=True,
            )
    
    elif name == "get_products":
        try:
            # Get list of all products
            result = await delta_api._make_request("GET", "/v2/products")
            
            if "error" in result:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error getting products: {result['error']}")],
                    isError=True,
                )
            
            # Handle different response formats
            if isinstance(result, list):
                products = result
            elif isinstance(result, dict) and 'result' in result:
                products = result['result']
            else:
                products = []
            
            # Find ETHUSD product if it exists
            ethusd_product = None
            for product in products:
                if isinstance(product, dict) and product.get('symbol') == 'ETHUSD':
                    ethusd_product = product
                    break
            
            if ethusd_product:
                logger.info(f"Found ETHUSD product with ID: {ethusd_product.get('id')}")
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Available products ({len(products)} total):\n{json.dumps(products, indent=2)}")],
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting products: {str(e)}")],
                isError=True,
            )
    
    elif name == "place_order":
        try:
            # Place a new order
            if not arguments:
                return CallToolResult(
                    content=[TextContent(type="text", text="Order parameters are required")],
                    isError=True,
                )
            
            # Extract and validate order parameters
            product_id = arguments.get("product_id")
            size = str(arguments.get("size"))  # Convert to string
            side = arguments.get("side")
            limit_price = arguments.get("limit_price")
            order_type = arguments.get("order_type", "limit_order")
            time_in_force = arguments.get("time_in_force", "gtc")
            
            # Validate required parameters
            if not all([product_id, size, side]):
                return CallToolResult(
                    content=[TextContent(type="text", text="product_id, size, and side are required")],
                    isError=True,
                )
            
            # Prepare order data
            order_data = {
                "product_id": product_id,
                "side": side,
                "size": size,
                "order_type": order_type,
                "time_in_force": time_in_force,
            }
            
            # Add limit price if provided or if order type is limit
            if limit_price:
                order_data["limit_price"] = str(limit_price)
            
            # Place the order
            result = await delta_api._make_request("POST", "/v2/orders", data=order_data)
            
            if "error" in result:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Failed to place order: {result['error']}")],
                    isError=True,
                )
            
            # Handle different response formats
            if isinstance(result, dict):
                if 'result' in result:
                    order_result = result['result']
                else:
                    order_result = result
            else:
                order_result = result
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Order placed successfully:\n{json.dumps(order_result, indent=2)}")],
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error placing order: {str(e)}")],
                isError=True,
            )
    
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Unknown tool: {name}")],
            isError=True,
        )

async def main():
    """
    Main entry point for the MCP server.
    Initializes and runs the server with stdio communication.
    """
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="delta-exchange",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())