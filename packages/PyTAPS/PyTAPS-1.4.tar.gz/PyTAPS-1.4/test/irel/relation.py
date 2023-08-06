from itaps import iBase, iMesh, iGeom, iRel
from .. import testhelper as unittest
import numpy

# TODO: test changeType and changeStatus
class TestRelation(unittest.TestCase):
    def setUp(self):
        self.mesh = iMesh.Mesh()
        self.geom = iGeom.Geom()
        self.rel  = iRel.Rel()

        self.mesh_ents = self.mesh.createVtx([[0, 0, 0]]*3)
        self.mesh_ent  = self.mesh_ents[0]
        self.geom_ent  = self.geom.createBrick(2, 2, 2)
        self.geom_ents = self.geom.getEntities(iBase.Type.vertex)[0:3]

        self.mesh_sets = iBase.Array([ self.mesh.createEntSet(False),
                                       self.mesh.createEntSet(False),
                                       self.mesh.createEntSet(False) ])
        self.mesh_set = self.mesh_sets[0]
        self.geom_sets = iBase.Array([ self.geom.createEntSet(False),
                                       self.geom.createEntSet(False),
                                       self.geom.createEntSet(False) ])
        self.geom_set = self.geom_sets[0]        

    def tearDown(self):
        self.geom.deleteAll()

    def helpTestEqual(self, pair, left, right):
        if isinstance(left, numpy.ndarray):
            self.assertArray(pair.left[left], right)
            self.assertArray(pair.right[right], left)
        else:
            self.assertEqual(pair.left[left], right)
            self.assertEqual(pair.right[right], left)

    def helpTestMissing(self, pair, left, right):
        self.assertRaises(iBase.TagNotFoundError,
                          lambda: pair.left[left])
        self.assertRaises(iBase.TagNotFoundError,
                          lambda: pair.right[right])

    def testEntEntRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.entity,
                                   self.geom, iRel.Type.entity)

        pair.relate(self.mesh_ent, self.geom_ent)
        self.helpTestEqual(pair, self.mesh_ent, self.geom_ent)
        del pair.left[self.mesh_ent]
        self.helpTestMissing(pair, self.mesh_ent, self.geom_ent)

        pair.left[self.mesh_ent] = self.geom_ent
        self.helpTestEqual(pair, self.mesh_ent, self.geom_ent)
        del pair.right[self.geom_ent]
        self.helpTestMissing(pair, self.mesh_ent, self.geom_ent)

        pair.right[self.geom_ent] = self.mesh_ent
        self.helpTestEqual(pair, self.mesh_ent, self.geom_ent)

    def testEntArrEntArrRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.entity,
                                   self.geom, iRel.Type.entity)

        pair.relate(self.mesh_ents, self.geom_ents)
        self.helpTestEqual(pair, self.mesh_ents, self.geom_ents)
        del pair.left[self.mesh_ents]
        self.helpTestMissing(pair, self.mesh_ents, self.geom_ents)

        pair.left[self.mesh_ents] = self.geom_ents
        self.helpTestEqual(pair, self.mesh_ents, self.geom_ents)
        del pair.right[self.geom_ents]
        self.helpTestMissing(pair, self.mesh_ents, self.geom_ents)

        pair.right[self.geom_ents] = self.mesh_ents
        self.helpTestEqual(pair, self.mesh_ents, self.geom_ents)

    def testEntSetRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.entity,
                                   self.geom, iRel.Type.set)

        pair.relate(self.mesh_ent, self.geom_set)
        self.helpTestEqual(pair, self.mesh_ent, self.geom_set)
        del pair.left[self.mesh_ent]
        self.helpTestMissing(pair, self.mesh_ent, self.geom_set)

        pair.left[self.mesh_ent] = self.geom_set
        self.helpTestEqual(pair, self.mesh_ent, self.geom_set)
        del pair.right[self.geom_set]
        self.helpTestMissing(pair, self.mesh_ent, self.geom_set)

        pair.right[self.geom_set] = self.mesh_ent
        self.helpTestEqual(pair, self.mesh_ent, self.geom_set)

    def testEntArrSetArrRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.entity,
                                   self.geom, iRel.Type.set)

        pair.relate(self.mesh_ents, self.geom_sets)
        self.helpTestEqual(pair, self.mesh_ents, self.geom_sets)
        del pair.left[self.mesh_ents]
        self.helpTestMissing(pair, self.mesh_ents, self.geom_sets)

        pair.left[self.mesh_ents] = self.geom_sets
        self.helpTestEqual(pair, self.mesh_ents, self.geom_sets)
        del pair.right[self.geom_sets]
        self.helpTestMissing(pair, self.mesh_ents, self.geom_sets)

        pair.right[self.geom_sets] = self.mesh_ents
        self.helpTestEqual(pair, self.mesh_ents, self.geom_sets)

    def testSetEntRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.set,
                                   self.geom, iRel.Type.entity)

        pair.relate(self.mesh_set, self.geom_ent)
        self.helpTestEqual(pair, self.mesh_set, self.geom_ent)
        del pair.left[self.mesh_set]
        self.helpTestMissing(pair, self.mesh_set, self.geom_ent)

        pair.left[self.mesh_set] = self.geom_ent
        self.helpTestEqual(pair, self.mesh_set, self.geom_ent)
        del pair.right[self.geom_ent]
        self.helpTestMissing(pair, self.mesh_set, self.geom_ent)

        pair.right[self.geom_ent] = self.mesh_set
        self.helpTestEqual(pair, self.mesh_set, self.geom_ent)

    def testSetArrEntArrRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.set,
                                   self.geom, iRel.Type.entity)

        pair.relate(self.mesh_sets, self.geom_ents)
        self.helpTestEqual(pair, self.mesh_sets, self.geom_ents)
        del pair.left[self.mesh_sets]
        self.helpTestMissing(pair, self.mesh_sets, self.geom_ents)

        pair.left[self.mesh_sets] = self.geom_ents
        self.helpTestEqual(pair, self.mesh_sets, self.geom_ents)
        del pair.right[self.geom_ents]
        self.helpTestMissing(pair, self.mesh_sets, self.geom_ents)

        pair.right[self.geom_ents] = self.mesh_sets
        self.helpTestEqual(pair, self.mesh_sets, self.geom_ents)

    def testSetSetRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.set,
                                   self.geom, iRel.Type.set)

        pair.relate(self.mesh_set, self.geom_set)
        self.helpTestEqual(pair, self.mesh_set, self.geom_set)
        del pair.left[self.mesh_set]
        self.helpTestMissing(pair, self.mesh_set, self.geom_set)

        pair.left[self.mesh_set] = self.geom_set
        self.helpTestEqual(pair, self.mesh_set, self.geom_set)
        del pair.right[self.geom_set]
        self.helpTestMissing(pair, self.mesh_set, self.geom_set)

        pair.right[self.geom_set] = self.mesh_set
        self.helpTestEqual(pair, self.mesh_set, self.geom_set)

    def testSetArrSetArrRel(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.set,
                                   self.geom, iRel.Type.set)

        pair.relate(self.mesh_sets, self.geom_sets)
        self.helpTestEqual(pair, self.mesh_sets, self.geom_sets)
        del pair.left[self.mesh_sets]
        self.helpTestMissing(pair, self.mesh_sets, self.geom_sets)

        pair.left[self.mesh_sets] = self.geom_sets
        self.helpTestEqual(pair, self.mesh_sets, self.geom_sets)
        del pair.right[self.geom_sets]
        self.helpTestMissing(pair, self.mesh_sets, self.geom_sets)

        pair.right[self.geom_sets] = self.mesh_sets
        self.helpTestEqual(pair, self.mesh_sets, self.geom_sets)

    def testInfer(self):
        pass

    def testInferAll(self):
        pair = self.rel.createPair(self.mesh, iRel.Type.entity,
                                   self.geom, iRel.Type.entity)

        self.geom.createBrick(2, 2, 2)
        geom_verts = self.geom.getEntities(iBase.Type.vertex)
        coords = self.geom.getVtxCoords(geom_verts)
        mesh_verts = self.mesh.createVtx(coords)

        pair.inferAllRelations()
