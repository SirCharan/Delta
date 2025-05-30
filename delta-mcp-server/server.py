#!/usr/bin/env python3
"""
Delta Exchange MCP Server - FIXED VERSION

Key fixes:
1. Proper CallToolResult content construction
2. Updated import for newer MCP version
3. Fixed TextContent construction
4. Better error handling format
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

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("delta-mcp-server")

class DeltaExchangeAPI:
    def __init__(self):
        self.api_key = os.getenv("DELTA_API_KEY", "OIG5ggif59gm7ZHJjquBA7cIZF0At7")
        self.api_secret = os.getenv("DELTA_API_SECRET", "idFFiuukXBfi5SdYne4nHx1mntfbV60YL9UU9SOSmpJwpgErGYgigNDD5XQO")
        self.base_url = os.getenv("DELTA_BASE_URL", "https://api.india.delta.exchange")
        
        logger.info(f"Initialized Delta Exchange API client")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"API Key: {self.api_key[:10]}...{self.api_key[-5:]}")
        
    def _generate_signature(self, method: str, endpoint: str, query_string: str = "", payload: str = "") -> tuple[str, str]:
        timestamp = str(int(time.time()))
        signature_data = method + timestamp + endpoint + query_string + payload
        
        logger.debug(f"🔏 Signature generation:")
        logger.debug(f"   Method: {method}")
        logger.debug(f"   Timestamp: {timestamp}")
        logger.debug(f"   Endpoint: {endpoint}")
        logger.debug(f"   Full signature data: {signature_data}")
        
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature, timestamp
    
    async def _make_request(self, method: str, endpoint: str, params: dict = None, data: dict = None) -> dict:
        url = f"{self.base_url}{endpoint}"
        
        query_string = ""
        payload = ""
        
        if method == "GET" and params:
            query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
            url += query_string
        elif method in ["POST", "PUT"] and data:
            payload = json.dumps(data, separators=(',', ':'))
        
        signature, timestamp = self._generate_signature(method, endpoint, query_string, payload)
        
        headers = {
            'api-key': self.api_key,
            'signature': signature,
            'timestamp': timestamp,
            'Content-Type': 'application/json',
            'User-Agent': 'python-3.10'
        }
        
        logger.info(f"Making {method} request to: {url}")
        logger.info(f"Headers: {dict(headers)}")
        if payload:
            logger.info(f"Payload: {payload}")
        
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
                logger.info(f"Response text: {response.text}")
                
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

delta_api = DeltaExchangeAPI()
app = Server("delta-exchange")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_assets",
            description="Get list of all available assets on Delta Exchange",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_products",
            description="Get list of all available trading products on Delta Exchange",
            inputSchema={"type": "object", "properties": {}},
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
    try:
        if name == "get_assets":
            result = await delta_api._make_request("GET", "/v2/assets")
            
            if "error" in result:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error getting assets: {result['error']}")],
                    isError=True
                )
            
            assets = result.get('result', result) if isinstance(result, dict) else result
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Available assets ({len(assets)} total):\n{json.dumps(assets, indent=2)}")],
                isError=False
            )
        
        elif name == "get_products":
            result = await delta_api._make_request("GET", "/v2/products")
            
            if "error" in result:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error getting products: {result['error']}")],
                    isError=True
                )
            
            products = result.get('result', result) if isinstance(result, dict) else result
            
            # Format products list for readability
            product_list = []
            for product in products:
                if isinstance(product, dict):
                    product_info = f"ID: {product.get('id', 'N/A')}, Symbol: {product.get('symbol', 'N/A')}, Type: {product.get('contract_type', 'N/A')}"
                    product_list.append(product_info)
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Available products ({len(products)} total):\n" + "\n".join(product_list[:50]) + f"\n\n... showing first 50 of {len(products)} products")],
                isError=False
            )
        
        elif name == "get_ticker":
            symbol = arguments.get("symbol") if arguments else None
            if not symbol:
                return CallToolResult(
                    content=[TextContent(type="text", text="Symbol is required")],
                    isError=True
                )
            
            result = await delta_api._make_request("GET", f"/v2/tickers/{symbol}")
            
            if "error" in result:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error getting ticker: {result['error']}")],
                    isError=True
                )
            
            ticker_data = result.get('result', result) if isinstance(result, dict) else result
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Ticker data for {symbol}:\n{json.dumps(ticker_data, indent=2)}")],
                isError=False
            )
        
        elif name == "place_order":
            if not arguments:
                return CallToolResult(
                    content=[TextContent(type="text", text="Order parameters are required")],
                    isError=True
                )
            
            product_id = arguments.get("product_id")
            size = str(arguments.get("size"))
            side = arguments.get("side")
            limit_price = arguments.get("limit_price")
            order_type = arguments.get("order_type", "limit_order")
            time_in_force = arguments.get("time_in_force", "gtc")
            
            if not all([product_id, size, side]):
                return CallToolResult(
                    content=[TextContent(type="text", text="product_id, size, and side are required")],
                    isError=True
                )
            
            # Prepare order data exactly as API expects
            order_data = {
                "product_id": int(product_id),
                "side": str(side),
                "size": str(size),
                "order_type": str(order_type),
                "time_in_force": str(time_in_force),
            }
            
            if limit_price:
                order_data["limit_price"] = str(limit_price)
            
            logger.info(f"Placing order: {order_data}")
            
            result = await delta_api._make_request("POST", "/v2/orders", data=order_data)
            
            if "error" in result:
                error_msg = f"Failed to place order: {result['error']}"
                logger.error(error_msg)
                return CallToolResult(
                    content=[TextContent(type="text", text=error_msg)],
                    isError=True
                )
            
            order_result = result.get('result', result) if isinstance(result, dict) else result
            success_msg = f"✅ Order placed successfully!\n\nOrder Details:\n{json.dumps(order_result, indent=2)}"
            
            return CallToolResult(
                content=[TextContent(type="text", text=success_msg)],
                isError=False
            )
        
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                isError=True
            )
    
    except Exception as e:
        error_msg = f"Error executing tool '{name}': {str(e)}"
        logger.error(error_msg)
        return CallToolResult(
            content=[TextContent(type="text", text=error_msg)],
            isError=True
        )

async def main():
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