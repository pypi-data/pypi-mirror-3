#
# -*- coding:utf-8 -*-
"""
>>> class SampleEnum(StandardEnum):
...     A = 1
...     B = 2
...     C = 3
...
>>> SampleEnum.A
<SampleEnum.A value=1>
>>> for e in SampleEnum:
...     print e
...
<SampleEnum.A value=1>
<SampleEnum.B value=2>
<SampleEnum.C value=3>
>>> SampleEnum.A == SampleEnum.A
True
>>> SampleEnum.A == SampleEnum.B
False
"""


class EnumType(type):

    def __init__(cls, name, bases, dct):
        super(EnumType, cls).__init__(name, bases, dct)
        cls._values = []

        for key, value in dct.items():
            if not key.startswith('_'):
                v = cls(key, value)
                setattr(cls, key, v)
                cls._values.append(v)

    def __iter__(cls):
        return iter(cls._values)



def StandardEnum__init__(self, k, v):
    self.v = v
    self.k = k

def StandardEnum__repr__(self):
    return "<%s.%s value=%s>" % (self.__class__.__name__, self.k, self.v)

def StandardEnum__str__(self):
    return str(self.v)

def StandardEnum__int__(self):
    return int(self.v)

def StandardEnum__long__(self):
    return long(self.v)

def StandardEnum__float__(self):
    return float(self.v)

def StandardEnum__complex__(self):
    return complex(self.v)

StandardEnum = EnumType(
    "StandardEnum",
    (object,),
    dict(
        __init__=StandardEnum__init__,
        __repr__=StandardEnum__repr__,
        __str__=StandardEnum__str__,
        __int__=StandardEnum__int__,
        __long__=StandardEnum__long__,
        __float__=StandardEnum__float__,
        __complex__=StandardEnum__complex__,
    ),    
)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
