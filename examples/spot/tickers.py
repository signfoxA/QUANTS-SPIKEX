from pyspikex.spot import Spot

spikex = Spot(host="https://sapi.spikex.com", access_key='', secret_key='')
print(spikex.get_tickers(symbol='btc_usdt'))
print(spikex.get_tickers(symbols=['btc_usdt', 'xt_usdt']))
