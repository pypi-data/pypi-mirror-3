from itaps.helpers import *
from .. import testhelper as unittest
import numpy
import sys

if sys.hexversion >= 0x020600f0:
    from collections import namedtuple
    point = namedtuple('point', 'x y')
else:
    point = lambda *args: args

class TestOffsetList(unittest.TestCase):
    def setUp(self):
        self.single = OffsetList(numpy.arange(0, 13, 3),
                                 numpy.arange(12))
        self.multi  = OffsetList(numpy.arange(0, 13, 3),
                                 point(numpy.arange(12),
                                       numpy.arange(12, 24)))

    def testSingleBasic(self):
        self.assertEqual(len(self.single), 4)
        self.assertArray(self.single[0], [0, 1, 2])
        self.assertArray(self.single.offsets, numpy.arange(0, 13, 3))
        self.assertArray(self.single.data, numpy.arange(12))

    def testSingleIndex(self):
        for i, hunk in enumerate(self.single):
            self.assertEqual(len(hunk), 3)
            self.assertEqual(self.single.length(i), 3)
            self.assertArray(hunk, numpy.arange(i*3, (i+1)*3))

        self.assertRaises(IndexError, lambda: self.single[4])
        self.assertRaises(IndexError, lambda: self.single[0,3])

    def testMultiBasic(self):
        self.assertEqual(len(self.multi), 4)
        self.assertArray(self.multi[0][0], [ 0,  1,  2])
        self.assertArray(self.multi[0][1], [12, 13, 14])
        self.assertArray(self.multi.data[0], numpy.arange(12))
        self.assertArray(self.multi.data[1], numpy.arange(12,24))

    def testMultiIndex(self):
        for i, hunk in enumerate(self.multi):
            self.assertEqual(len(hunk), 2)
            self.assertEqual(len(hunk[0]), 3)
            self.assertEqual(self.multi.length(i), 3)
            self.assertArray(hunk[0], numpy.arange(i*3,    (i+1)*3)   )
            self.assertArray(hunk[1], numpy.arange(i*3+12, (i+1)*3+12))

        self.assertRaises(IndexError, lambda: self.multi[4])
        self.assertRaises(IndexError, lambda: self.multi[0,3])

    def testMultiKey(self):
        for i, hunk in enumerate(self.multi.slice(0)):
            self.assertArray(hunk, numpy.arange(i*3, (i+1)*3))
        for i, hunk in enumerate(self.multi.slice(1)):
            self.assertArray(hunk, numpy.arange(i*3+12, (i+1)*3+12))

        self.assertRaises(AttributeError, lambda: self.multi.non_existant)

    if sys.hexversion >= 0x020600f0:
        def testMultiKeyNamed(self):
            self.assertEqual(self.multi.fields, ('x', 'y'))
            self.assertArray(self.multi.x.data, self.multi.slice('x').data)
            self.assertArray(self.multi.x.data, self.multi.slice(0).data)
