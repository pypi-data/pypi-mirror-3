import sys
if sys.hexversion >= 0x020600f0:
    from collections import namedtuple


def OffsetList(offsets, data):
    if isinstance(data, tuple):
        return OffsetListTuple(offsets, data)
    else:
        return OffsetListSingle(offsets, data)

class OffsetListSingle(object):
    def __init__(self, offsets, data):
        self.offsets = offsets
        self.data = data

    def _mapify(self, i):
        return self.data[i]

    def __getitem__(self, key):
        if isinstance(key, tuple):
            if len(key) != 2:
                raise ValueError
            if key[1] < 0 or key[1] >= self.length(key[0]):
                raise IndexError
            return self._mapify(self.offsets[key[0]] + key[1])
        else:
            return self._mapify(slice(self.offsets[key], self.offsets[key+1]))

    def __iter__(self):
        return (self[i] for i in xrange(len(self)))

    def length(self, i = None):
        if i == None:
            return len(self.offsets)-1
        else:
            return self.offsets[i+1] - self.offsets[i]

    def __len__(self):
        return self.length()


class OffsetListTuple(OffsetListSingle):
    if sys.hexversion >= 0x020600f0:
        def _mapify(self, i):
            return self.data.__class__._make([ val[i] for val in self.data ])

        def __getattr__(self, key):
            return OffsetListSingle(self.offsets, getattr(self.data, key))

        fields = property(lambda self: self.data._fields)

        def slice(self, key):
            if isinstance(key, str):
                return OffsetListSingle(self.offsets, getattr(self.data, key))
            else:
                return OffsetListSingle(self.offsets, self.data[key])
    else:
        def _mapify(self, i):
            return tuple([ val[i] for val in self.data ])

        def slice(self, key):
            return OffsetListSingle(self.offsets, self.data[key])

class IndexedList(object):
    def __init__(self, offsets, indices, data):
        self.indices = OffsetListSingle(offsets, indices)
        self.data = data

    def __getitem__(self, key):
        return self.data[ self.indices[key] ]

    def length(self, i = None):
        return self.indices.length(i)

    def __len__(self):
        return len(self.indices)
