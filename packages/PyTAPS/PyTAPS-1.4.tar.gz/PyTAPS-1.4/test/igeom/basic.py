from itaps import iBase, iGeom
from .. import testhelper as unittest
import numpy
import tempfile

class TestBasic(unittest.TestCase):
    def setUp(self):
        self.geom = iGeom.Geom()

    def tearDown(self):
        self.geom.deleteAll()

    def testMinimal(self):
        root = self.geom.rootSet

        self.assertEqual(len(self.geom.tolerance), 2)
        self.assertEqual(self.geom.boundBox.shape, (2,3))
        self.assertTrue(isinstance(self.geom.parametric, bool))
        self.assertTrue(isinstance(self.geom.topoLevel, int))

        self.assertEqual(self.geom.getNumOfType(iBase.Type.region), 0)
        self.assertEqual(self.geom.getNumOfType(iBase.Type.all), 0)

    def testType(self):
        self.geom.createBrick(1, 1, 1)

        faces = self.geom.getEntities(iBase.Type.face)
        self.assertEqual(self.geom.getEntType(faces[0]), iBase.Type.face)
        self.assertArray(self.geom.getEntType(faces), [iBase.Type.face]*6)
        self.geom.getFaceType(faces[0])

    def testMeasure(self):
        self.geom.createBrick(1, 1, 1)
        ents = self.geom.getEntities(iBase.Type.all)
        self.assertArray(self.geom.measure(ents), [1]*(1+6+12+8))

    def testParametric(self):
        self.geom.createBrick(1, 1, 1)
        faces = self.geom.getEntities(iBase.Type.face)
        verts = self.geom.getEntities(iBase.Type.vertex)

        self.assertEqual(self.geom.isEntParametric(faces[0]), True)
        self.assertArray(self.geom.isEntParametric(faces), [True]*6)
        self.assertEqual(self.geom.isEntParametric(verts[0]), False)
        self.assertArray(self.geom.isEntParametric(verts), [False]*8)

    def testPeriodic(self):
        self.geom.createBrick(1, 1, 1)
        ents = self.geom.getEntities(iBase.Type.face)

        self.assertArray(self.geom.isEntPeriodic(ents[0]), [False]*2)
        self.assertArray(self.geom.isEntPeriodic(ents), [[False]*2]*6)

    def testTolerance(self):
        self.geom.createBrick(1, 1, 1)
        ents = self.geom.getEntities(iBase.Type.all)

        self.assertTrue(isinstance(self.geom.getEntTolerance(ents[0]), float))
        self.assertEqual(self.geom.getEntTolerance(ents).dtype, numpy.double)

    def testSave(self):
        self.geom.createBrick(1, 1, 1)
        file = tempfile.NamedTemporaryFile(suffix=".sat")

        self.geom.save(file.name)
        self.geom.deleteAll()
        self.assertEqual(self.geom.getNumOfType(iBase.Type.all), 0)
        
        self.geom.load(file.name)
        self.assertEqual(self.geom.getNumOfType(iBase.Type.region), 1)
