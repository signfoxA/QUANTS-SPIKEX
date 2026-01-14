from pyspikex.spot import Spot

spikex = Spot(host="https://sapi.spikex.com", access_key='', secret_key='')
print(spikex.get_kline(symbol='btc_usdt', interval="1m"))
print(spikex.get_kline(symbol='btc_usdt', interval="1h", limit=10))