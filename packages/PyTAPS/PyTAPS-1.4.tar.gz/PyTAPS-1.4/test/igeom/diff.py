from itaps import iBase, iGeom
from .. import testhelper as unittest
import numpy

class TestDiff(unittest.TestCase):
    def setUp(self):
        self.geom = iGeom.Geom()

    def tearDown(self):
        self.geom.deleteAll()
        # Note: This breaks all but the first-run test when using CGM
        # self.geom = None

    def testClosestPt(self):
        self.geom.createBrick(2, 2, 2)
        faces = self.geom.getEntities(iBase.Type.face)
        result = [ [ 0,  0,  1],
                   [ 0,  0, -1],
                   [ 0, -1,  0],
                   [-1,  0,  0],
                   [ 0,  1,  0],
                   [ 1,  0,  0] ]

        ##### 1 entity, 1 vertex
        coords = self.geom.getEntClosestPt(faces[0], [0,0,0])
        self.assertArray(coords, result[0])
        coords = self.geom.getEntClosestPt(faces[0:1], [0,0,0])
        self.assertArray(coords, result[0:1])

        ##### 1 entity, n vertices
        coords = self.geom.getEntClosestPt(faces[0], [[0,0,0]]*6)
        self.assertArray(coords, result[0:1]*6)

        ##### n entities, 1 vertex
        coords = self.geom.getEntClosestPt(faces, [0,0,0])
        self.assertArray(coords, result)

        ##### n entities, n vertices
        coords = self.geom.getEntClosestPt(faces, [[0,0,0]]*6)
        self.assertArray(coords, result)

    def testNormalXYZ(self):
        self.geom.createBrick(1, 1, 1)
        faces = self.geom.getEntities(iBase.Type.face)
        result = [ [ 0,  0,  1],
                   [ 0,  0, -1],
                   [ 0, -1,  0],
                   [-1, -0,  0],
                   [ 0,  1,  0],
                   [ 1,  0,  0] ]

        ##### 1 entity, 1 vertex
        coords = self.geom.getEntNormal(faces[0], [0,0,0])
        self.assertArray(coords, result[0])
        coords = self.geom.getEntNormal(faces[0:1], [0,0,0])
        self.assertArray(coords, result[0:1])

        ##### 1 entity, n vertices
        coords = self.geom.getEntNormal(faces[0], [[0,0,0]]*6)
        self.assertArray(coords, result[0:1]*6)

        ##### n entities, 1 vertex
        coords = self.geom.getEntNormal(faces, [0,0,0])
        self.assertArray(coords, result)

        ##### n entities, n vertices
        coords = self.geom.getEntNormal(faces, [[0,0,0]]*6)
        self.assertArray(coords, result)

    def testNormalUV(self):
        self.geom.createBrick(1, 1, 1)
        faces = self.geom.getEntities(iBase.Type.face)
        result = [ [ 0,  0,  1],
                   [ 0,  0, -1],
                   [ 0, -1,  0],
                   [-1, -0,  0],
                   [ 0,  1,  0],
                   [ 1,  0,  0] ]

        ##### 1 entity, 1 vertex
        coords = self.geom.getEntNormal(faces[0], [0,0], iGeom.Basis.uv)
        self.assertArray(coords, result[0])
        coords = self.geom.getEntNormal(faces[0:1], [0,0], iGeom.Basis.uv)
        self.assertArray(coords, result[0:1])

        ##### 1 entity, n vertices
        coords = self.geom.getEntNormal(faces[0], [[0,0]]*6, iGeom.Basis.uv)
        self.assertArray(coords, result[0:1]*6)

        ##### n entities, 1 vertex
        coords = self.geom.getEntNormal(faces, [0,0], iGeom.Basis.uv)
        self.assertArray(coords, result)

        ##### n entities, n vertices
        coords = self.geom.getEntNormal(faces, [[0,0]]*6, iGeom.Basis.uv)
        self.assertArray(coords, result)

    def testNormalPl(self):
        self.geom.createBrick(2, 2, 2)
        faces = self.geom.getEntities(iBase.Type.face)
        result = [ [ 0,  0,  1],
                   [ 0,  0, -1],
                   [ 0, -1,  0],
                   [-1,  0,  0],
                   [ 0,  1,  0],
                   [ 1,  0,  0] ]

        ##### 1 entity, 1 vertex
        norm, pts = self.geom.getEntNormalPl(faces[0], [0,0,0])
        self.assertArray(norm, result[0])
        self.assertArray(pts,  result[0])
        norm, pts = self.geom.getEntNormalPl(faces[0:1], [0,0,0])
        self.assertArray(norm, result[0:1])
        self.assertArray(pts,  result[0:1])

        ##### 1 entity, n vertices
        norm, pts = self.geom.getEntNormalPl(faces[0], [[0,0,0]]*6)
        self.assertArray(norm, result[0:1]*6)
        self.assertArray(pts,  result[0:1]*6)

        ##### n entities, 1 vertex
        norm, pts = self.geom.getEntNormalPl(faces, [0,0,0])
        self.assertArray(norm, result)
        self.assertArray(pts,  result)

        ##### n entities, n vertices
        norm, pts = self.geom.getEntNormalPl(faces, [[0,0,0]]*6)
        self.assertArray(norm, result)
        self.assertArray(pts,  result)

    def testTangentXYZ(self):
        self.geom.createBrick(1, 1, 1)
        edges = self.geom.getEntities(iBase.Type.edge)
        result = [ [ 0,  1,  0],
                   [-1,  0,  0],
                   [ 0, -1,  0],
                   [ 1,  0,  0],
                   [ 0, -1,  0],
                   [-1,  0,  0],
                   [ 0,  1,  0],
                   [ 1,  0,  0],
                   [ 0,  0, -1],
                   [ 0,  0, -1],
                   [ 0,  0, -1],
                   [ 0,  0, -1] ]

        ##### 1 entity, 1 vertex
        coords = self.geom.getEntTangent(edges[0], [0,0,0])
        self.assertArray(coords, result[0])
        coords = self.geom.getEntTangent(edges[0:1], [0,0,0])
        self.assertArray(coords, result[0:1])

        ##### 1 entity, n vertices
        coords = self.geom.getEntTangent(edges[0], [[0,0,0]]*12)
        self.assertArray(coords, result[0:1]*12)

        ##### n entities, 1 vertex
        coords = self.geom.getEntTangent(edges, [0,0,0])
        self.assertArray(coords, result)

        ##### n entities, n vertices
        coords = self.geom.getEntTangent(edges, [[0,0,0]]*12)
        self.assertArray(coords, result)

    def testTangentU(self):
        self.geom.createBrick(1, 1, 1)
        edges = self.geom.getEntities(iBase.Type.edge)
        result = [ [ 0,  1,  0],
                   [-1,  0,  0],
                   [ 0, -1,  0],
                   [ 1,  0,  0],
                   [ 0, -1,  0],
                   [-1,  0,  0],
                   [ 0,  1,  0],
                   [ 1,  0,  0],
                   [ 0,  0, -1],
                   [ 0,  0, -1],
                   [ 0,  0, -1],
                   [ 0,  0, -1] ]

        ##### 1 entity, 1 vertex
        coords = self.geom.getEntTangent(edges[0], [0], iGeom.Basis.u)
        self.assertArray(coords, result[0])
        coords = self.geom.getEntTangent(edges[0:1], [0], iGeom.Basis.u)
        self.assertArray(coords, result[0:1])

        ##### 1 entity, n vertices
        coords = self.geom.getEntTangent(edges[0], [[0]]*12, iGeom.Basis.u)
        self.assertArray(coords, result[0:1]*12)

        ##### n entities, 1 vertex
        coords = self.geom.getEntTangent(edges, [0], iGeom.Basis.u)
        self.assertArray(coords, result)

        ##### n entities, n vertices
        coords = self.geom.getEntTangent(edges, [[0]]*12, iGeom.Basis.u)
        self.assertArray(coords, result)

    def testCurvatureXYZ(self):
        self.geom.createCylinder(1,1,1)
        edges = self.geom.getEntities(iBase.Type.edge)
        faces = self.geom.getEntities(iBase.Type.face)

        ##### edges; 1 entity, 1 vertex
        coords = self.geom.getEntCurvature(edges[0], [0,1,0])
        self.assertArray(coords, [0,-1,0])
        coords = self.geom.getEntCurvature(edges[0], [0,1,0],
                                           type=iBase.Type.edge)
        self.assertArray(coords, [0,-1,0])
        coords = self.geom.getEntCurvature(edges[0:1], [0,1,0])
        self.assertArray(coords, [[0,-1,0]])

        ##### edges; 1 entity, n vertices
        coords = self.geom.getEntCurvature(edges[0], [[0,1,0],[0,-1,0]])
        self.assertArray(coords, [[0,-1,0],[0,1,0]])

        ##### edges; n entities, 1 vertex
        coords = self.geom.getEntCurvature(edges, [0,1,0])
        self.assertArray(coords, [[0,-1,0],[0,-1,0]])

        ##### edges; n entities, n vertices
        coords = self.geom.getEntCurvature(edges, [[0,1,0],[0,-1,0]])
        self.assertArray(coords, [[0,-1,0],[0,1,0]])

        ##### faces; 1 entity, 1 vertex
        coords = self.geom.getEntCurvature(faces[0], [0,1,0])
        self.assertEqual(len(coords), 2)
        self.assertArray(coords[0], [0,0,0])
        self.assertArray(coords[1], [1,0,0])
        coords = self.geom.getEntCurvature(faces[0], [0,1,0],
                                           type=iBase.Type.face)
        self.assertEqual(len(coords), 2)
        self.assertArray(coords[0], [0,0,0])
        self.assertArray(coords[1], [1,0,0])
        coords = self.geom.getEntCurvature(faces[0:1], [0,1,0])
        self.assertEqual(len(coords), 2)
        self.assertArray(coords[0][0], [0,0,0])
        self.assertArray(coords[1][0], [1,0,0])

        ##### faces; 1 entity, n vertices
        coords = self.geom.getEntCurvature(faces[0], [[0,1,0],[0,-1,0]])
        self.assertEqual(len(coords), 2)
        self.assertArray(coords[0], [[0,0,0], [ 0,0,0]])
        self.assertArray(coords[1], [[1,0,0], [-1,0,0]])

        ##### faces; n entities, 1 vertex
        coords = self.geom.getEntCurvature(faces, [0,1,0])
        self.assertEqual(len(coords), 2)
        self.assertArray(coords[0], [[0,0,0], [0,0,0], [0,0,0]])
        self.assertArray(coords[1], [[1,0,0], [0,0,0], [0,0,0]])

        ##### faces; n entities, n vertices
        coords = self.geom.getEntCurvature(faces, [[0,1,0]]*3)
        self.assertEqual(len(coords), 2)
        self.assertArray(coords[0], [[0,0,0], [0,0,0], [0,0,0]])
        self.assertArray(coords[1], [[1,0,0], [0,0,0], [0,0,0]])

    def testCurvatureUV(self):
        self.geom.createCylinder(1,1,1)
        faces = self.geom.getEntities(iBase.Type.face)

        ##### 1 entity, 1 vertex
        coords = self.geom.getEntCurvature(faces[0], [0,0], iGeom.Basis.uv)
        self.assertEqual(len(coords), 2)
        self.assertArray(coords[0], [ 0, 0, 0])
        self.assertArray(coords[1], [ 0,-1, 0])
        coords = self.geom.getEntCurvature(faces[0], [0,0], iGeom.Basis.uv,
                                           iBase.Type.face)
        self.assertEqual(len(coords), 2)
        self.assertArray(coords[0], [ 0, 0, 0])
        self.assertArray(coords[1], [ 0,-1, 0])
        coords = self.geom.getEntCurvature(faces[0:1], [0,0], iGeom.Basis.uv)
        self.assertEqual(len(coords), 2)
        self.assertArray(coords[0][0], [ 0, 0, 0])
        self.assertArray(coords[1][0], [ 0,-1, 0])

        ##### 1 entity, n vertices
        coords = self.geom.getEntCurvature(faces[0], [[0,0],[0,0]],
                                           iGeom.Basis.uv)
        self.assertEqual(len(coords), 2)
        self.assertArray(coords[0], [[ 0, 0, 0], [ 0, 0, 0]])
        self.assertArray(coords[1], [[ 0,-1, 0], [ 0,-1, 0]])

        ##### n entities, 1 vertex
        coords = self.geom.getEntCurvature(faces, [0,0], iGeom.Basis.uv)
        self.assertEqual(len(coords), 2)
        self.assertArray(coords[0], [[ 0, 0, 0], [ 0, 0, 0], [ 0, 0, 0]])
        self.assertArray(coords[1], [[ 0,-1, 0], [ 0, 0, 0], [ 0, 0, 0]])

        ##### n entities, n vertices
        coords = self.geom.getEntCurvature(faces, [[0,0]]*3, iGeom.Basis.uv)
        self.assertEqual(len(coords), 2)
        self.assertArray(coords[0], [[ 0, 0, 0], [ 0, 0, 0], [ 0, 0, 0]])
        self.assertArray(coords[1], [[ 0,-1, 0], [ 0, 0, 0], [ 0, 0, 0]])

    def testEval(self):
        self.geom.createCylinder(2,1,1)
        edges = self.geom.getEntities(iBase.Type.edge)
        faces = self.geom.getEntities(iBase.Type.face)

        ##### edges; 1 entity, 1 vertex
        result = numpy.array([ [  0,  1, -1],
                               [  1,  0,  0],
                               [  0, -1,  0] ])
        coords = self.geom.getEntEval(edges[0], [0,1,0])
        self.assertArray(coords, result)
        coords = self.geom.getEntEval(edges[0:1], [0,1,0])
        self.assertArray(coords, result.reshape(3,1,3))
        coords = self.geom.getEntEval(edges[0], [0,1,0], iBase.Type.edge)
        self.assertArray(coords, result)
        coords = self.geom.getEntEval(edges[0:1], [0,1,0], iBase.Type.edge)
        self.assertArray(coords, result.reshape(3,1,3))

        ##### edges; 1 entity, n vertices
        result = numpy.array([ [[  0,  1, -1], [  0, -1, -1]],
                               [[  1,  0,  0], [ -1,  0,  0]],
                               [[  0, -1,  0], [  0,  1,  0]] ])
        coords = self.geom.getEntEval(edges[0], [[0,1,0], [0,-1,0]])
        self.assertArray(coords, result)
        coords = self.geom.getEntEval(edges[0], [[0,1,0], [0,-1,0]],
                                      iBase.Type.edge)
        self.assertArray(coords, result)

        ##### edges; n entities, 1 vertex
        result = numpy.array([ [[  0,  1, -1], [  0,  1,  1]],
                               [[  1,  0,  0], [ -1,  0,  0]],
                               [[  0, -1,  0], [  0, -1,  0]] ])
        coords = self.geom.getEntEval(edges, [0,1,0])
        self.assertArray(coords, result)
        coords = self.geom.getEntEval(edges, [0,1,0], iBase.Type.edge)
        self.assertArray(coords, result)

        ##### edges; n entities, n vertices
        result = numpy.array([ [[  0,  1, -1], [  0, -1,  1]],
                               [[  1,  0,  0], [  1,  0,  0]],
                               [[  0, -1,  0], [  0,  1,  0]] ])
        coords = self.geom.getEntEval(edges, [[0,1,0],[0,-1,0]],
                                      iBase.Type.edge)
        self.assertArray(coords, result)
        coords = self.geom.getEntEval(edges, [[0,1,0],[0,-1,0]],
                                      iBase.Type.edge)
        self.assertArray(coords, result)

        ##### faces; 1 entity, 1 vertex
        result = numpy.array([ [ 0,  1,  0,],
                               [ 0,  1,  0,],
                               [ 0,  0,  0,],
                               [ 1,  0,  0,] ])
        coords = self.geom.getEntEval(faces[0], [0,1,0])
        self.assertArray(coords, result)
        coords = self.geom.getEntEval(faces[0:1], [0,1,0])
        self.assertArray(coords, result.reshape(4,1,3))
        coords = self.geom.getEntEval(faces[0], [0,1,0], iBase.Type.face)
        self.assertArray(coords, result)
        coords = self.geom.getEntEval(faces[0:1], [0,1,0], iBase.Type.face)
        self.assertArray(coords, result.reshape(4,1,3))

        ##### faces; 1 entity, n vertices
        result = numpy.array([ [[ 0,  1,  0,], [ 0, -1,  0,]],
                               [[ 0,  1,  0,], [ 0, -1,  0,]],
                               [[ 0,  0,  0,], [ 0,  0,  0,]],
                               [[ 1,  0,  0,], [-1,  0,  0,]] ])

        coords = self.geom.getEntEval(faces[0], [[0,1,0],[0,-1,0]])
        self.assertArray(coords, result)
        coords = self.geom.getEntEval(faces[0], [[0,1,0],[0,-1,0]],
                                      iBase.Type.face)
        self.assertArray(coords, result)

        ##### faces; n entities, 1 vertex
        result = numpy.array([ [[ 0,  1,  0,], [ 0,  1, -1,], [ 0,  1,  1,]],
                               [[ 0,  1,  0,], [ 0,  0, -1,], [ 0,  0,  1,]],
                               [[ 0,  0,  0,], [-0,  0,  0,], [ 0,  0,  0,]],
                               [[ 1,  0,  0,], [ 0,  0,  0,], [ 0,  0,  0,]] ])
        coords = self.geom.getEntEval(faces, [0,1,0])
        self.assertArray(coords, result)
        coords = self.geom.getEntEval(faces, [0,1,0], iBase.Type.face)
        self.assertArray(coords, result)

        ##### faces; n entities, n vertices
        result = numpy.array([ [[ 0,  1,  0,], [ 0,  1, -1,], [ 0,  1,  1,]],
                               [[ 0,  1,  0,], [ 0,  0, -1,], [ 0,  0,  1,]],
                               [[ 0,  0,  0,], [-0,  0,  0,], [ 0,  0,  0,]],
                               [[ 1,  0,  0,], [ 0,  0,  0,], [ 0,  0,  0,]] ])
        coords = self.geom.getEntEval(faces, [[0,1,0]]*3)
        self.assertArray(coords, result)
        coords = self.geom.getEntEval(faces, [[0,1,0]]*3, iBase.Type.face)
        self.assertArray(coords, result)

    def testClassification(self):
        self.geom.createBrick(4, 4, 4)
        faces = self.geom.getEntities(iBase.Type.face)

        found = self.geom.getPtClass([1, 1, 2])
        self.assertTrue(found in faces)
        self.assertRaises(iBase.ITAPSError, self.geom.getPtClass, [2, 2, 4])

        found = self.geom.getPtClass([[1, 1, 2], [1, 2, 1], [2, 1, 1]])
        for i in found:
            self.assertTrue(i in faces)
        
        self.assertRaises(iBase.ITAPSError, self.geom.getPtClass,
                          [[2, 2, 4], [1, 2, 1], [2, 1, 1]])

    def testNormalSense(self):
        self.geom.createBrick(2, 2, 2)
        region = self.geom.getEntities(iBase.Type.region)[0]
        faces = self.geom.getEntities(iBase.Type.face)

        ##### 1 face, 1 region
        sense = self.geom.getEntNormalSense(faces[0], region)
        self.assertEqual(sense, 1)
        sense = self.geom.getEntNormalSense(faces[0:1], [region])
        self.assertArray(sense, [1])

        ##### 1 face, n regions
        sense = self.geom.getEntNormalSense(faces[0], [region]*6)
        self.assertArray(sense, [1]*6)

        ##### n faces, 1 region
        sense = self.geom.getEntNormalSense(faces, region)
        self.assertArray(sense, [1]*6)

        ##### n faces, n regions
        sense = self.geom.getEntNormalSense(faces, [region]*6)
        self.assertArray(sense, [1]*6)

    def testEgFcSense(self):
        self.geom.createBrick(2, 2, 2)
        faces = self.geom.getEntities(iBase.Type.face)
        edges = self.geom.getEntAdj(faces, iBase.Type.edge)

        ##### 1 edge, 1 face
        sense = self.geom.getEgFcSense(edges[0,0], faces[0])
        self.assertEqual(sense, 1)
        sense = self.geom.getEgFcSense([edges[0,1]], faces[0:1])
        self.assertArray(sense, [1])

        ##### 1 edge, n faces
        sense = self.geom.getEgFcSense(edges[0,0], [faces[0]]*6)
        self.assertArray(sense, [1]*6)

        ##### n edges, 1 face
        sense = self.geom.getEgFcSense(edges[0], faces[0])
        self.assertArray(sense, [1]*4)

        ##### n edges, n faces
        first_edges = [ edges[i,0] for i in range(len(edges)) ]
        sense = self.geom.getEgFcSense(first_edges, faces)
        self.assertArray(sense, [1]*6)

    def testEgVtxSense(self):
        self.geom.createBrick(2, 2, 2)
        edges = self.geom.getEntities(iBase.Type.edge)
        verts = self.geom.getEntAdj(edges, iBase.Type.vertex)

        pre  = [verts[i,0] for i in xrange(len(verts))]
        post = [verts[i,1] for i in xrange(len(verts))]

        ##### 1 edge, 1 vertex, 1 vertex
        sense = self.geom.getEgVtxSense(edges[0], pre[0], post[0])
        self.assertEqual(sense, 1)
        sense = self.geom.getEgVtxSense(edges[0:1], pre[0:1], post[0:1])
        self.assertArray(sense, [1])

        ##### 1 edge, 1 vertex, n vertices
        sense = self.geom.getEgVtxSense(edges[0], pre[0], post[0:1]*2)
        self.assertArray(sense, [1, 1])

        ##### 1 edge, n vertices, 1 vertex
        sense = self.geom.getEgVtxSense(edges[0], pre[0:1]*2, post[0])
        self.assertArray(sense, [1, 1])

        ##### 1 edge, n vertices, n vertices
        sense = self.geom.getEgVtxSense(edges[0], verts[0], verts[0][::-1])
        self.assertArray(sense, [1, -1])

        twice = edges[0:1].tolist()*2

        ##### n edges, 1 vertex, 1 vertex
        sense = self.geom.getEgVtxSense(twice, pre[0], post[0])
        self.assertArray(sense, [1, 1])

        ##### n edges, 1 vertex, n vertices
        sense = self.geom.getEgVtxSense(twice, pre[0], post[0:1]*2)
        self.assertArray(sense, [1, 1])

        ##### n edges, n vertices, 1 vertex
        sense = self.geom.getEgVtxSense(twice, pre[0:1]*2, post[0])
        self.assertArray(sense, [1, 1])

        ##### n edges, n vertices, n vertices
        sense = self.geom.getEgVtxSense(edges, pre, post)
        self.assertArray(sense, [1]*12)

    def testFcDegenerate(self):
        self.geom.createBrick(2, 2, 2)
        faces = self.geom.getEntities(iBase.Type.face)

        degen = self.geom.isFcDegenerate(faces[0])
        self.assertFalse(degen)

        degen = self.geom.isFcDegenerate(faces)
        self.assertFalse(degen.any())

    def testRayIntersect(self):
        self.geom.createSphere(1)

        ents, isect, param = self.geom.getPtRayIntersect([0,0,0], [1,0,0])
        # TODO: finish this

    def test1stDeriv(self):
        self.geom.createBrick(1, 1, 1)
        faces = self.geom.getEntities(iBase.Type.face)

        offsets = range(0, 7*3, 3)
        u = [ [ 1,  0,  0],
              [ 1,  0,  0],
              [-0,  0,  1],
              [ 0,  0, -1],
              [ 0,  0, -1],
              [ 0, -0,  1] ]
        v = [ [ 0,  1,  0],
              [ 0,  1,  0],
              [ 1,  0,  0],
              [-0,  1,  0],
              [ 1,  0,  0],
              [ 0,  1,  0] ]

        deriv = self.geom.getEnt1stDerivative(faces[0], [0,0])
        self.assertArray(deriv[0], u[0])
        self.assertArray(deriv[1], v[0])

        deriv = self.geom.getEnt1stDerivative(faces[0:1], [[0,0]])
        self.assertArray(deriv.offsets, offsets[0:2])
        self.assertArray(deriv.data[0], u[0:1])
        self.assertArray(deriv.data[1], v[0:1])

        deriv = self.geom.getEnt1stDerivative(faces, [[0,0]]*6)
        self.assertArray(deriv.offsets, offsets)
        self.assertArray(deriv.data[0], u)
        self.assertArray(deriv.data[1], v)

    def test2ndDeriv(self):
        self.geom.createBrick(1, 1, 1)
        faces = self.geom.getEntities(iBase.Type.face)

        # TODO: check results once I know what they should be
        deriv = self.geom.getEnt2ndDerivative(faces[0], [0,0])

        deriv = self.geom.getEnt2ndDerivative(faces[0:1], [[0,0]],
                                              Stg.interleaved)

        deriv = self.geom.getEnt2ndDerivative(faces, [[0,0]]*6)
