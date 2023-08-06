#coding:utf-8

import _env

__HASH__ =  {
    "init.js" : 'jH94fCHTEZo9CTCB6x8BrQ', #init
    "base.js" : '4cBtha57iwMr70fkLkwI-Q', #base
    "lib/jquery.js" : 'r2k_mup9rjb7O-9Mm25W-w', #lib_jquery
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
                            
