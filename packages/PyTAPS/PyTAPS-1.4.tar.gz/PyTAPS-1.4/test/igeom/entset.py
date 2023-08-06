from itaps import iBase, iGeom
from .. import testhelper as unittest

class TestEntSet(unittest.TestCase):
    def setUp(self):
        self.geom = iGeom.Geom()
        self.set = self.geom.createEntSet(True)

    def tearDown(self):
        self.geom.deleteAll()
        self.geom = None

    def testCreation(self):
        self.assertEqual(self.set.instance, self.geom)
        self.assertEqual(self.set.isList, True)
        self.assertEqual(self.set.getNumEntSets(), 0)
        self.assertEqual(self.geom.getNumEntSets(), 1)
        self.assertEqual(self.geom.rootSet.getNumEntSets(), 1)

        sets = self.geom.getEntSets()
        self.assertArray(sets, self.geom.rootSet.getEntSets())
        self.assertEqual(self.set, sets[0])

        self.geom.destroyEntSet(self.set)
        self.assertEqual(self.geom.getNumEntSets(), 0)
        self.assertEqual(self.geom.rootSet.getNumEntSets(), 0)

    def testEnt(self):
        ent = self.geom.createBrick(1,1,1)
        self.assertEqual(self.geom.getNumOfType(iBase.Type.all), 1+6+12+8)
        self.assertFalse(self.set.contains(ent))
        self.assertTrue(ent not in self.set)
        self.assertEqual(self.set.getNumOfType(iBase.Type.all), 0)
        self.assertEqual(len(self.set), 0)

        self.set.add(ent)
        self.assertTrue(self.set.contains(ent))
        self.assertTrue(ent in self.set)
        self.assertEqual(self.set.getNumOfType(iBase.Type.all), 1)
        self.assertEqual(len(self.set), 1)

        self.set.remove(ent)
        self.assertFalse(self.set.contains(ent))
        self.assertTrue(ent not in self.set)
        self.assertEqual(self.set.getNumOfType(iBase.Type.all), 0)
        self.assertEqual(len(self.set), 0)

    def testEntArr(self):
        self.geom.createBrick(1,1,1)
        ents = self.geom.getEntities(iBase.Type.all)
        self.assertEqual(self.geom.getNumOfType(iBase.Type.all), 1+6+12+8)
        self.assertFalse(self.set.contains(ents).any())
        self.assertEqual(self.set.getNumOfType(iBase.Type.all), 0)
        self.assertEqual(len(self.set.getEntities(iBase.Type.all)), 0)
        self.assertEqual(len(self.set), 0)

        self.set.add(ents)
        self.assertTrue(self.set.contains(ents).all())
        self.assertEqual(self.set.getNumOfType(iBase.Type.all), 1+6+12+8)
        self.assertEqual(len(self.set.getEntities(iBase.Type.all)), 1+6+12+8)
        self.assertEqual(len(self.set), 1+6+12+8)

        self.set.remove(ents)
        self.assertFalse(self.set.contains(ents).any())
        self.assertEqual(self.set.getNumOfType(iBase.Type.all), 0)
        self.assertEqual(len(self.set.getEntities(iBase.Type.all)), 0)
        self.assertEqual(len(self.set), 0)

    def testEntSet(self):
        sub = self.geom.createEntSet(True)
        subsub = self.geom.createEntSet(True)

        self.assertFalse(self.set.contains(sub))
        self.assertTrue(sub not in self.set)
        self.assertEqual(self.set.getNumEntSets(), 0)
        self.assertEqual(len(self.set.getEntSets()), 0)

        self.set.add(sub)
        sub.add(subsub)

        self.assertTrue(self.set.contains(sub))
        self.assertTrue(sub in self.set)
        self.assertEqual(self.set.getNumEntSets(), 2)
        self.assertEqual(self.set.getNumEntSets(0), 1)
        self.assertEqual(self.set.getNumEntSets(1), 2)

        self.assertArraySorted(self.set.getEntSets(),
                               iBase.Array([sub, subsub]))
        self.assertArraySorted(self.set.getEntSets(0), iBase.Array([sub]))
        self.assertArraySorted(self.set.getEntSets(1),
                               iBase.Array([sub, subsub]))

        self.set.remove(sub)
        self.assertFalse(self.set.contains(sub))
        self.assertTrue(sub not in self.set)

        self.geom.destroyEntSet(sub)

    def testChildren(self):
        sub = self.geom.createEntSet(True)
        self.set.addChild(sub)
        return

        self.assertTrue(self.set.isChild(sub))
        self.assertEqual(self.set.getNumChildren(), 1)
        self.assertEqual(sub.getNumParents(),  1)

        self.assertEqual(self.set.getChildren()[0], sub)
        self.assertEqual(sub.getParents()[0], self.set)

        self.set.removeChild(sub)

        self.assertFalse(self.set.isChild(sub))
        self.assertEqual(self.set.getNumChildren(), 0)
        self.assertEqual(sub.getNumParents(), 0)

    def testSubtract(self):
        set2 = self.geom.createEntSet(True)
        self.geom.createBrick(1, 1, 1)
        ents = self.geom.getEntities(iBase.Type.all)

        self.set.add(ents)
        set2.add(ents[0])

        diff = self.set - set2
        self.assertFalse(diff.contains(ents[0]))
        self.assertTrue (diff.contains(ents[1]))

        diff = self.set.difference(set2)
        self.assertFalse(diff.contains(ents[0]))
        self.assertTrue (diff.contains(ents[1]))

    def testIntersect(self):
        set2 = self.geom.createEntSet(True)
        self.geom.createBrick(1,1,1)
        ents = self.geom.getEntities(iBase.Type.all)

        self.set.add(ents[0:2])
        set2.add(ents[1:3])

        sect = self.set & set2
        self.assertFalse(sect.contains(ents[0]))
        self.assertTrue (sect.contains(ents[1]))
        self.assertFalse(sect.contains(ents[2]))

        sect = self.set.intersection(set2)
        self.assertFalse(sect.contains(ents[0]))
        self.assertTrue (sect.contains(ents[1]))
        self.assertFalse(sect.contains(ents[2]))

    def testUnite(self):
        set2 = self.geom.createEntSet(True)
        self.geom.createBrick(1,1,1)
        ents = self.geom.getEntities(iBase.Type.all)

        self.set.add(ents[0])
        set2.add(ents[1])

        union = self.set | set2
        self.assertTrue(union.contains(ents[0]))
        self.assertTrue(union.contains(ents[1]))

        union = self.set.union(set2)
        self.assertTrue(union.contains(ents[0]))
        self.assertTrue(union.contains(ents[1]))
