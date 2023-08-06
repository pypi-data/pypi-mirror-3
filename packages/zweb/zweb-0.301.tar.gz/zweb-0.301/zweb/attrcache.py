#!/usr/bin/env python
# -*- coding: utf-8 -*-

def attrcache(f):
    name = f.__name__
    @property
    def _attrcache(self):
        if name in self.__dict__:
            return self.__dict__[name]
        result = f(self)
        self.__dict__[name] = result
        return result

    return _attrcache

