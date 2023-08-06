#coding:utf-8

import _env
from model._db import Model , ModelMc, redis, redis_key
from time import time

# 接口
############################################

def gid(cid, user_id=0):
    id = redis.incr(REDIS_GID)
    Gid.execute(
        'insert delayed into Gid(id, cid, user_id, time) values (%s,%s,%s,%s)',
        (
            id, cid, user_id, int(time())
        )
    )
    redis.hincrby(REDIS_GID_COUNT, cid, 1)
    return id


def gid_count(cid=0):
    if cid:
        return redis.hgetall(REDIS_GID_COUNT)
    else:
        return redis.hget(REDIS_GID_COUNT, cid)


def cid_by_id(id):
    cursor = Gid.execute('select cid from Gid where id=%s', id)
    r = cursor.fetchone()
    return r[0]


_CID_NAME = {}

def cid_name(cid):
    cid = int(cid)
    if cid in _CID_NAME:
        return _CID_NAME[cid]
    name = redis.hget(REDIS_CID_NAME, cid)

    if name:
        _CID_NAME[cid] = name
        return name

class Cid(object):
    def __getattr__(self, name):
        cid = redis.hget(REDIS_CID, name)
        if cid:
            self.__dict__[name] = cid
            return cid
        else:
            query = raw_input("cid %s not exist , create ? enter 'yes' to create\n"%name)
            if query.strip() == 'yes':
                return _cid_new(name)
            else:
                raise Exception('cid not exist : %s'%name)



CID = Cid()



# 常量
############################################

REDIS_CID_ID = redis_key.CidId()
REDIS_CID = redis_key.Cid()
REDIS_CID_NAME = redis_key.CidName()
REDIS_GID = redis_key.Gid()
REDIS_GID_COUNT = redis_key.GidCount()


# 表结构
############################################
class Gid(Model):
    """
    CREATE TABLE `zpage_base`.`zpage` (
      `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      `cid` INTEGER UNSIGNED NOT NULL,
      `user_id` BIGINT UNSIGNED NOT NULL,
      `time` BIGINT UNSIGNED NOT NULL,
      PRIMARY KEY (`id`),
      INDEX `user_id`(`user_id`)
    )
    ENGINE = MyISAM;
    """
    pass

# 内部函数
############################################
def _cid_new(name):
    if redis.hget(REDIS_CID, name):
        raise Exception('CID EXIST : %s'%name)
    id = redis.incr(REDIS_CID_ID)
    p = redis.pipeline()
    p.hset(REDIS_CID, name, id)
    p.hset(REDIS_CID_NAME, id, name)
    p.execute()
    return id



if __name__ == '__main__':
    pass

