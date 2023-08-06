#coding:utf-8

import _env
from _route import route
from _base import ViewBase


@route("/")
class index(ViewBase):
    def get(self):
        self.render()
#        self.finish("good good study , day day up")


if __name__ == "__main__":
    pass

 
