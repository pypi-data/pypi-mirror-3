#!/usr/bin/env python
#coding:utf-8
import pyclbr
from os.path import isdir

def print_route(prefix):
    __import__('%s._install'%prefix)
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

        print '\t%s\t%s%s'%(
            ('%s +%s;'%(mn, mddict[cls_name].lineno)).ljust(42),
            url.ljust(42),
            cls_name
        )

if __name__ == "__main__":
    from misc.boot.app_install import APP_INSTALL 
    for site_domain , i in APP_INSTALL:
        for j in i:
            name = j.__name__
            print '\n%s\n%s/view/_install.py'%(site_domain, name.replace(".","/")) 
            print_route(name)
        
