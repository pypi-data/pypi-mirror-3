==================
standardenum
==================

USAGE
-----------------

>>> from standardenum import StandardEnum
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
