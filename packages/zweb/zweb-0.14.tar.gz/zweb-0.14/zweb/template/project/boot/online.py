#coding:utf-8
import _env
import config

from zweb.server.server_tornado_wsgi import Run
#from zweb.server_tornado import Run

from application import application

run = Run(config.PORT, application)

if __name__ == "__main__":
    run()


