#coding:utf-8

import _env

__HASH__ =  {
    "reset.css" : 'uh1ZsOU9OAsSs-l6QoszFA', #reset
    "base.css" : 'Dp5RQzDavqevnsFBrAp8OQ', #base
}


from misc.config import DEBUG, HOST_CSS_JS, HOST_DEV_PREFIX
from os.path import dirname,basename
__vars__ = vars()

for file_name, hash in __HASH__.iteritems():
    
    if DEBUG:
        value = "http://%s%s/%s/%s"%(HOST_DEV_PREFIX, HOST_CSS_JS, basename(dirname(__file__)), file_name)
    else:
        value = "http://%s/%s"%(HOST_CSS_JS, hash) 
    
    name = file_name.rsplit('.', 1)[0].replace('.', '_').replace('-', '_').replace('/', '_')
    
    __vars__[name] = value
                            
