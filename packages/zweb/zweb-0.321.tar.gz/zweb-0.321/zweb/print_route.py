#!/usr/bin/env python
#coding:utf-8
import pyclbr
from os.path import isdir
from _import import _import

RESULT = []
def _print_route(site_domain, prefix):
    __import__('%s._site'%prefix)
    mod = __import__(prefix, globals(), locals(), ['_route'], -1)

    prefix = len(prefix) + 1

    for i in sorted(mod._route.route.handlers):
        url, cls = i[:2]
        mn = cls.__module__

        mddict = pyclbr.readmodule(mn)
        cls_name = cls.__name__

        mn = mn.replace('.', '/')
        if isdir(mn):
            mn += '/__init__'
        mn += '.py'

        RESULT.append('\t%s\t%s%s'%(
            ('%s +%s;'%(mn, mddict[cls_name].lineno)).ljust(25),
            ("//%s%s"%(site_domain,url)).ljust(60),
            cls_name
        ))

def print_route(app):
    #app = _import(app)
    from misc import config
    config.DEBUG = False
    components = app.split(".")
    mod = __import__(".".join(components[:-1]), globals(), locals(), [components[-1]], -1) 
    mod = getattr(mod,components[-1])
    for site_domain , i in mod.APP:
        for j in i:
            name = j.__name__
            RESULT.append('\n%s/view/_site.py'%( name.replace(".","/")) )
            _print_route(site_domain, name)
    print "\n".join(RESULT) 

if __name__ == "__main__":
    app = raw_input("choose import app (default site_app) :\n").strip() or "site_app"
    print_route("misc.boot.%s"%app)

