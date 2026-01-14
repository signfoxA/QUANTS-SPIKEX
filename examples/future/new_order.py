from pyspikex.perp import Perp

spikex = Perp(host="https://fapi.spikex.com", access_key='', secret_key='')
res = spikex.send_order(symbol='btc_usdt', price=10000, amount=1, order_side='BUY', order_type='LIMIT', position_side='LONG')
print(res)
