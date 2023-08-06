Synopsis
========

concon (CONstrained CONtainers) provides usefully constrained container
subtypes:

* frozenlist
* frozendict
* frozenset - (Note this is a synonym for the builtin frozenset for completeness.)
* appendonlylist
* appendonlydict
* appendonlyset

Examples
--------

>>> import concon
>>> d = concon.appendonlydict()
>>> d['foo'] = 'bar'
>>> d.items()
[('foo', 'bar')]
>>> d['foo'] = 'quz'
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/n/virtualenvs/default/lib/python2.7/site-packages/concon.py", line 102, in setitem_without_overwrite
    raise OverwriteError(key, value, d[key])
concon.OverwriteError: Attempted overwrite of key 'foo' with new value 'quz' overwriting old value 'bar'
>>> l = concon.frozenlist(['a', 'b', 'c'])
>>> l[1]
'b'
>>> l.append(42)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/n/virtualenvs/default/lib/python2.7/site-packages/concon.py", line 37, in blocked_method
    raise cls(self, method.__name__, a, kw)
concon.ConstraintError: Attempt to call ['a', 'b', 'c'].append (42,) {} violates constraint.
>>> l[2] = 42
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/n/virtualenvs/default/lib/python2.7/site-packages/concon.py", line 37, in blocked_method
    raise cls(self, method.__name__, a, kw)
concon.ConstraintError: Attempt to call ['a', 'b', 'c'].__setitem__ (2, 42) {} violates constraint.
