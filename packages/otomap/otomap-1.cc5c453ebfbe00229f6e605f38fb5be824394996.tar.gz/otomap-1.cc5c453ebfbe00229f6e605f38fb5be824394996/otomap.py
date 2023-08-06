"""
One-to-One Mapping
"""

from collections import MutableMapping, MutableSet


class OTOMap (MutableSet):
    def __init__(self, entries=[]):
        left = {}
        right = {}

        self._left = self.Facet(left, right)
        self._right = self.Facet(right, left)

        # Set up peer cross references:
        self._left._peer = self._right
        self._right._peer = self._left

        for entry in entries:
            self.add(entry)

    @property
    def left(self):
        return self._left
    
    @property
    def right(self):
        return self._right

    # MutableSet methods:
    def add(self, entry):
        """Note: Unlike normal sets, this can mutate an existing entry when key already points to a different value."""
        (lkey, lval) = self._unwrap_entry(entry)
        self.left[lkey] = lval

    def discard(self, entry):
        if entry not in self:
            raise KeyError(entry)

        (lkey, _) = self._unwrap_entry(entry)
        del self.left[lkey]

    # Set methods:
    # none

    # Sized methods:
    def __len__(self):
        return len(self.left)

    # Iterable methods:
    def __iter__(self):
        return self.left.iteritems()

    # Container methods:
    def __contains__(self, entry):
        (lkey, rval) = self._unwrap_entry(entry)
        try:
            v = self.left[lkey]
        except KeyError:
            return False
        return v == rval
        

    # Private methods:
    def _unwrap_entry(self, entry):
        try:
            (left, right) = entry
        except ValueError:
            raise TypeError('Entries must be (leftValue, rightValue) tuples, not %r' % (entry,))
        return entry


    # Associated classes:
    class Facet (MutableMapping):
        """Present a dict interface with a directionality for the OTOMap."""

        def __init__(self, forward, reverse):
            self._forward = forward
            self._reverse = reverse
            self._peer = None # Privately set in OTOMap __init__

        @property
        def peer(self):
            """Get the peered Facet with the reverse directionality."""
            return self._peer

        # MutableMapping methods:
        def __setitem__(self, key, value):
            sentinel = object()
            oldValue = self._forward.pop(key, sentinel)
            if oldValue is not sentinel:
                del self._reverse[oldValue]
            oldKey = self._reverse.pop(value, sentinel)
            if oldKey is not sentinel:
                del self._forward[oldKey]

            self._forward[key] = value
            self._reverse[value] = key

        def __delitem__(self, key):
            value = self._forward.pop(key)
            del self._reverse[value]

        # Mapping methods:
        def __getitem__(self, key):
            return self._forward[key]

        # Sized methods:
        def __len__(self):
            return len(self._forward)

        # Iterable methods:
        def __iter__(self):
            return iter(self._forward)

        # Container methods:
        def __contains__(self, key):
            return key in self._forward
