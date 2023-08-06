from itaps import iBase, iMesh
from .. import testhelper as unittest
import numpy

class TestSets(unittest.TestCase):
    def setUp(self):
        self.mesh = iMesh.Mesh()

        self.set  = self.mesh.createEntSet(True)
        self.set2 = self.mesh.getEntSets()[0]

        for i in range(5):
            self.mesh.createEntSet(True)
        self.sets = self.mesh.getEntSets()

        self.bset  = iBase.EntitySet(self.set)
        self.bset2 = iBase.EntitySet(self.set2)
        self.bsets = numpy.asarray(self.sets)

    def testDtype(self):
        self.assertEqual(self.sets.dtype,  iBase.EntitySet)
        self.assertEqual(self.bsets.dtype, iBase.EntitySet)

    def testFromArray(self):
        sets = iBase.Array(self.sets)
        self.assertArray(sets, self.sets)
        self.assertEqual(type(sets), iBase.Array)
        self.assertEqual(sets.instance, self.mesh)
        self.assertEqual(sets.dtype, iBase.EntitySet)

        sets = iBase.Array(self.bsets, instance=self.mesh)
        self.assertArray(sets, self.sets)
        self.assertEqual(type(sets), iBase.Array)
        self.assertEqual(sets.instance, self.mesh)
        self.assertEqual(sets.dtype, iBase.EntitySet)

    def testFromList(self):
        sets = iBase.Array(self.sets.tolist())
        self.assertArray(sets, self.sets)
        self.assertEqual(type(sets), iBase.Array)
        self.assertEqual(sets.instance, self.mesh)
        self.assertEqual(sets.dtype.type, iBase.EntitySet)

        sets = iBase.Array(self.bsets.tolist(), instance=self.mesh)
        self.assertArray(sets, self.sets)
        self.assertEqual(type(sets), iBase.Array)
        self.assertEqual(sets.instance, self.mesh)
        self.assertEqual(sets.dtype.type, iBase.EntitySet)

    def testFromScalar(self):
        sets = iBase.Array(self.set)
        self.assertEqual(sets, self.sets[0:1])
        self.assertEqual(type(sets), iBase.Array)
        self.assertEqual(sets.instance, self.mesh)
        self.assertEqual(sets.dtype.type, iBase.EntitySet)

        sets = iBase.Array(self.bset, instance=self.mesh)
        self.assertEqual(sets, self.sets[0:1])
        self.assertEqual(type(sets), iBase.Array)
        self.assertEqual(sets.instance, self.mesh)
        self.assertEqual(sets.dtype.type, iBase.EntitySet)

    def testEquality(self):
        self.assertEqual(self.set,  self.set2)
        self.assertEqual(self.set,  self.bset2)
        self.assertEqual(self.bset, self.set2)
        self.assertEqual(self.bset, self.bset2)

        self.assertFalse(self.set  != self.set2)
        self.assertFalse(self.set  != self.bset2)
        self.assertFalse(self.bset != self.set2)
        self.assertFalse(self.bset != self.bset2)

        self.assertArray(self.sets,  self.sets)
        self.assertArray(self.sets,  self.bsets)
        self.assertArray(self.bsets, self.sets)
        self.assertArray(self.bsets, self.bsets)

        self.assertFalse((self.sets[0:2] != self.sets[0:2]).any())
        self.assertFalse((self.sets[0:2] != self.bsets[0:2]).any())
        self.assertFalse((self.bsets[0:2] != self.sets[0:2]).any())

    def testIn(self):
        self.assertTrue(self.set  in self.sets)
        self.assertTrue(self.bset in self.sets)
        self.assertTrue(self.set  in self.bsets)
        self.assertTrue(self.bset in self.bsets)

    def testGet(self):
        self.assertEqual(self.sets[0], self.set)
        self.assertEqual(self.sets[0].instance, self.mesh)
        self.assertEqual(self.bsets[0], self.bset)

    def testSet(self):
        sets = self.sets.copy()
        sets[1] = self.set
        self.assertEqual(sets[1], self.set)
        self.assertEqual(sets[1].instance, self.mesh)

        bsets = self.bsets.copy()
        bsets[1] = self.bset
        self.assertEqual(bsets[1], self.bset)

    def testSlice(self):
        self.assertArray(self.sets[:],     self.sets)
        self.assertArray(self.sets[0:2],   [self.sets[0], self.sets[1]])
        self.assertArray(self.sets[0:4:2], [self.sets[0], self.sets[2]])
        self.assertArray(self.sets[1::-1], [self.sets[1], self.sets[0]])

        self.assertArray(self.bsets[:],     self.bsets)
        self.assertArray(self.bsets[0:2],   [self.bsets[0], self.bsets[1]])
        self.assertArray(self.bsets[0:4:2], [self.bsets[0], self.bsets[2]])
        self.assertArray(self.bsets[1::-1], [self.bsets[1], self.bsets[0]])

    def testSort(self):
        # TODO: assumes array is sorted to begin with
        for arr in self.sets, self.bsets:
            for kind in 'quicksort', 'mergesort', 'heapsort':
                rev = arr[::-1].copy()
                self.assertArray(numpy.sort(rev, kind=kind), arr)

                rev = arr[::-1].copy()
                indices = numpy.arange(len(arr))[::-1]
                self.assertArray(numpy.argsort(rev, kind=kind), indices)
