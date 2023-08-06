from itaps import iBase, iMesh
from .. import testhelper as unittest

class TestBasic(unittest.TestCase):
    def setUp(self):
        self.mesh = iMesh.Mesh()

    def testDimension(self):
        self.mesh.geometricDimension = 2
        self.assertEqual(self.mesh.geometricDimension, 2)

    def testOptimize(self):
        self.mesh.optimize()

    def testDefaultStorage(self):
        self.assertTrue(isinstance(self.mesh.defaultStorage, int))

    def testAdjTable(self):
        self.assertEqual(self.mesh.adjTable.shape, (4,4))
        self.mesh.adjTable = [[0, 0, 0, 0],
                              [0, 0, 0, 0],
                              [0, 0, 0, 0],
                              [0, 0, 0, 0]]

    def testRootSet(self):
        root = self.mesh.rootSet

        self.assertEqual(self.mesh.getNumOfType(iBase.Type.all),     0)
        self.assertEqual(root.     getNumOfType(iBase.Type.all),     0)
        self.assertEqual(self.mesh.getNumOfTopo(iMesh.Topology.all), 0)
        self.assertEqual(root.     getNumOfTopo(iMesh.Topology.all), 0)
