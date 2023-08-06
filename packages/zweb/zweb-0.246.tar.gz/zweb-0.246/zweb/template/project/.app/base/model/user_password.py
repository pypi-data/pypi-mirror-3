#coding:utf-8

import _env
from model._db import Model , ModelMc, redis, redis_key, Kv
from hashlib import sha256
from gid import gid, CID
from binascii import hexlify

# 常量
############################################


# 数据库
############################################

UserPassword = Kv('UserPassword')


# 接口
############################################


def user_password_verify(user_id, password):
    password = password.strip()
    p = UserPassword.get(user_id)
    if not p and password:
        user_password_new(user_id, password)
        return True
    if p == _hash_password(user_id, password):
        return True
    return False

def user_password_new(user_id, password):
    password = password.strip()
    if password:
        password = _hash_password(user_id, password)
        UserPassword.set(user_id, password)
        


# 内部函数
############################################

def _hash_password(id, password):
    return sha256('%s%s'%(password, id)).digest()


if __name__ == '__main__':
    pass

