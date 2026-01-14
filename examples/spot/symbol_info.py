from pyspikex.spot import Spot

spikex = Spot(host="https://sapi.spikex.com", access_key='', secret_key='')
print(spikex.get_symbol_config(symbol='btc_usdt'))
