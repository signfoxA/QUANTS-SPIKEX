# -*- coding:utf-8 -*-
from pyspikex.spot import Spot

spikex = Spot(host="https://sapi.spikex.com", access_key='', secret_key='')
print(spikex.listen_key())
