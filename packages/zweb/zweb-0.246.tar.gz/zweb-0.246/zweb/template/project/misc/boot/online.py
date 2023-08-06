#coding:utf-8
import _env
from misc import config

from zweb.server.server_tornado_wsgi import Run
#from zweb.server_tornado import Run

from application import application

from zweb.config_loader import CONFIG_LOADED
for i in CONFIG_LOADED:
    print "loaded config : \n\t%s.py"%i.__file__.rsplit(".",1)[0][len(_env.PREFIX)+1:]

run = Run(config.PORT, application)

if __name__ == "__main__":
    run()


