from itaps import iBase, iGeom
from .. import testhelper as unittest
from math import sqrt
import numpy

class TestCreation(unittest.TestCase):
    def setUp(self):
        self.geom = iGeom.Geom()

    def tearDown(self):
        self.geom.deleteAll()
        # Note: This breaks all but the first-run test when using CGM
        # self.geom = None

    def testSphere(self):
        ent = self.geom.createSphere(1)

        lo, hi = self.geom.getEntBoundBox(ent)
        self.assertArray(lo, [-1,-1,-1])
        self.assertArray(hi, [ 1, 1, 1])

    def testPrism(self):
        ent = self.geom.createPrism(2, 3, 4, 4)

    def testBrick(self):
        ent = self.geom.createBrick(2, 2, 2)

        lo, hi = self.geom.getEntBoundBox(ent)
        self.assertArray(lo, [-1,-1,-1])
        self.assertArray(hi, [ 1, 1, 1])

        # alternate form
        ent = self.geom.createBrick([2, 2, 2])

        lo, hi = self.geom.getEntBoundBox(ent)
        self.assertArray(lo, [-1,-1,-1])
        self.assertArray(hi, [ 1, 1, 1])

    def testCylinder(self):
        ent = self.geom.createCylinder(2, 1, 1)
        lo, hi = self.geom.getEntBoundBox(ent)
        self.assertArray(lo, [-1,-1,-1])
        self.assertArray(hi, [ 1, 1, 1])

    def testCone(self):
        ent = self.geom.createCone(2, 1, 1, 0.5)

        lo, hi = self.geom.getEntBoundBox(ent)
        self.assertArray(lo, [-1,-1,-1])
        self.assertArray(hi, [ 1, 1, 1])

    def testTorus(self):
        ent = self.geom.createTorus(2, 1)

        lo, hi = self.geom.getEntBoundBox(ent)
        self.assertArray(lo, [-3,-3,-1])
        self.assertArray(hi, [ 3, 3, 1])

    def testMove(self):
        ent = self.geom.createBrick(2, 2, 2)
        self.geom.moveEnt(ent, [1,0,0])

        lo, hi = self.geom.getEntBoundBox(ent)
        self.assertArray(lo, [ 0,-1,-1])
        self.assertArray(hi, [ 2, 1, 1])

    def testScale(self):
        ent = self.geom.createBrick(2, 2, 2)
        self.geom.scaleEnt(ent, [1,2,3])

        lo, hi = self.geom.getEntBoundBox(ent)
        self.assertArray(lo, [-1,-2,-3])
        self.assertArray(hi, [ 1, 2, 3])

    def testReflect(self):
        ent = self.geom.createBrick(2, 4, 6)
        self.geom.reflectEnt(ent, [1,1,0])

        lo, hi = self.geom.getEntBoundBox(ent)
        self.assertTrue((abs(lo - [-2,-1,-3]) < 1e-5).all())
        self.assertTrue((abs(hi - [ 2, 1, 3]) < 1e-5).all())

    def testRotate(self):
        ent = self.geom.createBrick(2, 4, 6)
        self.geom.rotateEnt(ent, 90, [1,0,0])

        lo, hi = self.geom.getEntBoundBox(ent)
        self.assertArray(lo, [-1,-3,-2])
        self.assertArray(hi, [ 1, 3, 2])

    def testSweep(self):
        ent = self.geom.createBrick(2, 2, 2)
        face = self.geom.getEntities(iBase.Type.face)[0]
        edge = self.geom.getEntAdj(face, iBase.Type.edge)[0]

        axis = self.geom.getEntTangent(edge, [0,0,0])
        result = self.geom.sweepEntAboutAxis(edge, 360, axis)
        lo, hi = self.geom.getEntBoundBox(result)
        self.assertTrue((abs(lo - [-sqrt(2),-1,-sqrt(2)]) < 1e-5).all())
        self.assertTrue((abs(hi - [ sqrt(2), 1, sqrt(2)]) < 1e-5).all())

    def testSection(self):
        ent = self.geom.createSphere(1)
        self.geom.sectionEnt(ent, [1,0,0], 0, False)
        self.assertEqual(self.geom.getNumOfType(iBase.Type.face), 2)

    def testImprint(self):
        ent1 = self.geom.createBrick(2, 2, 2)
        ent2 = self.geom.createBrick(2, 2, 2)
        self.geom.moveEnt(ent2, [1, 0, 0])
        self.geom.imprintEnts([ent1, ent2])
        self.assertEqual(self.geom.getNumOfType(iBase.Type.vertex), 24)

        self.geom.deleteAll()

        # alternate syntax
        ent1 = self.geom.createBrick(2, 2, 2)
        ent2 = self.geom.createBrick(2, 2, 2)
        self.geom.moveEnt(ent2, [1, 0, 0])
        self.geom.imprintEnts(ent1, ent2)
        self.assertEqual(self.geom.getNumOfType(iBase.Type.vertex), 24)

    def testMerge(self):
        ent1 = self.geom.createBrick(2, 2, 2)
        ent2 = self.geom.createBrick(2, 2, 2)

        ents = self.geom.getEntities(iBase.Type.face)

        self.geom.moveEnt(ent2, [2,0,0])
        self.geom.mergeEnts(ents, 0.1)
        self.assertEqual(self.geom.getNumOfType(iBase.Type.face), 11)

    def testDelete(self):
        ent1 = self.geom.createBrick(2, 2, 2)
        ent2 = self.geom.createBrick(2, 2, 2)

        self.geom.deleteEnt(ent1)
        self.assertEqual(self.geom.getNumOfType(iBase.Type.region), 1)

        self.geom.deleteAll()
        self.assertEqual(self.geom.getNumOfType(iBase.Type.all), 0)

    def testCopy(self):
        ent1 = self.geom.createBrick(2, 2, 2)
        ent2 = self.geom.copyEnt(ent1)

        self.assertEqual(self.geom.getNumOfType(iBase.Type.region), 2)
        self.assertArray(numpy.array(self.geom.getEntBoundBox(ent1)),
                         numpy.array(self.geom.getEntBoundBox(ent2)))

    def testUnite(self):
        ent1 = self.geom.createBrick(2, 2, 4)
        ent2 = self.geom.createBrick(2, 4, 2)
        ent3 = self.geom.createBrick(4, 2, 2)
        union = self.geom.uniteEnts([ent1, ent2, ent3])

        lo, hi = self.geom.getEntBoundBox(union)
        self.assertArray(lo, [-2,-2,-2])
        self.assertArray(hi, [ 2, 2, 2])

        # alternate syntax
        ent1 = self.geom.createBrick(2, 2, 4)
        ent2 = self.geom.createBrick(2, 4, 2)
        ent3 = self.geom.createBrick(4, 2, 2)
        union = self.geom.uniteEnts(ent1, ent2, ent3)

        lo, hi = self.geom.getEntBoundBox(union)
        self.assertArray(lo, [-2,-2,-2])
        self.assertArray(hi, [ 2, 2, 2])

    def testIntersection(self):
        ent1 = self.geom.createBrick(2, 2, 4)
        ent2 = self.geom.createBrick(2, 4, 2)
        isect = self.geom.intersectEnts(ent1, ent2)

        lo, hi = self.geom.getEntBoundBox(isect)
        self.assertArray(lo, [-1,-1,-1])
        self.assertArray(hi, [ 1, 1, 1])

    def testSubtract(self):
        ent1 = self.geom.createBrick(4, 4, 4)
        ent2 = self.geom.createBrick(2, 4, 4)
        self.geom.moveEnt(ent2,[1,0,0])
        sub = self.geom.subtractEnts(ent1, ent2)

        lo, hi = self.geom.getEntBoundBox(sub)
        self.assertArray(lo, [-2,-2,-2])
        self.assertArray(hi, [ 0, 2, 2])
