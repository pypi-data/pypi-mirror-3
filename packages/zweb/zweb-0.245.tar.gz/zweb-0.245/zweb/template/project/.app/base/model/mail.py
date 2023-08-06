#coding:utf-8

import _env
from model._db import Model , ModelMc, redis, redis_key, Kv
from gid import gid, CID

# 常量
############################################

#REDIS_USER_NAME = redis_key.UserName()


# 数据库
############################################

Mail = Kv('Mail')

def mail_new(mail, user_id):
    mail = mail.strip().lower()
    id = gid(CID.MAIL, user_id)
    Mail.set(id, mail)
    return id

def mail_id(mail):
    mail = mail.strip().lower()
    return Mail.id_by_value(mail) 

# 接口
############################################



# 内部函数
############################################



if __name__ == '__main__':
    pass



