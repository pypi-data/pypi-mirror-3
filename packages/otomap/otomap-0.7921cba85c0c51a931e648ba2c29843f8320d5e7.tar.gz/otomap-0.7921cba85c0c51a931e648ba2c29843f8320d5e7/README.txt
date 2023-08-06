Synopsis
========

otomap provides a one-to-one mapping abstraction, presented with a
MutableSet interface of (left, right) entries.  An OTOMap instance also
has left and right facet attributes which both provide MutableMapping
interfaces with complementary directionality.

Examples
--------

>>> from otomap import OTOMap
>>> oto = OTOMap()
>>> oto.add(('foo', 'bar'))
>>> ('foo', 'bar') in oto
True
>>> list(oto)
[('foo', 'bar')]
>>> oto.left['foo']
'bar'
>>> oto.right['bar']
'foo'
>>> oto.left['X'] = 'bar'
>>> list(oto)
[('X', 'bar')]
>>> del oto.right['bar']
>>> oto.left.items()
[]

