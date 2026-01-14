#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spikex.com API Order Placement Test Example
Configure API keys using environment variables
"""

import sys
import os
# Add parent directory to path to import pyspikex module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyspikex.spot import Spot

# Read configuration from environment variables
# Setup method:
# export SPIKEX_HOST="https://sapi.ai-exchange-ai.com"
# export SPIKEX_ACCESS_KEY="your_access_key"
# export SPIKEX_SECRET_KEY="your_secret_key"

HOST = os.getenv("SPIKEX_HOST", "https://sapi.spikex.com")
ACCESS_KEY = os.getenv("SPIKEX_ACCESS_KEY", "")
SECRET_KEY = os.getenv("SPIKEX_SECRET_KEY", "")

# Check if API keys are set
if not ACCESS_KEY or not SECRET_KEY:
    print("⚠ Error: API keys not set!")
    print("\nPlease set environment variables:")
    print("  export SPIKEX_HOST='https://sapi.spikex.com'")
    print("  export SPIKEX_ACCESS_KEY='your_access_key'")
    print("  export SPIKEX_SECRET_KEY='your_secret_key'")
    print("\nOr set them directly in the script (not recommended, may leak keys)")
    exit(1)

# Create API client
spikex = Spot(host=HOST, access_key=ACCESS_KEY, secret_key=SECRET_KEY)

# 1. Get account balance
print("=" * 60)
print("1. Get Account Balance")
print("=" * 60)
try:
    balance = spikex.balance("usdt")
    print(f"USDT Balance: {balance}")
except Exception as e:
    print(f"Failed to get balance: {e}")

# 2. Get trading pair information
print("\n" + "=" * 60)
print("2. Get Trading Pair Information")
print("=" * 60)
try:
    symbols = spikex.get_symbol_config()
    print(f"Available trading pairs: {len(symbols)}")
    # Display first 5 trading pairs
    for symbol in symbols[:5]:
        print(f"  - {symbol.get('symbol')}")
except Exception as e:
    print(f"Failed to get trading pairs: {e}")

# 3. Get BTC price
print("\n" + "=" * 60)
print("3. Get BTC Current Price")
print("=" * 60)
try:
    ticker = spikex.get_tickers(symbol='btc_usdt')
    if ticker:
        current_price = float(ticker[0].get('p', 0)) if isinstance(ticker, list) else float(ticker.get('p', 0))
        print(f"BTC/USDT Current Price: {current_price}")
    else:
        print("Unable to get price")
        current_price = 95000
except Exception as e:
    print(f"Failed to get price: {e}")
    current_price = 95000

# 4. Place a limit buy order (price set to 90% of current price)
print("\n" + "=" * 60)
print("4. Order Placement Test")
print("=" * 60)
buy_price = round(current_price * 0.9, 2)
print(f"Trading Pair: btc_usdt")
print(f"Price: {buy_price}")
print(f"Quantity: 0.001")
print(f"Side: BUY")
print(f"Type: LIMIT")

try:
    order_result = spikex.order(
        symbol='btc_usdt',
        price=buy_price,
        quantity=0.001,
        side='BUY',
        type='LIMIT',
        time_in_force='GTC'
    )
    
    print("\n✓ Order placed successfully!")
    print(f"Order ID: {order_result.get('orderId')}")
    print(f"Order Status: {order_result.get('state', 'N/A')}")
    
    # 5. Query order
    print("\n" + "=" * 60)
    print("5. Query Order Details")
    print("=" * 60)
    order_id = order_result.get('orderId')
    if order_id:
        order_info = spikex.get_order(order_id=order_id)
        print(f"Order ID: {order_info.get('orderId')}")
        print(f"Trading Pair: {order_info.get('symbol')}")
        print(f"Price: {order_info.get('price')}")
        print(f"Quantity: {order_info.get('origQty')}")
        print(f"Executed: {order_info.get('executedQty')}")
        print(f"Status: {order_info.get('state')}")
    
except Exception as e:
    print(f"\n✗ Order placement failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test Completed")
print("=" * 60)
