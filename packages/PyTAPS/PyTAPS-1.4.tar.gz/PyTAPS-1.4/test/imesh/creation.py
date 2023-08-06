from itaps import iBase, iMesh
from .. import testhelper as unittest
import numpy
Topo = iMesh.Topology # shorthand

class TestCreation(unittest.TestCase):
    def setUp(self):
        self.mesh = iMesh.Mesh()

    def testVertex(self):
        coords = [1.0, 2.0, 3.0]
        vert = self.mesh.createVtx(coords)

        self.assertEqual(self.mesh.        getNumOfType(iBase.Type.vertex), 1)
        self.assertEqual(self.mesh.rootSet.getNumOfType(iBase.Type.vertex), 1)
        self.assertEqual(self.mesh.        getNumOfTopo(Topo.point), 1)
        self.assertEqual(self.mesh.rootSet.getNumOfTopo(Topo.point), 1)

        self.assertArray(self.mesh.getVtxCoords(vert), coords)
        self.assertOut(self.mesh.getVtxCoords, [vert], ex=[coords])

        self.assertEqual(self.mesh.getEntType(vert), iBase.Type.vertex)
        self.assertOut(self.mesh.getEntType, [vert], ex=[iBase.Type.vertex])

        self.assertEqual(self.mesh.getEntTopo(vert), Topo.point)
        self.assertOut(self.mesh.getEntTopo, [vert], ex=[Topo.point])

        coords = [4.0, 5.0, 6.0]
        self.mesh.setVtxCoords(vert, coords)
        self.assertArray(self.mesh.getVtxCoords(vert), coords)
        self.assertOut(self.mesh.getVtxCoords, [vert], ex=[coords])

        self.mesh.deleteEnt(vert)
        self.assertEqual(self.mesh.getNumOfType(iBase.Type.all), 0)

    def testVertices(self):
        coords = [[ 1.0,  2.0,  3.0], [ 4.0,  5.0,  6.0],
                  [ 7.0,  8.0,  9.0], [10.0, 11.0, 12.0]]
        verts = self.mesh.createVtx(coords)

        self.assertEqual(self.mesh.        getNumOfType(iBase.Type.vertex), 4)
        self.assertEqual(self.mesh.rootSet.getNumOfType(iBase.Type.vertex), 4)
        self.assertEqual(self.mesh.        getNumOfTopo(Topo.point), 4)
        self.assertEqual(self.mesh.rootSet.getNumOfTopo(Topo.point), 4)

        self.assertArray(self.mesh.getVtxCoords(verts[0]), coords[0])
        self.assertOut(self.mesh.getVtxCoords, verts, ex=coords)

        self.assertEqual(self.mesh.getEntType(verts[0]), iBase.Type.vertex)
        self.assertOut(self.mesh.getEntType, verts, ex=[iBase.Type.vertex]*4)

        self.assertEqual(self.mesh.getEntTopo(verts[0]), Topo.point)
        self.assertOut(self.mesh.getEntTopo, verts, ex=[Topo.point]*4)

        coords = [[12.0, 11.0, 10.0], [ 9.0,  8.0,  7.0],
                  [ 6.0,  5.0,  4.0], [ 3.0,  2.0,  1.0]]
        self.mesh.setVtxCoords(verts, coords)
        
        self.assertArray(self.mesh.getVtxCoords(verts[0]), coords[0])
        self.assertOut(self.mesh.getVtxCoords, verts, ex=coords)

        self.mesh.deleteEnt(verts)
        self.assertEqual(self.mesh.getNumOfType(iBase.Type.all), 0)

    def testCreateEnt(self):
        coords = [[0.0, 0.0, 0.0], [0.0, 0.0, 1.0],
                  [0.0, 1.0, 0.0], [0.0, 1.0, 1.0]]
        verts = self.mesh.createVtx(coords)
        quad, status = self.mesh.createEnt(Topo.quadrilateral, verts)

        self.assertEqual(status, iBase.CreationStatus.new)
        self.assertEqual(self.mesh.        getNumOfType(iBase.Type.vertex), 4)
        self.assertEqual(self.mesh.rootSet.getNumOfType(iBase.Type.vertex), 4)
        self.assertEqual(self.mesh.        getNumOfType(iBase.Type.face), 1)
        self.assertEqual(self.mesh.rootSet.getNumOfType(iBase.Type.face), 1)
        self.assertEqual(self.mesh.        getNumOfTopo(Topo.point), 4)
        self.assertEqual(self.mesh.rootSet.getNumOfTopo(Topo.point), 4)
        self.assertEqual(self.mesh.        getNumOfTopo(Topo.quadrilateral), 1)
        self.assertEqual(self.mesh.rootSet.getNumOfTopo(Topo.quadrilateral), 1)

    def testCreateEntArr(self):
        coords = [[0.0, 0.0, 0.0], [0.0, 0.0, 1.0],
                  [0.0, 1.0, 0.0], [0.0, 1.0, 1.0]]
        verts = self.mesh.createVtx(coords)
        lines, status = self.mesh.createEntArr(Topo.line_segment, verts)

        self.assertArray(status, [iBase.CreationStatus.new]*2)
        self.assertEqual(self.mesh.        getNumOfType(iBase.Type.vertex), 4)
        self.assertEqual(self.mesh.rootSet.getNumOfType(iBase.Type.vertex), 4)
        self.assertEqual(self.mesh.        getNumOfType(iBase.Type.edge), 2)
        self.assertEqual(self.mesh.rootSet.getNumOfType(iBase.Type.edge), 2)
        self.assertEqual(self.mesh.        getNumOfTopo(Topo.point), 4)
        self.assertEqual(self.mesh.rootSet.getNumOfTopo(Topo.point), 4)
        self.assertEqual(self.mesh.        getNumOfTopo(Topo.line_segment), 2)
        self.assertEqual(self.mesh.rootSet.getNumOfTopo(Topo.line_segment), 2)

    def testCreateHOEnt(self):
        coords = [[0.0, 0.0, 0.0], [0.0, 0.0, 1.0],
                  [0.0, 1.0, 0.0], [0.0, 1.0, 1.0]]
        verts = self.mesh.createVtx(coords)
        pairs = numpy.roll(numpy.repeat(verts, 2), -1)

        lines, status = self.mesh.createEntArr(Topo.line_segment, pairs)
        self.assertArray(status, [iBase.CreationStatus.new]*4)

        quad, status = self.mesh.createEnt(Topo.quadrilateral, lines)
        self.assertEqual(status, iBase.CreationStatus.new)

        self.assertEqual(self.mesh.        getNumOfType(iBase.Type.vertex),  4)
        self.assertEqual(self.mesh.rootSet.getNumOfType(iBase.Type.vertex),  4)
        self.assertEqual(self.mesh.        getNumOfType(iBase.Type.edge),    4)
        self.assertEqual(self.mesh.rootSet.getNumOfType(iBase.Type.edge),    4)
        self.assertEqual(self.mesh.        getNumOfType(iBase.Type.face),    1)
        self.assertEqual(self.mesh.rootSet.getNumOfType(iBase.Type.face),    1)

        self.assertEqual(self.mesh.        getNumOfTopo(Topo.point),         4)
        self.assertEqual(self.mesh.rootSet.getNumOfTopo(Topo.point),         4)
        self.assertEqual(self.mesh.        getNumOfTopo(Topo.line_segment),  4)
        self.assertEqual(self.mesh.rootSet.getNumOfTopo(Topo.line_segment),  4)
        self.assertEqual(self.mesh.        getNumOfTopo(Topo.quadrilateral), 1)
        self.assertEqual(self.mesh.rootSet.getNumOfTopo(Topo.quadrilateral), 1)
