from pyspikex.spot import Spot

spikex = Spot(host="https://sapi.spikex.com", access_key='', secret_key='')
res = spikex.cancel_order(order_id=12345678)
print(res)
