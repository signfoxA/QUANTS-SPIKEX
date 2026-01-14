import requests
import json
import time
import hashlib
import hmac
import logging
from copy import deepcopy
from typing import List, Dict

logger = logging.getLogger('spikex')

"""
curl --location --request POST 'http://sapi.spikex.com/spot/v4/order' \
--header 'accept: */*' \
--header 'Content-Type: application/json' \
--header 'xt-validate-appkey: 626fa1c2-94bf-4559-a3f2-c62897bc392e' \
--header 'xt-validate-timestamp: 1641446237201' \
--header 'xt-validate-signature: f24b67d42283feb4b405c59146ecfca4a48f64bccc33c05c33bcc73edad6b4db' \
--header 'xt-validate-recvwindow: 5000' \
--header 'xt-validate-algorithms: HmacSHA256' \
--data-raw '{"symbol": "BTC_USDT","clientOrderId": "16559390087220001","side": "BUY","type": "LIMIT","timeInForce": "GTC","bizType": "SPOT","price": 20,"quantity": 0.001}'
"""


class Spot:
    """
    Spikex.com API interface
    
    Exception handling:
        Returns None if no content received
        Raises exception if status code is not 200
    """

    # def __init__(self, host, account=None, user_id=None, account_id=None, access_key=None, secret_key=None):
    def __init__(self, host, user_id=None, access_key=None, secret_key=None):
        self.host = host
        # self.account = account
        self.user_id = user_id
        # self.account_id = account_id
        self.access_key = access_key
        self.secret_key = secret_key
        # self.anonymous = not(account and account_id and access_key and secret_key)
        self.anonymous = not (access_key and secret_key)
        self.timeout = 10  # Default timeout in seconds
        self.headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
        }

    @classmethod
    def underscore_to_camelcase(cls, name):
        parts = name.split('_')
        return parts[0] + ''.join(x.title() for x in parts[1:])

    @classmethod
    def create_sign(cls, url, method, headers=None, secret_key=None, **kwargs):
        path_str = url
        query = kwargs.pop('params', None)
        data = kwargs.pop('data', None) or kwargs.pop('json', None)
        query_str = '' if query is None else '&'.join(
            [f"{key}={json.dumps(query[key]) if type(query[key]) in [dict, list] else query[key]}" for key in
             sorted(query)])  # No endpoint uses both query and body simultaneously
        body_str = json.dumps(data) if data is not None else ''
        y = '#' + '#'.join([i for i in [method, path_str, query_str, body_str] if i])
        x = '&'.join([f"{key}={headers[key]}" for key in sorted(headers)])
        sign = f"{x}{y}"
        # print(sign)
        return hmac.new(secret_key.encode('utf-8'), sign.encode('utf-8'),
                        hashlib.sha256).hexdigest().upper()

    def gen_auth_header(self, url, method, **kwargs):
        headers = {}
        headers['xt-validate-timestamp'] = str(int((time.time() - 30) * 1000))
        headers['xt-validate-appkey'] = self.access_key
        headers['xt-validate-recvwindow'] = '60000'
        headers['xt-validate-algorithms'] = 'HmacSHA256'
        headers['xt-validate-signature'] = self.create_sign(url, method, headers, str(self.secret_key), **kwargs)
        headers_ = deepcopy(self.headers)
        headers_.update(headers)
        return headers

    def auth_req(self, url, method='GET', **params):  # Authenticated endpoint requiring signature
        if self.anonymous:
            raise SpikexCodeError('Spikex.com login credentials not provided correctly')
        headers = self.gen_auth_header(url, method, **params)
        kwargs = {'headers': headers, 'timeout': self.timeout}
        kwargs.update(params)
        resp = None
        res = None
        try:
            # print(params)
            resp = requests.request(method, self.host + url, **kwargs)
            resp.raise_for_status()
            res = resp.json()
        except Exception as e:
            info = f'url:{url} method:{method} params:{params} exception:{e}'
            logger.error(info, exc_info=True)
            raise SpikexHttpError(e, info=info, request={'url': url, 'method': method, 'params': params},
                              response=resp, res=res)
        if res['rc'] != 0:
            if res['mc'] == 'AUTH_103':  # When signature error occurs, log ak, url, headers for verification
                info = f'url:{url} method:{method} params:{params} headers:{json.dumps(headers)}'
                logger.error(info)
                raise SpikexBusinessError(res, info)
            info = f'url:{url} method:{method} params:{params} res:{res}'
            logger.debug(info)
            raise SpikexBusinessError(res, info)
        return res

    def req(self, url, method, **params):  # Public endpoint
        kwargs = {'headers': self.headers, 'timeout': self.timeout}
        kwargs.update(params)
        resp = None
        res = None

        try:
            resp = requests.request(method, self.host + url, **kwargs)
            resp.raise_for_status()
            res = resp.json()
        except Exception as e:
            info = f'url:{url} method:{method} params:{params} exception:{e}'
            logger.error(info, exc_info=True)
            raise SpikexHttpError(e, info=info, response=resp, res=res)
        return resp.json()

    def req_get(self, url, params=None, auth=None):  # Determine if authentication is required based on endpoint name
        auth = auth if auth is not None else '/v4/public' not in url
        if auth:
            return self.auth_req(url, "GET", params=params)
        return self.req(url, "GET", params=params)

    def req_post(self, url, params=None, auth=None):  # POST request, only supports JSON data
        auth = auth if auth is not None else '/v4/public' not in url
        if auth:
            return self.auth_req(url=url, method="POST", json=params)
        return self.req(url=url, method="POST", json=params)

    def req_delete(self, url, params=None, json=None, auth=None):  # DELETE request, only supports JSON data
        auth = auth if auth is not None else '/v4/public' not in url
        if auth:
            return self.auth_req(url, "DELETE", params=params, json=json)
        return self.req(url, "DELETE", params=params, json=json)

    # -----------------------------------Market Data-----------------------------------

    def get_time(self) -> int:
        """
        Get server timestamp
        :return: 1662435658062  # datetime.datetime.fromtimestamp(1662435658062/1000)
        """
        return int(self.req_get("/v4/public/time")['result']['serverTime'])

    def get_symbol_config(self, symbol: str = None, symbols: list = None) -> dict:
        """
        Get trading pair information
        :param symbol: Trading pair name, e.g., btc_usdt
        :param symbols: List of trading pair names
        :return: {}
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        elif symbols:
            params['symbols'] = symbols
        res = self.req_get("/v4/public/symbol", params=params)
        return res['result']['symbols']
        # return {s['symbol']: s for s in res['result']['symbols']}

    def get_depth(self, symbol: str, limit: int = None) -> dict:
        """
        Get order book depth data
        :param symbol: Trading pair symbol
        :param limit: Number of orders, default 50, range 1-500
        :return: {
    "timestamp": 1662445330524,  // Timestamp
    "lastUpdateId": 137333589606963580,  // Last update ID
    "bids": [     // Buy orders ([?][0]=price; [?][1]=quantity)
      [
        "200.0000",   // Price
        "0.996000"    // Quantity
      ],
      [
        "100.0000",
        "0.001000"
      ],
      [
        "20.0000",
        "10.000000"
      ]
    ],
    "asks": []    // Sell orders ([?][0]=price; [?][1]=quantity)
  }
        """
        params = {'symbol': symbol}
        if limit:
            params['limit'] = limit
        res = self.req_get('/v4/public/depth', params)
        return res['result']

    def get_kline(self, symbol: str, interval: str, start_time: int = None, end_time: int = None, limit: int = 100):
        """
        Get kline/candlestick data
        :param symbol: Trading pair symbol
        :param interval: Kline interval: 1m;3m;5m;15m;30m;1h;2h;4h;6h;8h;12h;1d;3d;1w;1M e.g., 1m
        :param start_time: Start timestamp
        :param end_time: End timestamp
        :param limit: Limit number of results, default 100
        :return: [
    {
      "t": 1662601014832,  // Open time
      "o": "30000", // Open price
      "c": "32000",  // Close price
      "h": "35000",  // High price
      "l": "25000",  // Low price
      "q": "512",  // Volume (quantity)
      "v": "15360000"    // Turnover (volume)
    }
  ]
        """
        params = {'symbol': symbol, 'interval': interval}
        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time
        if limit:
            params['limit'] = limit
        res = self.req_get('/v4/public/kline', params)
        return res['result']

    def get_trade_recent(self, symbol, limit: int = None):
        """
        Query recent trade list
        :param symbol: Trading pair symbol
        :param limit: Number of trades, default 200, range 1-1000
        :return:[
    {
      "i": 0,   // Trade ID
      "t": 0,   // Trade time
      "p": "string", // Trade price
      "q": "string",  // Trade quantity
      "v": "string",  // Trade volume
      "b": true   // Direction (buyerMaker)
    }
  ]
        """
        params = {'symbol': symbol}
        if limit:
            params['limit'] = limit
        res = self.req_get('/v4/public/trade/recent', params)
        return res['result']

    def get_trade_history(self, symbol, direction, limit: int = None, from_id: int = None):
        """
        Query historical trade list
        :param symbol: Trading pair symbol
        :param direction: Query direction
        :param limit: Number of trades, default 200, range 1-1000
        :param from_id: Starting trade ID, e.g., 6216559590087220004
        :return:[
    {
      "i": 0,   // Trade ID
      "t": 0,   // Trade time
      "p": "string", // Trade price
      "q": "string",  // Trade quantity
      "v": "string",  // Trade volume
      "b": true   // Direction (buyerMaker)
    }
  ]
        """
        params = {
            'symbol': symbol,
            'direction': direction
        }
        if limit:
            params['limit'] = limit
        if from_id:
            params['fromId'] = from_id
        res = self.req_get('/v4/public/trade/history', params)
        return res['result']

    def get_tickers(self, symbol: str = None, symbols: list = None) -> dict:
        """
        Get ticker price information
        :param symbol: Single trading pair symbol
        :param symbols: List of trading pair symbols
        :return:    [
            {
              "s": "btc_usdt",   // Trading pair (symbol)
              "p": "9000.0000",   // Price
              "t": 1661856036925   // Time
            }
          ]
        {
            <symbol>: {'price': float, }
        }
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        elif symbols:
            params['symbols'] = symbols
        res = self.req_get('/v4/public/ticker/price', params)
        return res['result']

    def get_tickers_book(self, symbol: str = None, symbols: list = None):
        """
        Get best bid/ask ticker
        :param symbol: Single trading pair symbol
        :param symbols: List of trading pair symbols
        :return:  [
    {
      "s": "btc_usdt",  // Trading pair (symbol)
      "ap": null,  // Ask price (best ask)
      "aq": null,  // Ask quantity (best ask)
      "bp": null,   // Bid price (best bid)
      "bq": null    // Bid quantity (best bid)
    }
  ]
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        elif symbols:
            params['symbols'] = symbols
        res = self.req_get('/v4/public/ticker/book', params)
        return res['result']

    def get_tickers_24h(self, symbol: str = None, symbols: list = None):
        """
        Get 24h statistics ticker
        :param symbol: Single trading pair symbol
        :param symbols: List of trading pair symbols
        :return:  [
    {
      "s": "btc_usdt",   // Trading pair (symbol)
      "cv": "0.0000",   // Price change (change value)
      "cr": "0.00",     // Price change percentage (change rate)
      "o": "9000.0000",   // Open price (first trade)
      "l": "9000.0000",   // Low price
      "h": "9000.0000",   // High price
      "c": "9000.0000",   // Close price (last trade)
      "q": "0.0136",      // Volume (quantity)
      "v": "122.9940"    // Turnover (volume)
    }
  ]
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        elif symbols:
            params['symbols'] = symbols
        res = self.req_get('/v4/public/ticker/24h', params)
        return res['result']

    # -----------------------------------Orders-----------------------------------

    def get_order(self, order_id=None, client_order_id=None) -> dict:
        """
        Get single order
        :param order_id: Order ID
        :param client_order_id: Client order ID
        :return: Order information dictionary
        """
        params = {}
        if order_id:
            params['orderId'] = order_id
        elif client_order_id:
            params['clientOrderId'] = client_order_id
        res = self.req_get('/v4/order', params)
        return res['result']

    def order(self, symbol, side, type, biz_type='SPOT', time_in_force='GTC', client_order_id=None, price=None,
              quantity=None, quote_qty=None):
        """
        Place order
        :param symbol: Trading pair (required)
        :param client_order_id: Client order ID (optional, max 32 characters)
        :param side: Order side - BUY or SELL (required)
        :param type: Order type - LIMIT (limit order) or MARKET (market order) (required)
        :param time_in_force: Time in force - GTC, FOK, IOC, GTX (required)
        :param biz_type: Business type - SPOT (spot) or LEVER (leverage) (required)
        :param price: Price. Required for LIMIT orders; not used for MARKET orders
        :param quantity: Quantity. Required for LIMIT orders; required for MARKET orders when ordering by quantity
        :param quote_qty: Quote quantity. Not used for LIMIT orders; required for MARKET orders when ordering by amount
        :return: Order result dictionary
        """
        params = {'symbol': symbol, 'side': side, 'type': type, 'bizType': biz_type,
                  'timeInForce': time_in_force}
        if client_order_id:
            params['clientOrderId'] = client_order_id
        if price:
            params['price'] = price
        if quote_qty:
            params['quoteQty'] = quote_qty
        if quantity:
            if type == "MARKET" and side == "BUY" and quote_qty is None:
                params['quoteQty'] = quantity * price
            else:
                params['quantity'] = quantity
        res = self.req_post("/v4/order", params)
        return res['result']

    def batch_order(self):
        pass

    def cancel_order(self, order_id):
        """
        Cancel single order
        :param order_id: Order ID to cancel
        :return: Cancellation result
        """
        res = self.req_delete(f'/v4/order/{order_id}')
        return res['result']

    def get_open_orders(self, symbol=None, biz_type=None, side=None) -> list:
        """
        Query current open orders
        :param symbol: Trading pair, if not specified, returns all pairs
        :param biz_type: Business type - SPOT, LEVER
        :param side: Order side - BUY, SELL
        :return: List of open orders
        """
        params = {}
        if symbol:
            params["symbol"] = symbol
        if biz_type:
            params["bizType"] = biz_type
        if side:
            params["side"] = side

        res = self.req_get("/v4/open-order", params)
        return res['result']

    def cancel_open_orders(self, symbol=None, biz_type='SPOT', side=None):
        """
        Cancel all open orders
        :param symbol: Trading pair symbol
        :param biz_type: Business type
        :param side: Order side
        :return: Cancellation result
        """
        params = {'bizType': biz_type}
        if symbol:
            params['symbol'] = symbol
        if side:
            params['side'] = side
        res = self.req_delete('/v4/open-order', json=params)
        return res['result']

    def cancel_orders(self, order_ids: list) -> None:
        """
        Cancel multiple orders
        :param order_ids: List of order IDs (must be less than 300)
        :return: Cancellation result
        """
        params = {'orderIds': order_ids}
        res = self.req_delete("/v4/batch-order", json=params)
        return res['result']

    def batch_order(self, data, batch_id=None) -> List[Dict]:
        """
        Place batch orders (maximum 100 per batch)
        :param data: List of order dictionaries [{}]
        :param batch_id: Batch ID
        :return: List of order results
        
        Reference the order() method to construct the data array with dictionaries.
        Parameters: symbol, side, type, biz_type='SPOT', time_in_force='GTC', client_order_id=None, price=None, quantity=None, quote_qty=None
        
        :param data: {
  "clientBatchId": "51232",
  "items": [
    {
      "symbol": "BTC_USDT",
      "clientOrderId": "16559590087220001",
      "side": "BUY",
      "type": "LIMIT",
      "timeInForce": "GTC", # Choose one: GTC, IOC, FOK, GTX
      "bizType": "SPOT",
      "price": 40000,
      "quantity": 2,
      "quoteQty": 80000
    }
  ]
}
        :return: [{'index': 0, 'clientOrderId': 'batch_order1663857797612_1', 'orderId': '143259835441769153', 'rejected': False, 'reason': None}]
        """
        items = []
        for item in data:
            # item_ = {transfer_hump(k): v for k, v in item.items()}
            items.append(item)
        params = {"clientBatchId": batch_id, "items": items}
        res = self.req_post("/v4/batch-order", params)
        return res['result']

    def get_batch_orders(self, order_ids: list) -> list:
        """
        Get batch orders
        :param order_ids: List of order IDs (maximum 150, otherwise GET request may be too large)
        :return: List of order dictionaries, same format as get_order()
        """
        # if
        params = {'orderIds': ','.join(order_ids)}
        res = self.req_get("/v4/batch-order", params)
        return res['result']

    def get_all_orders(self, market: str):
        res = []
        orders_all = self.get_open_orders(market)
        order_ids_all = [i['orderId'] for i in orders_all]
        page = 0
        page_size = 150
        now_order_ids = order_ids_all[page_size * 0: (page + 1) * page_size]
        while now_order_ids:
            item = self.get_batch_orders(now_order_ids)
            res.extend(item)
            page += 1
            now_order_ids = order_ids_all[page_size * page: (page + 1) * page_size]
        return res

    def get_history_orders(self, symbol=None, biz_type=None, side=None, type=None, order_id=None, from_id=None,
                           direction=None, limit=None, start_time=None, end_time=None, hidden_canceled=None):
        """
        Query historical orders
        :param symbol: Trading pair symbol
        :param biz_type: Business type
        :param side: Order side
        :param type: Order type
        :param order_id: Order ID
        :param from_id: Starting order ID
        :param direction: Query direction
        :param limit: Number of results
        :param start_time: Start timestamp
        :param end_time: End timestamp
        :param hidden_canceled: Hide canceled orders
        :return: Historical orders list
        """
        vars = locals()
        params = {self.underscore_to_camelcase(k): v for k, v in vars.items() if k != 'self' and v is not None}

        res = self.req_get('/v4/history-order', params)
        return res['result']

    def get_trade(self, symbol=None, biz_type=None, side=None, type=None, order_id=None, from_id=None, direction=None,
                  limit=None, start_time=None, end_time=None):
        """
        Query trade history (default returns 20 records per query)
        :param symbol: Trading pair symbol
        :param biz_type: Business type
        :param side: Order side
        :param type: Order type
        :param order_id: Order ID
        :param from_id: Starting trade ID
        :param direction: Query direction
        :param limit: Number of results
        :param start_time: Start timestamp
        :param end_time: End timestamp
        :return: {'hasPrev': False, 'hasNext': True, 'items': [
        {'symbol': 'people_usdt', 'tradeId': '139968422023832642', 'orderId': '139968399989795073', 'orderSide': 'BUY',
        'orderType': 'LIMIT', 'bizType': 'SPOT', 'time': 1663073072298, 'price': '1.031929', 'quantity': '100.0000',
        'quoteQty': '103.192900', 'baseCurrency': 'people', 'quoteCurrency': 'usdt', 'fee': '0.2',
        'feeCurrency': 'people', 'takerMaker': 'MAKER'}
        ]}}

        """
        vars = locals()
        params = {self.underscore_to_camelcase(k): v for k, v in vars.items() if k != 'self' and v is not None}
        res = self.req_get('/v4/trade', params)
        return res['result']

    # -----------------------------------Assets-----------------------------------
    def get_currencies(self):
        """
        Get currency information
        :return: List of currency information
        """
        res = self.req_get("/v4/public/currencies")
        return res['result']['currencies']

    def balance(self, currency):
        """
        Get balance for specific currency
        :param currency: Currency name, comma-separated for multiple currencies, e.g., usdt,btc
        :return: Balance information
        """
        params = {'currency': currency}
        res = self.req_get('/v4/balance', params)
        return res['result']

    def balances(self, currencies=None):
        """
        Get balances for multiple currencies
        :param currencies: List of currency names, comma-separated, e.g., usdt,btc
        :return: Balances information
        """
        params = {'currencies': ','.join(currencies)} if currencies else None
        res = self.req_get('/v4/balances', params)
        return res['result']

    def listen_key(self):
        """
        @return:
        """
        res = self.req_post('/v4/ws-token', auth=True)
        return res['result']

    def transfer(self, from_account, to_account, currency, amount):
        """
        Transfer funds between accounts
        
        BizType values:
        SPOT - Spot trading
        LEVER - Leverage trading
        FINANCE - Finance/Staking
        FUTURES_U - Futures (USDT margin)
        FUTURES_C - Futures (Coin margin)

        :param from_account: Source account BizType
        :param to_account: Destination account BizType
        :param currency: Currency name (must be lowercase, e.g., usdt, btc)
        :param amount: Transfer amount
        :return: Transfer result
        """

        params = {
            "bizId": int(time.time() * 1000),
            "from": from_account,
            "to": to_account,
            "currency": currency,
            "amount": amount
        }

        res = self.req_post("/v4/balance/transfer", params, auth=True)
        return res['result']


