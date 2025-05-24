#!/usr/bin/env python3
"""
Delta Exchange MCP Server - Complete Working Version
Provides tools for interacting with Delta Exchange API
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

# Correct MCP imports
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
    def __init__(self):
        # Get API credentials from environment variables
        self.api_key = os.getenv("DELTA_API_KEY", "OIG5ggif59gm7ZHJjquBA7cIZF0At7")
        self.api_secret = os.getenv("DELTA_API_SECRET", "idFFiuukXBfi5SdYne4nHx1mntfbV60YL9UU9SOSmpJwpgErGYgigNDD5XQO")
        self.base_url = os.getenv("DELTA_BASE_URL", "https://api.india.delta.exchange")
        
        logger.info(f"Initialized Delta Exchange API client")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"API Key: {self.api_key[:10]}...{self.api_key[-5:]}")
        
    def _generate_signature(self, method: str, endpoint: str, query_string: str = "", payload: str = "") -> tuple[str, str]:
        """Generate signature for Delta Exchange API using their exact format"""
        timestamp = str(int(time.time()))
        
        # Create the signature data using Delta Exchange format:
        # method + timestamp + path + query_string + body
        signature_data = method + timestamp + endpoint + query_string + payload
        
        logger.debug(f"Signature data: {signature_data}")
        
        # Generate HMAC signature
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature, timestamp
    
    async def _make_request(self, method: str, endpoint: str, params: dict = None, data: dict = None) -> dict:
        """Make authenticated request to Delta Exchange API"""
        url = f"{self.base_url}{endpoint}"
        
        # Prepare query string and payload
        query_string = ""
        payload = ""
        
        if method == "GET" and params:
            query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
            url += query_string
        elif method in ["POST", "PUT"] and data:
            payload = json.dumps(data, separators=(',', ':'))  # No spaces in JSON
        
        # Generate signature
        signature, timestamp = self._generate_signature(method, endpoint, query_string, payload)
        
        # Prepare headers with required User-Agent
        headers = {
            'api-key': self.api_key,
            'signature': signature,
            'timestamp': timestamp,
            'Content-Type': 'application/json',
            'User-Agent': 'python-3.10'  # REQUIRED by Delta Exchange API
        }
        
        logger.info(f"Making {method} request to: {url}")
        
        # Make request
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

# Create the MCP server
app = Server("delta-exchange")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools for Delta Exchange API"""
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
                        "type": "integer",
                        "description": "Order size/quantity",
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
                        "description": "Order type: 'MARKET' or 'LIMIT'",
                        "enum": ["MARKET", "LIMIT"],
                        "default": "LIMIT",
                    },
                    "time_in_force": {
                        "type": "string",
                        "description": "Time in force: 'GTC', 'IOC', or 'FOK'",
                        "enum": ["GTC", "IOC", "FOK"],
                        "default": "GTC",
                    },
                },
                "required": ["product_id", "size", "side"],
            },
        ),
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> CallToolResult:
    """Handle tool calls for Delta Exchange API"""
    
    if name == "get_assets":
        try:
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
    
    elif name == "place_order":
        try:
            if not arguments:
                return CallToolResult(
                    content=[TextContent(type="text", text="Order parameters are required")],
                    isError=True,
                )
            
            # Extract parameters
            product_id = arguments.get("product_id")
            size = str(arguments.get("size"))  # Convert to string
            side = arguments.get("side")
            limit_price = arguments.get("limit_price")
            order_type = arguments.get("order_type", "LIMIT").lower()
            time_in_force = arguments.get("time_in_force", "GTC").lower()
            
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