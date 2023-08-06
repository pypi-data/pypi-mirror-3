#coding:utf-8
import _env
from model._db import Kv
from mail import mail_new, mail_id

# 数据库
############################################

UserMail = Kv('UserMail')


def user_mail_new(mail, user_id):
    id = mail_new(mail, user_id)
    UserMail.set(id, user_id)
    return id

def user_id_by_mail(mail):
    _mail_id = mail_id(mail)
    if _mail_id:
        return UserMail.get(_mail_id)

if __name__ == '__main__':
    pass
    user_mail_new("zsp007@gmail.com", 11)    
    print user_id_by_mail('zsp007@gmail.com')



