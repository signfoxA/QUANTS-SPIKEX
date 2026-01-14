# -*- coding:utf-8 -*-
from pyspikex.perp import Perp

spikex = Perp(host="https://fapi.spikex.com", access_key='', secret_key='')
print(spikex.listen_key())
