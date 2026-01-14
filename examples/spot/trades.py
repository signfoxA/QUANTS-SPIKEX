from pyspikex.spot import Spot

spikex = Spot(host="https://sapi.spikex.com", access_key='', secret_key='')
print(spikex.get_trade_recent(symbol='btc_usdt'))
print(spikex.get_trade_recent(symbol='btc_usdt', limit=10))
