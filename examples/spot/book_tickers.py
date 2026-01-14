from pyspikex.spot import Spot

spikex = Spot(host="https://sapi.spikex.com", access_key='', secret_key='')
print(spikex.get_tickers_book(symbol='btc_usdt'))
print(spikex.get_tickers_book(symbols=['btc_usdt', 'xt_usdt']))
