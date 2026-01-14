from pyspikex.perp import Perp

spikex = Perp(host="https://fapi.spikex.com", access_key='', secret_key='')
print(spikex.get_market_config(symbol='btc_usdt'))
