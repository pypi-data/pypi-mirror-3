from itaps import iBase, iMesh
from .. import testhelper as unittest
import numpy

class TestTags(unittest.TestCase):
    def setUp(self):
        self.mesh = iMesh.Mesh()

        self.tag  = self.mesh.createTag("foo", 1, 'i')
        self.tag2 = self.mesh.getTagHandle("foo")

        self.tag[self.mesh.rootSet] = 1
        for name in "bar", "baz", "quux":
            tmp = self.mesh.createTag(name, 1, 'i')
            tmp[self.mesh.rootSet] = 1
        self.tags = self.mesh.getAllTags(self.mesh.rootSet)

        self.btag  = iBase.Tag(self.tag)
        self.btag2 = iBase.Tag(self.tag2)
        self.btags = numpy.asarray(self.tags)

    def testDtype(self):
        self.assertEqual(self.tags.dtype,  iBase.Tag)
        self.assertEqual(self.btags.dtype, iBase.Tag)

    def testFromArray(self):
        tags = iBase.Array(self.tags)
        self.assertArray(tags, self.tags)
        self.assertEqual(type(tags), iBase.Array)
        self.assertEqual(tags.instance, self.mesh)
        self.assertEqual(tags.dtype, iBase.Tag)

        tags = iBase.Array(self.btags, instance=self.mesh)
        self.assertArray(tags, self.tags)
        self.assertEqual(type(tags), iBase.Array)
        self.assertEqual(tags.instance, self.mesh)
        self.assertEqual(tags.dtype, iBase.Tag)

    def testFromList(self):
        tags = iBase.Array(self.tags.tolist())
        self.assertArray(tags, self.tags)
        self.assertEqual(type(tags), iBase.Array)
        self.assertEqual(tags.instance, self.mesh)
        self.assertEqual(tags.dtype.type, iBase.Tag)

        tags = iBase.Array(self.btags.tolist(), instance=self.mesh)
        self.assertArray(tags, self.tags)
        self.assertEqual(type(tags), iBase.Array)
        self.assertEqual(tags.instance, self.mesh)
        self.assertEqual(tags.dtype.type, iBase.Tag)

    def testFromScalar(self):
        tags = iBase.Array(self.tag)
        self.assertEqual(tags, self.tags[0:1])
        self.assertEqual(type(tags), iBase.Array)
        self.assertEqual(tags.instance, self.mesh)
        self.assertEqual(tags.dtype.type, iBase.Tag)

        tags = iBase.Array(self.btag, instance=self.mesh)
        self.assertEqual(tags, self.tags[0:1])
        self.assertEqual(type(tags), iBase.Array)
        self.assertEqual(tags.instance, self.mesh)
        self.assertEqual(tags.dtype.type, iBase.Tag)

    def testEquality(self):
        self.assertEqual(self.tag,  self.tag2)
        self.assertEqual(self.tag,  self.btag2)
        self.assertEqual(self.btag, self.tag2)
        self.assertEqual(self.btag, self.btag2)

        self.assertFalse(self.tag  != self.tag2)
        self.assertFalse(self.tag  != self.btag2)
        self.assertFalse(self.btag != self.tag2)
        self.assertFalse(self.btag != self.btag2)

        self.assertArray(self.tags,  self.tags)
        self.assertArray(self.tags,  self.btags)
        self.assertArray(self.btags, self.tags)
        self.assertArray(self.btags, self.btags)

        self.assertFalse((self.tags[0:2] != self.tags[0:2]).any())
        self.assertFalse((self.tags[0:2] != self.btags[0:2]).any())
        self.assertFalse((self.btags[0:2] != self.tags[0:2]).any())

    def testIn(self):
        self.assertTrue(self.tag  in self.tags)
        self.assertTrue(self.btag in self.tags)
        self.assertTrue(self.tag  in self.btags)
        self.assertTrue(self.btag in self.btags)

    def testGet(self):
        self.assertEqual(self.tags[0], self.tag)
        self.assertEqual(self.tags[0].instance, self.mesh)
        self.assertEqual(self.btags[0], self.btag)

    def testSet(self):
        tags = self.tags.copy()
        tags[1] = self.tag
        self.assertEqual(tags[1], self.tag)
        self.assertEqual(tags[1].instance, self.mesh)

        btags = self.btags.copy()
        btags[1] = self.btag
        self.assertEqual(btags[1], self.btag)

    def testSlice(self):
        self.assertArray(self.tags[:],     self.tags)
        self.assertArray(self.tags[0:2],   [self.tags[0], self.tags[1]])
        self.assertArray(self.tags[0:4:2], [self.tags[0], self.tags[2]])
        self.assertArray(self.tags[1::-1], [self.tags[1], self.tags[0]])

        self.assertArray(self.btags[:],     self.btags)
        self.assertArray(self.btags[0:2],   [self.btags[0], self.btags[1]])
        self.assertArray(self.btags[0:4:2], [self.btags[0], self.btags[2]])
        self.assertArray(self.btags[1::-1], [self.btags[1], self.btags[0]])

    def testSort(self):
        # TODO: assumes array is sorted to begin with
        for arr in self.tags, self.btags:
            for kind in 'quicksort', 'mergesort', 'heapsort':
                rev = arr[::-1].copy()
                self.assertArray(numpy.sort(rev, kind=kind), arr)

                rev = arr[::-1].copy()
                indices = numpy.arange(len(arr))[::-1]
                self.assertArray(numpy.argsort(rev, kind=kind), indices)
