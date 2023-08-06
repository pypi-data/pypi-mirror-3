class Proxy(object):
    def __init__(self, **kwargs):
        for (k, v) in kwargs.items():
            setattr(self, k, v)

class Head(Proxy):
    pass
class Commit(Proxy):
    pass
class Tree(Proxy):
    pass
class Blob(Proxy):
    pass

