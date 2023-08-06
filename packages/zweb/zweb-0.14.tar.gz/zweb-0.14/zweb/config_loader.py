#coding:utf-8

from zweb.lib.jsdict import JsDict
from os.path import dirname
import sys
from _import import _import

def load(self, *args):
    self = JsDict(self)

    prepare_list = [ ]
    finish_list = [ ]

    sys.path.insert(0, dirname(self.__file__))

    def load(name):
        
        try:
            mod = _import(name)
        except ImportError:
            return

        prepare = getattr(mod, 'pre_config', None)
        if prepare:
            prepare_list.append(prepare)

        finish = getattr(mod, 'post_config', None)
        if finish:
            finish_list.append(finish)

    for i in args:
        load(i)

    funclist = prepare_list+list(reversed(finish_list))
    for _ in funclist:
        _(self)

    sys.path.pop(0)

    return self



