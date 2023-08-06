#coding:utf-8
import _env

import yajl
import json

json.dump = yajl.dump
json.dumps = yajl.dumps
json.loads = yajl.loads
json.load = yajl.load


def pre_config(o):

    o.SITE_DOMAIN = '42qu.com'
    o.SITE_NAME   = '42区'
    o.SITE_SLOGO  = "找到给你答案的人"

    o.DEBUG = False
    o.PORT = 42001

    o.MYSQL_HOST = '127.0.0.1'
    o.MYSQL_PORT = '3306'
    o.MYSQL_USER = 'zpage'
    o.MYSQL_PASSWD = '42qudev'
    o.MYSQL_PREFIX = o.MYSQL_USER

    o.MEMCACHED_ADDR = (
        '127.0.0.1:11211',

    )
    o.DISABLE_LOCAL_CACHED = False

    o.REDIS_CONFIG = dict(
#        unix_socket_path = "/tmp/redis.sock"
        host = 'localhost', 
        port = 6379, 
        db   = 0
    )

def post_config(o):
    o.SITE_URL = "//%s"%o.SITE_DOMAIN
    o.SITE_HTTP = "http:%s"%o.SITE_URL


