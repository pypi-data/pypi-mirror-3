from itaps import iBase, iGeom
from .. import testhelper as unittest
import numpy

class TestCoords(unittest.TestCase):
    def setUp(self):
        self.geom = iGeom.Geom()

    def tearDown(self):
        self.geom.deleteAll()

    def testVtxCoordsXYZ(self):
        ent = self.geom.createBrick(2, 2, 2)
        verts = self.geom.getEntities(iBase.Type.vertex)

        coords = self.geom.getVtxCoords(verts[0])
        self.assertArray(coords, [1,-1,1])

        coords = self.geom.getVtxCoords(verts)
        self.assertArray(coords, [ [ 1, -1,  1],
                                  [ 1,  1,  1],
                                  [-1,  1,  1],
                                  [-1, -1,  1],
                                  [ 1,  1, -1],
                                  [ 1, -1, -1],
                                  [-1, -1, -1],
                                  [-1,  1, -1] ])

    def testVtxCoordsUV(self):
        ent = self.geom.createBrick(2, 2, 2)
        faces = self.geom.getEntities(iBase.Type.face)
        verts = self.geom.getEntAdj(faces, iBase.Type.vertex)

        result = [ [ 1, -1],
                   [ 1,  1],
                   [ 1, -1],
                   [-1,  1],
                   [-1,  1],
                   [ 1, -1] ]

        # 1 vertex, 1 entity
        coords = self.geom.getVtxCoords(verts[0,0], faces[0])
        self.assertArray(coords, [1,-1])
        coords = self.geom.getVtxCoords(verts[0,0], (faces[0], iGeom.Basis.uv))
        self.assertArray(coords, [1,-1])
        coords = self.geom.getVtxCoords(verts[0,0], faces[0:1])
        self.assertArray(coords, [[1,-1]])
        coords = self.geom.getVtxCoords(verts[0,0], (faces[0:1],
                                                     iGeom.Basis.uv))
        self.assertArray(coords, [[1,-1]])

        # 1 vertex, n entities
        coords = self.geom.getVtxCoords(verts[0,0], [faces[0]]*4)
        self.assertArray(coords, [[1,-1]]*4)
        coords = self.geom.getVtxCoords(verts[0,0], ([faces[0]]*4,
                                                     iGeom.Basis.uv))
        self.assertArray(coords, [[1,-1]]*4)

        # n vertices, 1 entity
        coords = self.geom.getVtxCoords(verts[0], faces[0])
        self.assertArray(coords, [[1,-1], [1,1], [-1,1], [-1,-1]])
        coords = self.geom.getVtxCoords(verts[0], (faces[0], iGeom.Basis.uv))
        self.assertArray(coords, [[1,-1], [1,1], [-1,1], [-1,-1]])

        # n vertices, n entities
        first_verts = [ verts[i,0] for i in range(len(verts)) ]
        coords = self.geom.getVtxCoords(first_verts, faces)
        self.assertArray(coords, result)
        coords = self.geom.getVtxCoords(first_verts, (faces, iGeom.Basis.uv))
        self.assertArray(coords, result)

    def testVtxCoordsU(self):
        ent = self.geom.createBrick(2, 2, 2)
        edges = self.geom.getEntities(iBase.Type.edge)
        verts = self.geom.getEntAdj(edges, iBase.Type.vertex)

        # 1 vertex, 1 entity
        coords = self.geom.getVtxCoords(verts[0,0], edges[0])
        self.assertArray(coords, [-1])
        coords = self.geom.getVtxCoords(verts[0,0], (edges[0], iGeom.Basis.u))
        self.assertArray(coords, [-1])
        coords = self.geom.getVtxCoords(verts[0,0], edges[0:1])
        self.assertArray(coords, [[-1]])
        coords = self.geom.getVtxCoords(verts[0,0], (edges[0:1], iGeom.Basis.u))
        self.assertArray(coords, [[-1]])

        # 1 vertex, n entities
        coords = self.geom.getVtxCoords(verts[0,0], [edges[0]]*4)
        self.assertArray(coords, [[-1]]*4)
        coords = self.geom.getVtxCoords(verts[0,0], ([edges[0]]*4,
                                                     iGeom.Basis.u))
        self.assertArray(coords, [[-1]]*4)

        # n vertices, 1 entity
        coords = self.geom.getVtxCoords(verts[0], edges[0])
        self.assertArray(coords, [[-1], [1]])
        coords = self.geom.getVtxCoords(verts[0], (edges[0], iGeom.Basis.u))
        self.assertArray(coords, [[-1], [1]])

        # n vertices, n entities
        first_verts = [ verts[i,0] for i in range(len(verts)) ]
        coords = self.geom.getVtxCoords(first_verts, edges)
        self.assertArray(coords, [[-1]]*12)
        coords = self.geom.getVtxCoords(first_verts, (edges, iGeom.Basis.u))
        self.assertArray(coords, [[-1]]*12)

    def testEntCoordsXYZtoUV(self):
        ent = self.geom.createBrick(2, 2, 2)
        faces = self.geom.getEntities(iBase.Type.face)

        ##### 1 vertex, 1 entity
        coords = self.geom.getEntCoords([0,0,0], dest=faces[0])
        self.assertArray(coords, [0,0])
        coords = self.geom.getEntCoords([0,0,0], dest=(faces[0],iGeom.Basis.uv))
        self.assertArray(coords, [0,0])
        coords = self.geom.getEntCoords([0,0,0], dest=faces[0:1])
        self.assertArray(coords, [[0,0]])
        coords = self.geom.getEntCoords([0,0,0], dest=(faces[0:1],
                                                       iGeom.Basis.uv))
        self.assertArray(coords, [[0,0]])

        ##### 1 vertex, n entities
        coords = self.geom.getEntCoords([0,0,0], dest=faces)
        self.assertArray(coords, [[0,0]]*6)
        coords = self.geom.getEntCoords([0,0,0], dest=(faces, iGeom.Basis.uv))
        self.assertArray(coords, [[0,0]]*6)

        ##### n vertices, 1 entity
        coords = self.geom.getEntCoords([[0,0,0]]*6, dest=faces[0])
        self.assertArray(coords, [[0,0]]*6)
        coords = self.geom.getEntCoords([[0,0,0]]*6, dest=(faces[0],
                                                           iGeom.Basis.uv))
        self.assertArray(coords, [[0,0]]*6)

        ##### n vertices, n entities
        coords = self.geom.getEntCoords([[0,0,0]]*6, dest=faces)
        self.assertArray(coords, [[0,0]]*6)
        coords = self.geom.getEntCoords([[0,0,0]]*6, dest=(faces,
                                                           iGeom.Basis.uv))
        self.assertArray(coords, [[0,0]]*6)

    def testEntCoordsUVtoXYZ(self):
        ent = self.geom.createBrick(2, 2, 2)
        faces = self.geom.getEntities(iBase.Type.face)
        result = [ [ 0,  0,  1],
                   [ 0,  0, -1],
                   [ 0, -1,  0],
                   [-1,  0,  0],
                   [ 0,  1,  0],
                   [ 1,  0,  0] ]

        ##### 1 vertex, 1 entity
        coords = self.geom.getEntCoords([0,0], src=faces[0])
        self.assertArray(coords, result[0])
        coords = self.geom.getEntCoords([0,0], src=(faces[0], iGeom.Basis.uv))
        self.assertArray(coords, result[0])
        coords = self.geom.getEntCoords([0,0], src=faces[0:1])
        self.assertArray(coords, result[0:1])
        coords = self.geom.getEntCoords([0,0], src=(faces[0:1], iGeom.Basis.uv))
        self.assertArray(coords, result[0:1])

        ##### 1 vertex, n entities
        coords = self.geom.getEntCoords([0,0], src=faces)
        self.assertArray(coords, result)
        coords = self.geom.getEntCoords([0,0], src=(faces, iGeom.Basis.uv))
        self.assertArray(coords, result)

        ##### n vertices, 1 entity
        coords = self.geom.getEntCoords([[0,0]]*6, src=faces[0])
        self.assertArray(coords, result[0:1]*6)
        coords = self.geom.getEntCoords([[0,0]]*6, src=(faces[0],
                                                        iGeom.Basis.uv))
        self.assertArray(coords, result[0:1]*6)

        ##### n vertices, n entities
        coords = self.geom.getEntCoords([[0,0]]*6, src=faces)
        self.assertArray(coords, result)
        coords = self.geom.getEntCoords([[0,0]]*6, src=(faces, iGeom.Basis.uv))
        self.assertArray(coords, result)

    def testEntCoordsXYZtoU(self):
        ent = self.geom.createBrick(2, 2, 2)
        edges = self.geom.getEntities(iBase.Type.edge)

        ##### 1 vertex, 1 entity
        coords = self.geom.getEntCoords([0,0,0], dest=edges[0])
        self.assertArray(coords, [0])
        coords = self.geom.getEntCoords([0,0,0], dest=(edges[0], iGeom.Basis.u))
        self.assertArray(coords, [0])
        coords = self.geom.getEntCoords([0,0,0], dest=edges[0:1])
        self.assertArray(coords, [[0]])
        coords = self.geom.getEntCoords([0,0,0], dest=(edges[0:1],
                                                       iGeom.Basis.u))
        self.assertArray(coords, [[0]])

        ##### 1 vertex, n entities
        coords = self.geom.getEntCoords([0,0,0], dest=edges)
        self.assertArray(coords, [[0]]*12)
        coords = self.geom.getEntCoords([0,0,0], dest=(edges, iGeom.Basis.u))
        self.assertArray(coords, [[0]]*12)

        ##### n vertices, 1 entity
        coords = self.geom.getEntCoords([[0,0,0]]*12, dest=edges[0])
        self.assertArray(coords, [[0]]*12)
        coords = self.geom.getEntCoords([[0,0,0]]*12, dest=(edges[0],
                                                            iGeom.Basis.u))
        self.assertArray(coords, [[0]]*12)

        ##### n vertices, n entities
        coords = self.geom.getEntCoords([[0,0,0]]*12, dest=edges)
        self.assertArray(coords, [[0]]*12)
        coords = self.geom.getEntCoords([[0,0,0]]*12, dest=(edges,
                                                            iGeom.Basis.u))
        self.assertArray(coords, [[0]]*12)

    def testEntCoordsUtoXYZ(self):
        ent = self.geom.createBrick(2, 2, 2)
        edges = self.geom.getEntities(iBase.Type.edge)
        result = [ [ 1,  0,  1],
                   [ 0,  1,  1],
                   [-1,  0,  1],
                   [ 0, -1,  1],
                   [ 1,  0, -1],
                   [ 0, -1, -1],
                   [-1,  0, -1],
                   [ 0,  1, -1],
                   [-1, -1,  0],
                   [ 1, -1,  0],
                   [-1,  1,  0],
                   [ 1,  1,  0] ]

        ##### 1 vertex, 1 entity
        coords = self.geom.getEntCoords([0], src=edges[0])
        self.assertArray(coords, result[0])
        coords = self.geom.getEntCoords([0], src=(edges[0], iGeom.Basis.u))
        self.assertArray(coords, result[0])
        coords = self.geom.getEntCoords([0], src=edges[0:1])
        self.assertArray(coords, result[0:1])
        coords = self.geom.getEntCoords([0], src=(edges[0:1], iGeom.Basis.u))
        self.assertArray(coords, result[0:1])

        ##### 1 vertex, n entities
        coords = self.geom.getEntCoords([0], src=edges)
        self.assertArray(coords, result)
        coords = self.geom.getEntCoords([0], src=(edges, iGeom.Basis.u))
        self.assertArray(coords, result)

        ##### n vertices, 1 entity
        coords = self.geom.getEntCoords([[0]]*12, src=edges[0])
        self.assertArray(coords, result[0:1]*12)
        coords = self.geom.getEntCoords([[0]]*12, src=(edges[0], iGeom.Basis.u))
        self.assertArray(coords, result[0:1]*12)

        ##### n vertices, n entities
        coords = self.geom.getEntCoords([[0]]*12, src=edges)
        self.assertArray(coords, result)
        coords = self.geom.getEntCoords([[0]]*12, src=(edges, iGeom.Basis.u))
        self.assertArray(coords, result)

    def testEntCoordsUtoUV(self):
        ent = self.geom.createBrick(2, 2, 2)
        edges = self.geom.getEntities(iBase.Type.edge)
        faces = self.geom.getEntities(iBase.Type.face)

        ##### 1 vertex, 1 edge, 1 face
        coords = self.geom.getEntCoords([0], src=edges[0], dest=faces[0])
        self.assertArray(coords, [1,0])
        coords = self.geom.getEntCoords([0], src =(edges[0], iGeom.Basis.u),
                                             dest=(faces[0], iGeom.Basis.uv))
        self.assertArray(coords, [1,0])
        coords = self.geom.getEntCoords([0], src=edges[0:1], dest=faces[0:1])
        self.assertArray(coords, [[1,0]])
        coords = self.geom.getEntCoords([0], src =(edges[0:1], iGeom.Basis.u),
                                             dest=(faces[0:1], iGeom.Basis.uv))
        self.assertArray(coords, [[1,0]])

        ##### 1 vertex, 1 edge, n faces
        result = [[1,0], [1,0], [1,1], [-1,0], [-1,1], [1,0]]
        coords = self.geom.getEntCoords([0], src=edges[0], dest=faces)
        self.assertArray(coords, result)
        coords = self.geom.getEntCoords([0], src =(edges[0], iGeom.Basis.u),
                                             dest=(faces,    iGeom.Basis.uv))
        self.assertArray(coords, result)

        ##### 1 vertex, n edges, 1 face
        result = [[1,0], [0,1], [-1,0], [0,-1], [1,0], [0,-1], [-1,0], [0,1],
                  [-1,-1], [1,-1], [-1,1], [1,1]]
        coords = self.geom.getEntCoords([0], src=edges, dest=faces[0])
        self.assertArray(coords, result)
        coords = self.geom.getEntCoords([0], src =(edges,    iGeom.Basis.u),
                                             dest=(faces[0], iGeom.Basis.uv))
        self.assertArray(coords, result)

        ##### 1 vertex, n edges, n faces
        result = [[1,0], [0,1], [1,-1], [-1,-1], [1,1], [-1,-1]]
        coords = self.geom.getEntCoords([0], src=edges[0:6], dest=faces)
        self.assertArray(coords, result)
        coords = self.geom.getEntCoords([0], src =(edges[0:6], iGeom.Basis.u),
                                             dest=(faces,      iGeom.Basis.uv))
        self.assertArray(coords, result)

        ##### n vertices, 1 edge, 1 face
        coords = self.geom.getEntCoords([[0]]*6, src=edges[0], dest=faces[0])
        self.assertArray(coords, [[1,0]]*6)
        coords = self.geom.getEntCoords([[0]]*6,
                                        src =(edges[0], iGeom.Basis.u),
                                        dest=(faces[0], iGeom.Basis.uv))
        self.assertArray(coords, [[1,0]]*6)

        ##### n vertices, 1 edge, n faces
        result = [[1,0], [1,0], [1,1], [-1,0], [-1,1], [1,0]]
        coords = self.geom.getEntCoords([[0]]*6, src=edges[0], dest=faces)
        self.assertArray(coords, result)
        coords = self.geom.getEntCoords([[0]]*6,
                                        src =(edges[0], iGeom.Basis.u),
                                        dest=(faces,    iGeom.Basis.uv))
        self.assertArray(coords, result)

        ##### n vertices, n edges, 1 face
        result = [[1,0], [0,1], [-1,0], [0,-1], [1,0], [0,-1], [-1,0], [0,1],
                  [-1,-1], [1,-1], [-1,1], [1,1]]
        coords = self.geom.getEntCoords([[0]]*12, src=edges, dest=faces[0])
        self.assertArray(coords, result)
        coords = self.geom.getEntCoords([[0]]*12, 
                                        src =(edges,    iGeom.Basis.u),
                                        dest=(faces[0], iGeom.Basis.uv))
        self.assertArray(coords, result)

        ##### n vertices, n edges, n faces
        result = [[1,0], [0,1], [1,-1], [-1,-1], [1,1], [-1,-1]]
        coords = self.geom.getEntCoords([[0]]*6, src=edges[0:6], dest=faces)
        self.assertArray(coords, result)
        coords = self.geom.getEntCoords([[0]]*6, 
                                        src =(edges[0:6], iGeom.Basis.u),
                                        dest=(faces,      iGeom.Basis.uv))
        self.assertArray(coords, result)

    def testRange(self):
        ent = self.geom.createBrick(2, 2, 2)
        faces = self.geom.getEntities(iBase.Type.face)
        edges = self.geom.getEntities(iBase.Type.edge)

        lo, hi = self.geom.getEntRange(faces[0], iGeom.Basis.uv)
        self.assertArray(lo, [-1,-1])
        self.assertArray(hi, [ 1, 1])
        lo, hi = self.geom.getEntRange(faces[0])
        self.assertArray(lo, [-1,-1])
        self.assertArray(hi, [ 1, 1])

        lo, hi = self.geom.getEntRange(faces, iGeom.Basis.uv)
        self.assertArray(lo, [[-1,-1]]*6)
        self.assertArray(hi, [[ 1, 1]]*6)
        lo, hi = self.geom.getEntRange(faces)
        self.assertArray(lo, [[-1,-1]]*6)
        self.assertArray(hi, [[ 1, 1]]*6)

        lo, hi = self.geom.getEntRange(edges[0], iGeom.Basis.u)
        self.assertArray(lo, [-1])
        self.assertArray(hi, [ 1])
        lo, hi = self.geom.getEntRange(edges[0])
        self.assertArray(lo, [-1])
        self.assertArray(hi, [ 1])

        lo, hi = self.geom.getEntRange(edges, iGeom.Basis.u)
        self.assertArray(lo, [[-1]]*12)
        self.assertArray(hi, [[ 1]]*12)
        lo, hi = self.geom.getEntRange(edges)
        self.assertArray(lo, [[-1]]*12)
        self.assertArray(hi, [[ 1]]*12)
