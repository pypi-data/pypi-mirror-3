from itaps import iBase, iMesh
from .. import testhelper as unittest
Topo = iMesh.Topology # shorthand

class TestIter(unittest.TestCase):
    def setUp(self):
        self.mesh = iMesh.Mesh()
        self.empty = self.mesh.createEntSet(True)

        self.ents = self.mesh.createVtx([[0,0,0]]*17)
        self.set = self.mesh.createEntSet(True)
        self.set.add(self.ents)

    def helpEmpty(self, iterator):
        for i in iterator:
            self.fail('empty iterator has >0 elements')

    def helpSingle(self, iterator):
        count = 0
        for i in iterator:
            self.assertEqual(i, self.ents[count])
            count += 1
        self.assertEqual(count, len(self.ents))

    def helpArr(self, iterator):
        count = 0
        for block in iterator:
            for i in block:
                self.assertEqual(i, self.ents[count])
                count += 1

        self.assertEqual(count, len(self.ents))

    def testSimpleEmpty(self):
        self.helpEmpty(iter(self.empty))
    def testEmpty(self):
        self.helpEmpty(self.empty.iterate(iBase.Type.all, Topo.all))
    def testArrEmpty(self):
        self.helpEmpty(self.empty.iterate(iBase.Type.all, Topo.all, 16))
    def testAltEmpty(self):
        self.helpEmpty(iMesh.Iterator(self.empty, iBase.Type.all, Topo.all))
    def testAltArrEmpty(self):
        self.helpEmpty(iMesh.Iterator(self.empty, iBase.Type.all, Topo.all, 16))

    def testSimpleSingle(self):
        self.helpSingle(iter(self.set))
    def testSingle(self):
        self.helpSingle(self.set.iterate(iBase.Type.all, Topo.all))
    def testAltEmpty(self):
        self.helpSingle(iMesh.Iterator(self.set, iBase.Type.all, Topo.all))

    def testArr(self):
        self.helpArr(self.set.iterate(iBase.Type.all, Topo.all, 16))
    def testAltArr(self):
        self.helpArr(iMesh.Iterator(self.set, iBase.Type.all, Topo.all, 16))

    def testReset(self):
        iterator = iMesh.Iterator(self.set, iBase.Type.all, Topo.all)
        self.helpSingle(iterator)
        iterator.reset()
        self.helpSingle(iterator)
