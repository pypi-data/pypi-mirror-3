#coding:utf-8

import _env
from model._db import Model , ModelMc, redis, redis_key
from gid import gid, CID

# 常量
############################################

REDIS_USER_NAME = redis_key.UserName()


# 接口
############################################

def user_id():
    """返回一个用户的ID , 可用于实现未登录用户的购物车 ; 建议用ajax实现 , 避免爬虫造成数据库冲击"""
    return gid(CID.USER)

def user_new(name):
    id = gid(CID.USER)
    user_name_set(id, name)
    return id

def user_name_set(id, name):
    name = name.replace('@', '＠').replace('(', '[').replace(')', ']')
    redis.hset(REDIS_USER_NAME, id, name)

def user_name(id):
    return redis.hget(REDIS_USER_NAME, id)

def user_name_list(id_list):
    return redis.hmget(REDIS_USER_NAME, id_list)


if __name__ == '__main__':
    pass
    user_id = user_new('张沈鹏')
    for i in user_name_list([user_id]):
        print i
    print user_id
    from gid import cid_by_id, cid_name
    cid = cid_by_id(user_id)
    print cid
    print cid_name(cid)


