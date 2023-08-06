#coding:utf-8

class Signal(object):
    def __init__(self):
        self.receiver = []

    def send(self, *args):
        for func in self.receiver:
            func(*args) 

    def __call__(self, func):
        self.receiver.append(func)
        return func

class _(object):
    def __getattr__(self, name):
        d = self.__dict__
        if name not in d:
            d[name] = Signal()
        return d[name]
        

SIGNAL = _()

if __name__ == "__main__":


    @SIGNAL.follow_new
    def follow_new(a,b):
        print a,b 
    
    SIGNAL.follow_new.send(1 , 3)

