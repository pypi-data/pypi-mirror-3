#coding:utf-8

import _env
from model._db import Kv
from os import urandom
from struct import pack, unpack
from base64 import urlsafe_b64encode, urlsafe_b64decode
import binascii

# 常量
############################################
Session = Kv('Session')

#CREATE TABLE  `zpage_base`.`Session` (
#  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
#  `value` binary(12) DEFAULT NULL,
#  PRIMARY KEY (`id`)
#) ENGINE=MyISAM DEFAULT CHARSET=utf8;

# 接口
############################################
def session_new(user_id):
    s = urandom(12)
    Session.set(user_id, s)
    return _id_binary_encode(user_id, s)

def id_by_session(session):
    user_id, binary = _id_binary_decode(session)
    if user_id and binary == Session.get(user_id):
        return user_id 

def session_delete(user_id):
    Session.set(user_id, None)


# 内部函数
############################################

def _id_by_base64(string):
    try:
        user_id = urlsafe_b64decode(string+'==')
    except (binascii.Error, TypeError):
        return 0
    else:
        return unpack('Q', user_id)[0]

def _id_binary_decode(session):
    if not session:
        return None, None
    user_id = session[:11]
    value = session[11:]
    try:
        value = urlsafe_b64decode(value+'=')
    except (binascii.Error, TypeError):
        return None, None
    user_id = _id_by_base64(user_id)
    return user_id, value

def _id_binary_encode(user_id, session):
    user_id_key = pack('q', int(user_id))
    user_id_key = urlsafe_b64encode(user_id_key).rstrip("=")
    ck_key = urlsafe_b64encode(session)
    return '%s%s'%(user_id_key, ck_key)


if __name__ == '__main__':
    a = session_new(1)
    print id_by_session(a)
    session_delete(1) 
    print id_by_session(a) 


