from pyspikex.spot import Spot

spikex = Spot(host="https://sapi.spikex.com", access_key='', secret_key='')
res = spikex.order(symbol='btc_usdt', price=10000, quantity=0.001, side='BUY', type='LIMIT')
print(res)
