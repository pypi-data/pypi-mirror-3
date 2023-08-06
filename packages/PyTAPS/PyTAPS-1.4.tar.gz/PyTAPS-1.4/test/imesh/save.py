from itaps import iBase, iMesh
from .. import testhelper as unittest
import tempfile
Topo = iMesh.Topology # shorthand

class TestSave(unittest.TestCase):
    def setUp(self):
        self.mesh = iMesh.Mesh()
        self.coords = [[0.0, 0.0, 0.0], [0.0, 0.0, 1.0],
                       [0.0, 1.0, 0.0], [0.0, 1.0, 1.0]]
        verts = self.mesh.createVtx(self.coords)
        self.mesh.createEnt(Topo.quadrilateral, verts)

    def testSave(self):
        f = tempfile.NamedTemporaryFile()

        self.mesh.save(f.name)
        
        self.mesh = iMesh.Mesh()
        self.assertEqual(self.mesh.getNumOfType(iBase.Type.all), 0)

        self.mesh.load(f.name)

        verts = self.mesh.getEntities(iBase.Type.vertex)
        self.assertArray(self.mesh.getVtxCoords(verts), self.coords)

        self.assertEqual(self.mesh.getNumOfType(iBase.Type.vertex),  4)
        self.assertEqual(self.mesh.getNumOfType(iBase.Type.face),    1)
        self.assertEqual(self.mesh.getNumOfTopo(Topo.point),         4)
        self.assertEqual(self.mesh.getNumOfTopo(Topo.quadrilateral), 1)

    def testAltSave(self):
        f = tempfile.NamedTemporaryFile()

        self.mesh.rootSet.save(f.name)
        
        self.mesh = iMesh.Mesh()
        self.assertEqual(self.mesh.getNumOfType(iBase.Type.all), 0)

        self.mesh.rootSet.load(f.name)

        verts = self.mesh.getEntities(iBase.Type.vertex)
        self.assertArray(self.mesh.getVtxCoords(verts), self.coords)

        self.assertEqual(self.mesh.getNumOfType(iBase.Type.vertex),  4)
        self.assertEqual(self.mesh.getNumOfType(iBase.Type.face),    1)
        self.assertEqual(self.mesh.getNumOfTopo(Topo.point),         4)
        self.assertEqual(self.mesh.getNumOfTopo(Topo.quadrilateral), 1)
