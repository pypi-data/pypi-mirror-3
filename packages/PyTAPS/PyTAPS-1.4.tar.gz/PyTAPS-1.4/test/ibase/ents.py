from itaps import iBase, iMesh
from .. import testhelper as unittest
import numpy

class TestEnts(unittest.TestCase):
    def setUp(self):
        self.mesh = iMesh.Mesh()
        self.ent  = self.mesh.createVtx([0,0,0])
        self.ent2 = self.mesh.getEntities()[0]

        self.mesh.createVtx([[0,0,0]]*10)
        self.ents = self.mesh.getEntities()

    def testDtype(self):
        self.assertEqual(self.ents.dtype,  iBase.Entity)

    def testFromArray(self):
        ents = numpy.array(self.ents)
        self.assertArray(ents, self.ents)
        self.assertEqual(type(ents), numpy.ndarray)
        self.assertEqual(ents.dtype, iBase.Entity)

    def testFromList(self):
        ents = numpy.array(self.ents.tolist())
        self.assertArray(ents, self.ents)
        self.assertEqual(type(ents), numpy.ndarray)
        self.assertEqual(ents.dtype.type, iBase.Entity)

    def testFromScalar(self):
        ents = numpy.array(self.ent)
        self.assertEqual(ents, self.ents[0:1])
        self.assertEqual(type(ents), numpy.ndarray)
        self.assertEqual(ents.dtype.type, iBase.Entity)

    def testEquality(self):
        self.assertTrue (self.ent == self.ent2)
        self.assertFalse(self.ent != self.ent2)

        self.assertArray(self.ents, self.ents)
        self.assertFalse((self.ents[0:2] != self.ents[0:2]).any())

    def testIn(self):
        self.assertTrue(self.ent in self.ents)

    def testGet(self):
        self.assertEqual(self.ents[0], self.ent)

    def testSet(self):
        ents = self.ents.copy()
        ents[1] = self.ent
        self.assertEqual(ents[1], self.ent)

    def testSlice(self):
        self.assertArray(self.ents[:],     self.ents)
        self.assertArray(self.ents[0:2],   [self.ents[0], self.ents[1]])
        self.assertArray(self.ents[0:4:2], [self.ents[0], self.ents[2]])
        self.assertArray(self.ents[1::-1], [self.ents[1], self.ents[0]])

    def testSort(self):
        # TODO: assumes array is sorted to begin with
        for kind in 'quicksort', 'mergesort', 'heapsort':
            rev = self.ents[::-1].copy()
            self.assertArray(numpy.sort(rev, kind=kind), self.ents)

            rev = self.ents[::-1].copy()
            indices = numpy.arange(len(self.ents))[::-1]
            self.assertArray(numpy.argsort(rev, kind=kind), indices)
