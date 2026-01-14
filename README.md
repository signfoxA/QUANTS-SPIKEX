# pyspikex
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

Official Python3 API connector for Spikex.com's HTTP and WebSocket APIs.

## Table of Contents

- [About](#about)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Examples](#examples)
- [Supported Markets](#supported-markets)
- [Contact](#contact)

## About

`pyspikex` (Python + Spikex.com) is the official lightweight Python SDK for interacting with Spikex.com's comprehensive trading platform. Spikex.com is a professional cryptocurrency exchange offering advanced trading features including spot trading, perpetual futures, CFD contracts, and AI-powered copy trading.

## Features

### 🚀 **Comprehensive Trading Support**
- **Spot Trading**: Full support for spot market operations including order placement, cancellation, and market data retrieval
- **Perpetual Futures**: Access to perpetual futures trading with leverage support
- **CFD Contracts**: Trade Contracts for Difference (CFD) on various cryptocurrency pairs
- **Market Data**: Real-time and historical market data including order books, tickers, klines, and trade history

### 🤖 **AI Copy Trading**
- Integrated support for AI-powered copy trading features
- Automated trading strategies and signal following
- Portfolio management tools

### 📊 **Real-time Data Streaming**
- WebSocket support for real-time market updates
- User data streaming (orders, trades, balances, positions)
- Incremental order book updates
- Low-latency market data feeds

### 🔒 **Security & Reliability**
- HMAC-SHA256 signature authentication
- Secure API key management
- Comprehensive error handling
- Request rate limiting support

### 💼 **Advanced Trading Features**
- Multiple order types: Limit, Market, IOC, FOK, GTX
- Batch order operations
- Position management
- Leverage adjustment
- Stop-loss and take-profit orders
- Trigger orders and conditional orders

## Installation

`pyspikex` requires Python 3.9.1 or higher. The module can be installed manually or via [PyPI](https://pypi.org/project/pyspikex/) with `pip`:

```bash
pip install pyspikex
```

For the latest development version:

```bash
pip install pyspikex --upgrade
```

## Quick Start

### Spot Trading

```python
from pyspikex.spot import Spot

# Initialize the Spot API client
spikex = Spot(
    host="https://sapi.spikex.com",
    access_key='your_api_key',
    secret_key='your_secret_key'
)

# Get account balance
balance = spikex.balance("usdt")
print(balance)

# Get market ticker
ticker = spikex.get_tickers(symbol='btc_usdt')
print(ticker)

# Place a limit order
order = spikex.order(
    symbol='btc_usdt',
    price=50000,
    quantity=0.001,
    side='BUY',
    type='LIMIT'
)
print(order)
```

### Perpetual Futures Trading

```python
from pyspikex.perp import Perp

# Initialize the Perpetual Futures API client
spikex = Perp(
    host="https://fapi.spikex.com",
    access_key='your_api_key',
    secret_key='your_secret_key'
)

# Get account capital
capital = spikex.get_account_capital()
print(capital)

# Get market depth
depth = spikex.get_depth(symbol='btc_usdt', depth=10)
print(depth)

# Place a limit order with position side
order = spikex.send_order(
    symbol='btc_usdt',
    price=50000,
    amount=1,
    order_side='BUY',
    order_type='LIMIT',
    position_side='LONG'
)
print(order)
```

### WebSocket Streaming

```python
from pyspikex.websocket.spot import SpotWebsocketStreamClient

# Initialize WebSocket client for spot market
def on_message(ws, message):
    print(f"Received: {message}")

client = SpotWebsocketStreamClient(
    stream_url="wss://stream.spikex.com",
    on_message=on_message
)

# Subscribe to ticker updates
client.ticker(symbol='btc_usdt', action='subscribe')
```

## API Documentation

### Spot API

The Spot API provides access to spot trading functionality:

- **Market Data**: `get_time()`, `get_symbol_config()`, `get_depth()`, `get_kline()`, `get_tickers()`, `get_trade_recent()`, `get_trade_history()`
- **Trading**: `order()`, `batch_order()`, `cancel_order()`, `cancel_open_orders()`, `get_order()`, `get_open_orders()`, `get_history_orders()`
- **Account**: `balance()`, `balances()`, `transfer()`, `listen_key()`

### Perpetual Futures API

The Perpetual Futures API provides access to futures trading:

- **Market Data**: `get_market_config()`, `get_depth()`, `get_k_line()`, `get_book_ticker()`, `get_funding_rate()`, `get_mark_price()`
- **Trading**: `send_order()`, `send_batch_order()`, `cancel_order()`, `cancel_all_order()`, `get_order_id()`, `get_history_order()`
- **Account**: `get_account_capital()`, `get_position()`, `set_account_leverage()`
- **Advanced Orders**: `send_trigger_order()`, `send_stop_profit_or_loss_order()`, `modify_stop_profit_or_loss_order()`

### WebSocket API

Real-time data streaming via WebSocket:

- **Spot Streams**: Trade, Kline, Depth, Ticker, User Balance, User Order, User Trade
- **Futures Streams**: Trade, Kline, Depth, Ticker, Mark Price, Index Price, Funding Rate, User Balance, User Position, User Order, User Trade

## Examples

Comprehensive examples are available in the `/examples` directory:

- **Spot Trading Examples**: Order placement, market data retrieval, account management
- **Futures Trading Examples**: Position management, leverage adjustment, advanced orders
- **WebSocket Examples**: Real-time data streaming for both spot and futures markets

For detailed usage examples, see:
- [Spot Trading Guide](examples/spot_guide.ipynb)
- [Futures Trading Guide](examples/future_guide.ipynb)

## Supported Markets

Spikex.com supports trading across multiple markets:

- **Spot Markets**: Trade cryptocurrencies directly with fiat and stablecoins
- **Perpetual Futures**: Trade perpetual contracts with up to 125x leverage
- **CFD Contracts**: Trade Contracts for Difference on major cryptocurrency pairs
- **AI Copy Trading**: Follow and copy successful trading strategies automatically

## Contact

For API support, documentation, and community discussions:

- **Website**: [https://www.spikex.com](https://www.spikex.com)
- **API Documentation**: [https://www.spikex.com/en/api-docs](https://www.spikex.com/en/api-docs)
- **Support**: Contact Spikex.com support team through the official website

---

**Note**: This SDK is maintained by the Spikex.com development team. For the latest updates and bug reports, please refer to the official Spikex.com documentation and support channels.
