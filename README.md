# Delta Exchange API Integration Suite

A comprehensive Python-based integration suite for the Delta Exchange API, providing both testing and production-ready components for interacting with the Delta Exchange platform.

## Project Structure

```
delta-mcp-server/
├── delta_api_test.py      # Comprehensive API test suite
├── delta_official_test.py # Official client test script
├── server.py             # MCP server implementation
├── test_server.py        # Server test script
└── requirements.txt      # Project dependencies
```

## Features

### API Test Suite (`delta_api_test.py`)
- Complete endpoint testing
- Secure authentication handling
- Detailed logging and error reporting
- Support for both public and private endpoints
- Order placement and management
- Wallet balance checking
- Position tracking

### MCP Server (`server.py`)
- Model-Controller-Provider interface
- Async request handling
- Tool-based API access
- Comprehensive error handling
- Secure credential management

### Official Client Test (`delta_official_test.py`)
- India endpoint verification
- Basic API functionality testing
- Balance and order management

## Prerequisites

- Python 3.10 or higher
- Required Python packages:
  - requests
  - httpx (for async support)
  - python-dotenv
  - delta-rest-client
  - mcp-server

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SirCharan/Delta.git
cd Delta
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (create a `.env` file):
```env
DELTA_API_KEY=your_api_key
DELTA_API_SECRET=your_api_secret
DELTA_BASE_URL=https://api.india.delta.exchange
```

## Usage

### Running the Test Suite
```bash
python delta-mcp-server/delta_api_test.py
```

### Testing the Server
```bash
python delta-mcp-server/test_server.py
```

### Running the MCP Server
```bash
python delta-mcp-server/server.py
```

## API Endpoints Tested

- Products (`/v2/products`)
- Ticker (`/v2/tickers`)
- Wallet Balances (`/v2/wallet/balances`)
- Positions (`/v2/positions`)
- Orders (`/v2/orders`)
- Order Placement (`/v2/orders` POST)
- Order Cancellation (`/v2/orders/{id}` DELETE)

## Security Features

- API credentials handled securely
- HMAC-SHA256 request signing
- HTTPS enforced for all communications
- Environment variable configuration
- Secure error handling

## Logging

The suite includes comprehensive logging with the following levels:
- DEBUG: Detailed request/response information
- INFO: General operation status
- ERROR: Error conditions and failures

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Delta Exchange API Documentation
- Python MCP Server Framework
- Delta Exchange Python Client 