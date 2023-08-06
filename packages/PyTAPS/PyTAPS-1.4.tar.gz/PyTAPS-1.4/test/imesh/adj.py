from itaps import iBase, iMesh
from .. import testhelper as unittest
import numpy
Topo = iMesh.Topology # shorthand

class TestAdj(unittest.TestCase):
    def setUp(self):
        self.mesh = iMesh.Mesh()
        self.coords = [[0.0, 0.0, 0.0], [0.0, 0.0, 1.0],
                       [0.0, 1.0, 0.0], [0.0, 1.0, 1.0]]
        self.verts = self.mesh.createVtx(self.coords)

        pairs = numpy.roll(numpy.repeat(self.verts, 2), -1)
        self.lines = self.mesh.createEntArr(Topo.line_segment, pairs)[0]

    def testAdj(self):
        adj = self.mesh.getEntAdj(self.verts[1], iBase.Type.all)
        self.assertArray(adj, self.lines[0:2])

        adj = self.mesh.getEntAdj(self.verts, iBase.Type.all)

        for i in range(len(adj)):
            self.assertEqual(adj.length(i), 2)

        self.assertArray(adj[0], self.lines[::3])
        self.assertArray(adj[1], self.lines[0:2])
        self.assertArray(adj[2], self.lines[1:3])
        self.assertArray(adj[3], self.lines[2:4])

        self.assertEqual(adj[0, 0], self.lines[0])
        self.assertEqual(adj[2, 1], self.lines[2])

        self.assertRaises(IndexError, lambda: adj[0, 2])

    def test2ndAdj(self):
        quad = self.mesh.createEnt(Topo.quadrilateral, self.lines)[0]

        adj = self.mesh.getEnt2ndAdj(self.verts[1], iBase.Type.edge,
                                     iBase.Type.vertex)
        self.assertArray(adj, self.verts[0:3:2])

        adj = self.mesh.getEnt2ndAdj(self.verts, iBase.Type.edge,
                                     iBase.Type.vertex)

        for i in range(len(adj)):
            self.assertEqual(adj.length(i), 2)

        self.assertArray(adj[0], self.verts[1::2])
        self.assertArray(adj[1], self.verts[0::2])
        self.assertArray(adj[2], self.verts[1::2])
        self.assertArray(adj[3], self.verts[0::2])

        self.assertEqual(adj[0, 0], self.verts[1])
        self.assertEqual(adj[2, 1], self.verts[3])

        self.assertRaises(IndexError, lambda: adj[0, 2])

    def testAdjIndices(self):
        entset = self.mesh.createEntSet(True)
        entset.add(self.verts)
        ents, adj = entset.getAdjEntIndices(iBase.Type.all, Topo.all,
                                            iBase.Type.all)

        self.assertArray(ents, self.verts)
        self.assertArray(adj.data, self.lines)

        self.assertArray(adj.indices[0], [0,3])
        self.assertArray(adj.indices[1], [0,1])
        self.assertArray(adj.indices[2], [1,2])
        self.assertArray(adj.indices[3], [2,3])
