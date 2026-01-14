from pyspikex.perp import Perp

spikex = Perp(host="https://fapi.spikex.com", access_key='', secret_key='')
res = spikex.cancel_order(order_id=12345678)
print(res)