import json
import requests


class SpikexCodeError(Exception):
    pass


class SpikexHttpError(Exception):
    PARAMS_DIC = {
        'request': 'Request',
        'response': 'Response',
        'res': 'Result',
    }

    def __init__(self, *args, **kwargs):
        """
        HTTP error exception
        
        :param args: Exception arguments
        :param kwargs: Custom fields, typical usage:
        :info: Description
        :request: Request object dictionary {url, method, params}
        :response: Response object requests.response
        :res: Response JSON data
        """
        self.args = args
        self.exception = args[0]
        self.exception_type = type(self.exception)
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._err_data = kwargs
        self.init()

    def init(self):
        """
        Extract common exceptions and set error messages for easier debugging
        :return: None
        """
        import traceback
        self.trace_info = traceback.format_exc()

    @property
    def desc(self):
        return f'Spikex.com service error: {self.exception}'

    @property
    def err_str(self):
        res = []
        for k, v in self._err_data.items():
            try:
                s = self.PARAMS_DIC.get(k, k) + ':'
                if k == 'response' and type(v) is requests.Response:
                    v_ = {'status_code': v.status_code, 'content': str(v.content)}
                else:
                    v_ = v
                s += json.dumps(v_)
                res.append(s)
            except Exception as e:
                # logger.debug(e)
                pass
        return '\n'.join(res)

    def __str__(self):
        return f'Spikex.com API error: {self.info}\nDetails: {self.err_str}\nException: {self.desc}'


