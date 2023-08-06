
# coding:utf-8

import _env
from misc import config
import os

p1 = _env.PREFIX +'/js/_build/'
p2 = _env.PREFIX+ '/css/_build/'

for i in os.listdir(p1):
    os.remove(p1 + i)

for i in os.listdir(p2):
    os.remove(p2 + i)


