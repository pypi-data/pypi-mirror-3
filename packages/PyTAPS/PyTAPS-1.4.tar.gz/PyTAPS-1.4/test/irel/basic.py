from itaps import iBase, iMesh, iGeom, iRel
from .. import testhelper as unittest
import numpy

class TestBasic(unittest.TestCase):
    def setUp(self):
        self.mesh = iMesh.Mesh()
        self.geom = iGeom.Geom()
        self.rel  = iRel.Rel()

    def tearDown(self):
        self.geom.deleteAll()

    def testMinimal(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.entity,
                                   self.geom, iRel.Type.entity)

        self.assertEqual(pair.instance, self.rel)
        self.assertEqual(pair.left.instance,  self.mesh)
        self.assertEqual(pair.right.instance, self.geom)

        self.rel.destroyPair(pair)

        self.mesh = None
        #self.geom = None
        self.rel  = None

    def testPair(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.entity,
                                   self.geom, iRel.Type.entity)

        self.assertEqual(self.rel.findPairs(self.mesh), [pair])
        self.assertEqual(self.rel.findPairs(self.geom), [pair])

        self.rel.destroyPair(pair)
        self.assertEqual(len(self.rel.findPairs(self.mesh)), 0)
        self.assertEqual(len(self.rel.findPairs(self.geom)), 0)

    def testPairAlt(self):
        pair = self.rel.createPair(
            self.mesh, iRel.Type.entity, iRel.Status.active,
            self.geom, iRel.Type.entity, iRel.Status.active)

        self.assertEqual(self.rel.findPairs(self.mesh), [pair])
        self.assertEqual(self.rel.findPairs(self.geom), [pair])

        self.rel.destroyPair(pair)
        self.assertEqual(len(self.rel.findPairs(self.mesh)), 0)
        self.assertEqual(len(self.rel.findPairs(self.geom)), 0)
