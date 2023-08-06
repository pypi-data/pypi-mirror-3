from itaps import iBase, iGeom
from .. import testhelper as unittest

class TestIter(unittest.TestCase):
    def setUp(self):
        self.geom = iGeom.Geom()
        self.empty = self.geom.createEntSet(True)

        self.geom.createBrick(1,1,1)
        self.ents = self.geom.getEntities(iBase.Type.all)
        self.set = self.geom.createEntSet(True)
        self.set.add(self.ents)

    def tearDown(self):
        self.geom.deleteAll()
        self.geom = None

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
        self.helpEmpty(self.empty.iterate(iBase.Type.all))
    def testArrEmpty(self):
        self.helpEmpty(self.empty.iterate(iBase.Type.all, 16))
    def testAltEmpty(self):
        self.helpEmpty(iGeom.Iterator(self.empty, iBase.Type.all))
    def testAltArrEmpty(self):
        self.helpEmpty(iGeom.Iterator(self.empty, iBase.Type.all, 16))

    def testSimpleSingle(self):
        self.helpSingle(iter(self.set))
    def testSingle(self):
        self.helpSingle(self.set.iterate(iBase.Type.all))
    def testAltEmpty(self):
        self.helpSingle(iGeom.Iterator(self.set, iBase.Type.all))

    def testArr(self):
        self.helpArr(self.set.iterate(iBase.Type.all, 16))
    def testAltArr(self):
        self.helpArr(iGeom.Iterator(self.set, iBase.Type.all, 16))

    def testReset(self):
        iterator = iGeom.Iterator(self.set, iBase.Type.all)
        self.helpSingle(iterator)
        iterator.reset()
        self.helpSingle(iterator)
