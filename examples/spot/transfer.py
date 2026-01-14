# -*- coding:utf-8 -*-

from pyspikex.spot import Spot

spikex = Spot(host="https://sapi.spikex.com", access_key='', secret_key='')
print(spikex.transfer(from_account="SPOT", to_account="FUTURES_U", currency="usdt", amount=10))
