import unittest

from otomap import OTOMap


class FacetTestsMixin (object):
    def test_peer(self):
        sentinel = object()
        self.facet._peer = sentinel
        self.assertIs(sentinel, self.facet.peer)

    def test__setitem__(self):
        self.facet['foo'] = 'bar'
        self.assertEqual({'foo': 'bar'}, self.left)
        self.assertEqual({'bar': 'foo'}, self.right)

    def test__setiem__alter_key(self):
        self.facet['foo'] = 'bar'
        self.facet['foo'] = 'quz'
        self.assertEqual({'foo': 'quz'}, self.left)
        self.assertEqual({'quz': 'foo'}, self.right)

    def test__setiem__alter_value(self):
        self.facet['foo'] = 'bar'
        self.facet['quz'] = 'bar'
        self.assertEqual({'quz': 'bar'}, self.left)
        self.assertEqual({'bar': 'quz'}, self.right)

    def test__delitem__(self):
        self.facet['foo'] = 'bar'
        del self.facet['foo']
        self.assertEqual({}, self.left)
        self.assertEqual({}, self.right)
        
    def test__getitem__(self):
        value = 'bar'
        self.facet['foo'] = value
        actual = self.facet['foo']
        self.assertIs(value, actual)
        
    def test__len__(self):
        self.assertEqual(0, len(self.facet))
        self.facet['foo'] = 'bar'
        self.assertEqual(1, len(self.facet))
        
    def test__iter__(self):
        self.facet['foo'] = 'bar'
        self.assertEqual(['foo'], list(iter(self.facet)))
        self.assertEqual(1, len(self.left))
        self.assertEqual(1, len(self.right))
        
    def test__contains__(self):
        self.facet['foo'] = 'bar'
        self.assertEqual(True, 'foo' in self.facet)
        
    # Test some MutableMapping concrete methods:
    def test_keys_values_and_items(self):
        self.facet['foo'] = 'bar'

        keys = self.facet.keys()
        self.assertEqual(['foo'], keys)
        self.assertEqual(self.left.keys(), keys)
        self.assertEqual(self.right.values(), keys)

        values = self.facet.values()
        self.assertEqual(['bar'], values)
        self.assertEqual(self.left.values(), values)
        self.assertEqual(self.right.keys(), values)

        items = self.facet.items()
        self.assertEqual([('foo', 'bar')], items)
        self.assertEqual(self.left.items(), items)
        
    def test_pop(self):
        self.facet['foo'] = 'bar'
        self.assertEqual('bar', self.facet.pop('foo'))
        self.assertEqual(42, self.facet.pop('foo', 42))
        self.assertRaises(KeyError, self.facet.pop, 'foo')
        self.assertEqual(0, len(self.facet))
        

class FacetTests (unittest.TestCase, FacetTestsMixin):
    def setUp(self):
        self.left = {}
        self.right = {}
        self.facet = OTOMap.Facet(self.left, self.right)


class OTOMapTests (unittest.TestCase, FacetTestsMixin):
    def setUp(self):
        self.oto = OTOMap()

        # For FacetTestsMixin:
        self.facet = self.oto._left
        self.left = self.oto._left._forward
        self.right = self.oto._right._forward

    def test_properties_and_internal_object_graph(self):
        self.assertIs(self.oto.left.peer, self.oto.right)
        self.assertIs(self.oto.right.peer, self.oto.left)
        self.assertIs(self.oto.left._forward, self.oto.right._reverse)
        self.assertIs(self.oto.right._forward, self.oto.left._reverse)
        
    def test_add(self):
        self.oto.add(('foo', 'bar'))
        self.assertEqual({'foo': 'bar'}, self.left)
        self.assertEqual({'bar': 'foo'}, self.right)

    def test_discard(self):
        entry = ('foo', 'bar')
        self.oto.add(entry)
        self.oto.discard(entry)
        self.assertEqual({}, self.left)
        self.assertEqual({}, self.right)

    def test_discard_nonexistent_entry(self):
        entry = ('foo', 'bar')
        self.oto.add(entry)

        self.assertRaises(KeyError, self.oto.discard, ('X', 'Y'))
        self.assertRaises(KeyError, self.oto.discard, ('foo', 'quz'))
        self.assertRaises(KeyError, self.oto.discard, ('quz', 'bar'))

    def test__len__(self):
        self.assertEqual(0, len(self.oto))
        self.oto.add(('foo', 'bar'))
        self.assertEqual(1, len(self.oto))
        self.oto.add(('foo', 'quz'))
        self.assertEqual(1, len(self.oto))
        self.oto.add(('X', 'Y'))
        self.assertEqual(2, len(self.oto))

    def test__iter__(self):
        entry = ('foo', 'bar')
        self.oto.add(entry)

        entries = list(iter(self.oto))
        self.assertEqual([entry], entries)
        self.assertEqual(self.oto.left.items(), entries)

    def test__contains__(self):
        # Make different string object identities which are value-equivalent:
        lkey = 'foo'
        rval = 'bar'
        lkey2 = '!foo!'[1:-1]
        rval2 = 'ba' + 'r'[0]

        assert lkey is not lkey2
        assert rval is not rval2

        self.oto.add( (lkey, rval) )

        self.assertEqual(True, (lkey2, rval2) in self.oto)
        self.assertEqual(False, ('X', 'Y') in self.oto)
        self.assertEqual(False, ('foo', 'quz') in self.oto)
        self.assertEqual(False, ('quz', 'bar') in self.oto)

    def test_invalid_entry(self):
        self.assertRaises(TypeError, self.oto.add, ())
        self.assertRaises(TypeError, self.oto.add, (42,))
        self.assertRaises(TypeError, self.oto.add, (42,7,'too many elements'))
        self.assertRaises(TypeError, self.oto.add, None)


if __name__ == '__main__':
    unittest.main()
