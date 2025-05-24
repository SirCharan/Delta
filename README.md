# Delta Exchange API Test Suite

A comprehensive Python test suite for interacting with the Delta Exchange API. This project provides a robust implementation for testing various endpoints of the Delta Exchange platform, including market data, trading, and account management features.

## Features

- Complete API endpoint testing
- Secure authentication handling
- Detailed logging and error reporting
- Support for both public and private endpoints
- Order placement and management
- Wallet balance checking
- Position tracking

## Prerequisites

- Python 3.10 or higher
- Required Python packages:
  - requests
  - hmac
  - hashlib
  - json
  - logging

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd delta-exchange-api-test
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The API credentials are configured in the `DeltaExchangeAPITester` class. Replace the following values with your own:

```python
self.api_key = "YOUR_API_KEY"
self.api_secret = "YOUR_API_SECRET"
```

## Usage

Run the test suite:

```bash
python delta_api_test.py
```

The script will:
1. Test all major API endpoints
2. Place a test order for ETHUSD
3. Provide detailed logging of all operations

## API Endpoints Tested

- Products (`/v2/products`)
- Ticker (`/v2/tickers`)
- Wallet Balances (`/v2/wallet/balances`)
- Positions (`/v2/positions`)
- Orders (`/v2/orders`)
- Order Placement (`/v2/orders` POST)
- Order Cancellation (`/v2/orders/{id}` DELETE)

## Logging

The script includes comprehensive logging with the following levels:
- DEBUG: Detailed request/response information
- INFO: General operation status
- ERROR: Error conditions and failures

## Security

- API credentials are handled securely
- All requests are properly signed
- HTTPS is enforced for all communications

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details. 