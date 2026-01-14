from pyspikex.perp import Perp

spikex = Perp(host="https://fapi.spikex.com", access_key='', secret_key='')
print(spikex.get_k_line(symbol='btc_usdt', interval="1m"))