SPIKEX_MES_ERRORS = {
    '0': 'Client error',
    'SUCCESS': 'Success',
    'FAILURE': 'Failure',
    'not exist': 'Target does not exist',
    'AUTH_001': 'Missing header xt-validate-appkey',
    'AUTH_002': 'Missing header xt-validate-timestamp',
    'AUTH_003': 'Missing header xt-validate-recvwindow',
    'AUTH_004': 'Invalid header xt-validate-recvwindow',
    'AUTH_005': 'Missing header xt-validate-algorithms',
    'AUTH_006': 'Invalid header xt-validate-algorithms',
    'AUTH_007': 'Missing header xt-validate-signature',
    'AUTH_101': 'ApiKey does not exist',
    'AUTH_102': 'ApiKey not activated',
    'AUTH_103': 'Signature error',
    'AUTH_104': 'Request from non-bound IP',
    'AUTH_105': 'Request expired',
    'AUTH_106': 'ApiKey permission exceeded',
    'ORDER_001': 'Platform rejected order',
    'ORDER_002': 'Insufficient funds',
    'ORDER_003': 'Trading pair suspended',
    'ORDER_004': 'Trading prohibited',
    'ORDER_005': 'Order does not exist',
    'ORDER_F0101': 'Price filter triggered - minimum value',
    'ORDER_F0102': 'Price filter triggered - maximum value',
    'ORDER_F0103': 'Price filter triggered - step value',
    'ORDER_F0201': 'Quantity filter triggered - minimum value',
    'ORDER_F0202': 'Quantity filter triggered - maximum value',
    'ORDER_F0203': 'Quantity filter triggered - step value',
    'ORDER_F0301': 'Amount filter triggered - minimum value',
    'ORDER_F0401': 'Opening protection filter triggered',
    'ORDER_F0501': 'Limit order protection filter triggered',
    'ORDER_F0601': 'Market order protection filter triggered',
    'ORDER_F0701': 'Too many open orders',
    'ORDER_F0801': 'Too many open conditional orders',
}


class SpikexBusinessError(Exception):
    def __init__(self, data, info: str = None):
        self.return_code = data.get('rc', '0')
        self.message_code = data.get('mc', '0')
        self.source = data
        self.info = info

    @property
    def desc(self):
        return SPIKEX_MES_ERRORS.get(self.message_code, f'Unknown error code: {self.message_code}')

    def __str__(self):
        return f"Spikex.com ERROR. RC:{self.return_code} MC: {self.message_code} DESC:{self.desc} INFO: {self.info} SOURCE:{json.dumps(self.source)}"
