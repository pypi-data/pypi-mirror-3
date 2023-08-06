#coding:utf-8
import _env


def pre_config(o):

    o.SITE_DOMAIN = 'z32e1.tk'
    o.SITE_NAME   = '42区'
    o.SITE_SLOGO  = "找到给你答案的人"

    #线上用的域名 , 静态文件会设置永久缓存 (其他域名默认生成的nginx配置文件会禁用缓存)
    o.ONLINE_DOMAIN = (
        #"42qu.com"
    ) 

    o.DEBUG = False
    o.PORT = 42001
    o.PROCESS_NUM = 4
    

    o.MYSQL_HOST = '127.0.0.1'
    o.MYSQL_PORT = '3306'
    o.MYSQL_USER = 'zweb'
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

    # 注意：备份路径只为数据备份准备，而不是表备份
    o.BACKUP_PATH = '/mnt/backup/%s'%o.SITE_DOMAIN

    # css js 静态文件的域名
    o.FS_DOMAIN = 's.%s'%o.SITE_DOMAIN
    o.FS_URL =  'http://%s'%o.FS_DOMAIN

