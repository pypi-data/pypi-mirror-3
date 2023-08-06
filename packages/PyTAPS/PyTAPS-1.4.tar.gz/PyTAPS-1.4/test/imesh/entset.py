from itaps import iBase, iMesh
from .. import testhelper as unittest

class TestEntSet(unittest.TestCase):
    def setUp(self):
        self.mesh = iMesh.Mesh()
        self.set = self.mesh.createEntSet(True)

    def testCreation(self):
        self.assertEqual(self.set.instance, self.mesh)
        self.assertEqual(self.set.isList, True)

        self.assertEqual(self.set.getNumEntSets(), 0)
        self.assertEqual(self.mesh.getNumEntSets(), 1)
        self.assertEqual(self.mesh.rootSet.getNumEntSets(), 1)

        sets = self.mesh.getEntSets()
        self.assertArray(sets, self.mesh.rootSet.getEntSets())
        self.assertEqual(self.set, sets[0])

        self.mesh.destroyEntSet(self.set)
        self.assertEqual(self.mesh.getNumEntSets(), 0)
        self.assertEqual(self.mesh.rootSet.getNumEntSets(), 0)

    def testEnt(self):
        ent = self.mesh.createVtx([1,2,3])
        self.assertEqual(self.mesh.getNumOfType(iBase.Type.all), 1)
        self.assertEqual(self.mesh.getNumOfTopo(iMesh.Topology.all), 1)
        self.assertFalse(self.set.contains(ent))
        self.assertTrue(ent not in self.set)
        self.assertEqual(self.set.getNumOfType(iBase.Type.all), 0)
        self.assertEqual(self.set.getNumOfTopo(iMesh.Topology.all), 0)
        self.assertEqual(len(self.set), 0)

        self.set.add(ent)
        self.assertTrue(self.set.contains(ent))
        self.assertTrue(ent in self.set)
        self.assertEqual(self.set.getNumOfType(iBase.Type.all), 1)
        self.assertEqual(self.set.getNumOfTopo(iMesh.Topology.all), 1)
        self.assertEqual(len(self.set), 1)

        self.set.remove(ent)
        self.assertFalse(self.set.contains(ent))
        self.assertTrue(ent not in self.set)
        self.assertEqual(self.set.getNumOfType(iBase.Type.all), 0)
        self.assertEqual(self.set.getNumOfTopo(iMesh.Topology.all), 0)
        self.assertEqual(len(self.set), 0)

    def testEntArr(self):
        ents = self.mesh.createVtx([[1,2,3], [4,5,6], [7,8,9]])
        self.assertEqual(self.mesh.getNumOfType(iBase.Type.all), 3)
        self.assertEqual(self.mesh.getNumOfTopo(iMesh.Topology.all), 3)
        self.assertFalse(self.set.contains(ents).any())
        self.assertEqual(self.set.getNumOfType(iBase.Type.all), 0)
        self.assertEqual(self.set.getNumOfTopo(iMesh.Topology.all), 0)
        self.assertEqual(len(self.set), 0)

        self.set.add(ents)
        self.assertTrue(self.set.contains(ents).all())
        self.assertEqual(self.set.getNumOfType(iBase.Type.all), 3)
        self.assertEqual(self.set.getNumOfTopo(iMesh.Topology.all), 3)
        self.assertEqual(len(self.set), 3)

        self.set.remove(ents)
        self.assertFalse(self.set.contains(ents).any())
        self.assertEqual(self.set.getNumOfType(iBase.Type.all), 0)
        self.assertEqual(self.set.getNumOfTopo(iMesh.Topology.all), 0)
        self.assertEqual(len(self.set), 0)

    def testEntSet(self):
        sub = self.mesh.createEntSet(True)
        subsub = self.mesh.createEntSet(True)

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

        self.mesh.destroyEntSet(sub)

    def testChildren(self):
        sub = self.mesh.createEntSet(True)
        self.set.addChild(sub)

        self.assertTrue(self.set.isChild(sub))
        self.assertEqual(self.set.getNumChildren(), 1)
        self.assertEqual(sub.getNumParents(), 1)

        self.assertOut(self.set.getChildren, ex=iBase.Array([sub]))
        self.assertOut(sub.getParents, ex=iBase.Array([self.set]))

        self.set.removeChild(sub)

        self.assertFalse(self.set.isChild(sub))
        self.assertEqual(self.set.getNumChildren(), 0)
        self.assertEqual(sub.getNumParents(),  0)

    def testSubtract(self):
        set2 = self.mesh.createEntSet(True)
        ents = self.mesh.createVtx([[1,2,3], [4,5,6]])
        self.set.add(ents)
        set2.add(ents[0])

        diff = self.set - set2
        self.assertFalse(diff.contains(ents[0]))
        self.assertTrue (diff.contains(ents[1]))

        diff = self.set.difference(set2)
        self.assertFalse(diff.contains(ents[0]))
        self.assertTrue (diff.contains(ents[1]))

    def testIntersect(self):
        set2 = self.mesh.createEntSet(True)
        ents = self.mesh.createVtx([[1,2,3], [4,5,6], [7,8,9]])
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
        set2 = self.mesh.createEntSet(True)
        ents = self.mesh.createVtx([[1,2,3], [4,5,6]])
        self.set.add(ents[0])
        set2.add(ents[1])

        union = self.set | set2
        self.assertTrue(union.contains(ents[0]))
        self.assertTrue(union.contains(ents[1]))

        union = self.set.union(set2)
        self.assertTrue(union.contains(ents[0]))
        self.assertTrue(union.contains(ents[1]))
