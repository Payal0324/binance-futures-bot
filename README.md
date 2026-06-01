# Binance USDT-M Futures Testnet Trading Bot CLI

A production-quality Python 3 Command-Line Interface (CLI) application that allows placing `MARKET`, `LIMIT`, and `STOP_LIMIT` orders on the Binance USDT-M Futures Testnet.

---

## Architecture

The project is structured cleanly to separate concerns, making it modular and easy to extend or unit test:

```
binance_futures_bot/
│
├── bot/
│   ├── __init__.py         # Exposes the main modules
│   ├── client.py           # Core HTTP requests, signing, time synchronization
│   ├── orders.py           # Orchestration layer (validates and routes to client)
│   ├── validators.py       # Input validation logic
│   └── logging_config.py   # Global logging setup
│
├── cli.py                  # Click-based CLI entrypoint
├── requirements.txt        # Third-party dependencies
├── README.md               # Documentation and setup instructions
└── bot.log                 # Generated application log file (contains API requests & responses)
```

---

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher.
- A terminal (Windows Command Prompt, PowerShell, or bash).

### 2. Install Dependencies
Clone or copy this repository to your target directory. Navigate to the root directory and install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Obtain Binance Futures Testnet Keys
1. Navigate to the [Binance Futures Testnet](https://testnet.binancefuture.com) website.
2. Register / log in using your credentials (you can log in via email or standard Binance account).
3. Scroll down to the **API Key** tab under the dashboard.
4. Click **Generate API Key** and secure both your **API Key** and **Secret Key**.

### 4. Configure Environment Variables
You must export the credentials as environment variables before executing the bot.

#### On Windows PowerShell:
```powershell
$env:BINANCE_API_KEY="your_testnet_api_key_here"
$env:BINANCE_API_SECRET="your_testnet_api_secret_here"
```

#### On Windows Command Prompt (cmd):
```cmd
set BINANCE_API_KEY=your_testnet_api_key_here
set BINANCE_API_SECRET=your_testnet_api_secret_here
```

#### On macOS/Linux:
```bash
export BINANCE_API_KEY="your_testnet_api_key_here"
export BINANCE_API_SECRET="your_testnet_api_secret_here"
```

---

## Usage Examples

Execute the bot via the `cli.py` file. Run `--help` to view all option descriptions:

```bash
python cli.py --help
```

### 1. Place a MARKET BUY Order
Places a market order to buy 0.001 BTC on the BTCUSDT futures instrument:
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### 2. Place a LIMIT SELL Order
Places a limit order to sell 0.002 BTC at a price of $100,000:
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 100000.0
```

### 3. Place a STOP_LIMIT BUY Order (Bonus Feature)
Places a stop-limit order to buy 0.001 BTC. It is triggered when the market price touches $95,000, placing a limit order at $95,050:
```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.001 --price 95050.0 --stop-price 95000.0
```

---

## Input Validation

The bot validates parameters locally before dispatching them to the Binance API:
- **Side**: Must be `BUY` or `SELL` (case-insensitive).
- **Type**: Must be `MARKET`, `LIMIT`, or `STOP_LIMIT` (case-insensitive).
- **Quantity**: Must be a number greater than 0.
- **Price**: Required and must be greater than 0 for `LIMIT` and `STOP_LIMIT` orders.
- **Stop Price**: Required and must be greater than 0 for `STOP_LIMIT` orders.

---

## Error Handling & Logging

- All network requests, server responses, client validations, and exceptions are logged with timestamps and logging levels to the local `bot.log` file.
- Outgoing API calls write query parameters, methods, and base URLs.
- Incoming API responses print HTTP status codes and the full response body.
- When errors happen, the program handles them gracefully without collapsing silently:
  - **Validation Errors**: Inform the user about the invalid input and list instructions.
  - **API Errors**: Print the specific error message and code returned directly from the exchange.
  - **Network Errors**: Detect socket timeouts/failures and recommend network diagnostic checks.

---

## Assumptions & Notes
1. **Trading Rules (Step Size & Tick Size)**: The bot verifies that price and quantity inputs are formatted correctly, but does not hardcode tick size or step size limits. Binance Testnet API itself will reject the order with a descriptive code (e.g., `-1111 Precision is over the maximum`) if you violate the exchange's minimum filters.
2. **Time Syncing**: The client automatically requests the exchange server time upon startup and computes the offset against the local machine. This ensures that even if your local PC's clock is slightly out of sync, signature timestamps will not fail the `recvWindow` security check.
