from itaps import iBase, iMesh
from .. import testhelper as unittest
import numpy

class TestTags(unittest.TestCase):
    def setUp(self):
        self.mesh = iMesh.Mesh()

        self.btag = self.mesh.createTag('byte',   1, 'b')
        self.itag = self.mesh.createTag('int',    1, 'i')
        self.dtag = self.mesh.createTag('double', 1, 'd')
        self.etag = self.mesh.createTag('handle', 1, 'E')
        self.stag = self.mesh.createTag('set',    1, 'S')

        self.b3tag = self.mesh.createTag('byte3',   3, 'b')
        self.i3tag = self.mesh.createTag('int3',    3, 'i')
        self.d3tag = self.mesh.createTag('double3', 3, 'd')
        self.e3tag = self.mesh.createTag('handle3', 3, 'E')
        self.s3tag = self.mesh.createTag('set3',    3, 'S')

        self.ents = self.mesh.createVtx([[1,2,3], [4,5,6], [7,8,9]])
        self.ent  = self.mesh.createVtx([1,2,3])
        self.set  = self.mesh.createEntSet(True)
        self.sets = [self.set, self.set, self.set]

    def testCreation(self):
        self.assertEqual(self.btag.instance, self.mesh)
        self.assertEqual(self.btag.name, 'byte')
        self.assertEqual(self.btag.type, 'b')
        self.assertEqual(self.btag.sizeValues, 1)
        self.assertEqual(self.btag.sizeBytes, 1)

        self.assertEqual(self.itag.instance, self.mesh)
        self.assertEqual(self.itag.name, 'int')
        self.assertEqual(self.itag.type, 'i')
        self.assertEqual(self.itag.sizeValues, 1)

        self.assertEqual(self.dtag.instance, self.mesh)
        self.assertEqual(self.dtag.name, 'double')
        self.assertEqual(self.dtag.type, 'd')
        self.assertEqual(self.dtag.sizeValues, 1)
        self.assertEqual(self.dtag.sizeBytes, 8)

        self.assertEqual(self.etag.instance, self.mesh)
        self.assertEqual(self.etag.name, 'handle')
        self.assertEqual(self.etag.type, 'E')
        self.assertEqual(self.etag.sizeValues, 1)

        self.assertEqual(self.stag.instance, self.mesh)
        self.assertEqual(self.stag.name, 'set')
        self.assertEqual(self.stag.type, 'S')
        self.assertEqual(self.stag.sizeValues, 1)

    def testAlternate(self):
        btag = self.mesh.createTag('byte_',   1, numpy.byte)
        itag = self.mesh.createTag('int_',    1, int)
        dtag = self.mesh.createTag('double_', 1, float)
        etag = self.mesh.createTag('handle_', 1, iBase.Entity)
        stag = self.mesh.createTag('set_',    1, iBase.EntitySet)

        self.assertEqual(btag.type, 'b')
        self.assertEqual(itag.type, 'i')
        self.assertEqual(dtag.type, 'd')
        self.assertEqual(etag.type, 'E')
        self.assertEqual(stag.type, 'S')

    def testDestruction(self):
        self.mesh.destroyTag(self.itag, True)
        self.assertRaises(iBase.TagNotFoundError, self.mesh.getTagHandle, 'int')

    def testFind(self):
        t = self.mesh.getTagHandle('int')
        self.assertEqual(t.name, self.itag.name)

        self.assertRaises(iBase.TagNotFoundError, self.mesh.getTagHandle,
                          'potato')


    def testRawData(self):
        self.btag[self.ent] = 42
        self.assertEqual(self.btag[self.ent], 42)

        del self.btag[self.ent]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.btag[self.ent])

    def testIntData(self):
        self.itag[self.ent] = 42

        self.assertEqual(self.itag[self.ent], 42)

        del self.itag[self.ent]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.itag[self.ent])

    def testDblData(self):
        self.dtag[self.ent] = 42

        self.assertEqual(self.dtag[self.ent], 42)

        del self.dtag[self.ent]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.dtag[self.ent])

    def testEHData(self):
        self.etag[self.ent] = self.ent

        self.assertEqual(self.etag[self.ent], self.ent)

        del self.etag[self.ent]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.etag[self.ent])

    def testESHData(self):
        self.stag[self.ent] = self.set

        self.assertEqual(self.stag[self.ent], self.set)

        del self.stag[self.ent]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.stag[self.ent])


    def testRawArrData(self):
        self.b3tag[self.ent] = [42]*3
        self.assertArray(self.b3tag[self.ent], [42]*3)

        del self.b3tag[self.ent]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.b3tag[self.ent])

    def testIntArrData(self):
        self.i3tag[self.ent] = [42]*3
        self.assertArray(self.i3tag[self.ent], [42]*3)

        del self.i3tag[self.ent]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.i3tag[self.ent])

    def testDblArrData(self):
        self.d3tag[self.ent] = [42]*3
        self.assertArray(self.d3tag[self.ent], [42]*3)

        del self.d3tag[self.ent]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.d3tag[self.ent])

    def testEHArrData(self):
        self.e3tag[self.ent] = [self.ent]*3
        self.assertArray(self.e3tag[self.ent], [self.ent]*3)

        del self.e3tag[self.ent]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.e3tag[self.ent])

    def testESHArrData(self):
        self.s3tag[self.ent] = [self.set]*3
        self.assertArray(self.s3tag[self.ent], [self.set]*3)

        del self.s3tag[self.ent]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.s3tag[self.ent])


    def testArrRawData(self):
        self.btag[self.ents] = [42]*3
        self.assertArray(self.btag[self.ents], [42]*3)
        self.assertEqual(self.btag[self.ents[0]], 42)

        del self.btag[self.ents]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.btag[self.ents])

    def testArrIntData(self):
        self.itag[self.ents] = [42]*3
        self.assertArray(self.itag[self.ents], [42]*3)
        self.assertEqual(self.itag[self.ents[0]], 42)

        del self.itag[self.ents]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.itag[self.ents])

    def testArrDblData(self):
        self.dtag[self.ents] = [42]*3
        self.assertArray(self.dtag[self.ents], [42]*3)
        self.assertEqual(self.dtag[self.ents[0]], 42)

        del self.dtag[self.ents]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.dtag[self.ents])

    def testArrEHData(self):
        self.etag[self.ents] = self.ents
        self.assertArray(self.etag[self.ents], self.ents)
        self.assertEqual(self.etag[self.ents[0]], self.ents[0])

        del self.etag[self.ents]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.etag[self.ents])

    def testArrESHData(self):
        self.stag[self.ents] = self.sets
        self.assertArray(self.stag[self.ents], self.sets)
        self.assertEqual(self.stag[self.ents[0]], self.sets[0])

        del self.stag[self.ents]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.stag[self.ents])


    def testArrRawArrData(self):
        self.b3tag[self.ents] = [[1,2,3]]*3
        self.assertArray(self.b3tag[self.ents], [[1,2,3]]*3)
        self.assertArray(self.b3tag[self.ents[0]], [1,2,3])

        del self.b3tag[self.ents]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.b3tag[self.ents])

    def testArrIntArrData(self):
        self.i3tag[self.ents] = [[1,2,3]]*3
        self.assertArray(self.i3tag[self.ents], [[1,2,3]]*3)
        self.assertArray(self.i3tag[self.ents[0]], [1,2,3])

        del self.i3tag[self.ents]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.i3tag[self.ents])

    def testArrDblArrData(self):
        self.d3tag[self.ents] = [[1,2,3]]*3
        self.assertArray(self.d3tag[self.ents], [[1,2,3]]*3)
        self.assertArray(self.d3tag[self.ents[0]], [1,2,3])

        del self.d3tag[self.ents]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.d3tag[self.ents])

    def testArrEHArrData(self):
        data = numpy.tile(self.ents, (3, 1))

        self.e3tag[self.ents] = data
        self.assertArray(self.e3tag[self.ents], data)
        self.assertArray(self.e3tag[self.ents[0]], self.ents)

        del self.e3tag[self.ents]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.e3tag[self.ents])

    def testArrESHArrData(self):
        data = numpy.tile(self.sets, (3, 1))

        self.s3tag[self.ents] = data
        self.assertArray(self.s3tag[self.ents], data)
        self.assertArray(self.s3tag[self.ents[0]], self.sets)

        del self.s3tag[self.ents]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.s3tag[self.ents])


    def testSetRawData(self):
        self.btag[self.set] = 42
        self.assertEqual(self.btag[self.set], 42)

        del self.btag[self.set]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.btag[self.set])

    def testSetIntData(self):
        self.itag[self.set] = 42
        self.assertEqual(self.itag[self.set], 42)

        del self.itag[self.set]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.itag[self.set])

    def testSetDblData(self):
        self.dtag[self.set] = 42
        self.assertEqual(self.dtag[self.set], 42)

        del self.dtag[self.set]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.dtag[self.set])
        
    def testSetEHData(self):
        self.etag[self.set] = self.ent
        self.assertEqual(self.etag[self.set], self.ent)

        del self.etag[self.set]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.etag[self.set])

    def testSetESHData(self):
        self.stag[self.set] = self.set
        self.assertEqual(self.stag[self.set], self.set)

        del self.stag[self.set]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.stag[self.set])


    def testSetRawArrData(self):
        self.b3tag[self.set] = [42]*3
        self.assertArray(self.b3tag[self.set], [42]*3)

        del self.b3tag[self.set]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.b3tag[self.set])

    def testSetIntArrData(self):
        self.i3tag[self.set] = [42]*3
        self.assertArray(self.i3tag[self.set], [42]*3)

        del self.i3tag[self.set]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.i3tag[self.set])

    def testSetDblArrData(self):
        self.d3tag[self.set] = [42]*3
        self.assertArray(self.d3tag[self.set], [42]*3)

        del self.d3tag[self.set]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.d3tag[self.set])
        
    def testSetEHArrData(self):
        self.e3tag[self.set] = [self.ent]*3
        self.assertArray(self.e3tag[self.set], [self.ent]*3)

        del self.e3tag[self.set]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.e3tag[self.set])

    def testSetESHArrData(self):
        self.s3tag[self.set] = [self.set]*3
        self.assertArray(self.s3tag[self.set], [self.set]*3)

        del self.s3tag[self.set]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.s3tag[self.set])


    def testRootSetRawData(self):
        self.btag[self.mesh] = 42
        self.assertEqual(self.btag[self.mesh], 42)

        del self.btag[self.mesh]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.btag[self.mesh])

    def testRootSetIntData(self):
        self.itag[self.mesh] = 42
        self.assertEqual(self.itag[self.mesh], 42)

        del self.itag[self.mesh]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.itag[self.mesh])

    def testRootSetDblData(self):
        self.dtag[self.mesh] = 42
        self.assertEqual(self.dtag[self.mesh], 42)

        del self.dtag[self.mesh]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.dtag[self.mesh])
        
    def testRootSetEHData(self):
        self.etag[self.mesh] = self.ent
        self.assertEqual(self.etag[self.mesh], self.ent)

        del self.etag[self.mesh]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.etag[self.mesh])

    def testRootSetESHData(self):
        self.stag[self.mesh] = self.set
        self.assertEqual(self.stag[self.mesh], self.set)

        del self.stag[self.mesh]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.stag[self.mesh])


    def testRootSetRawArrData(self):
        self.b3tag[self.mesh] = [42]*3
        self.assertArray(self.b3tag[self.mesh], [42]*3)

        del self.b3tag[self.mesh]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.b3tag[self.mesh])

    def testRootSetIntArrData(self):
        self.i3tag[self.mesh] = [42]*3
        self.assertArray(self.i3tag[self.mesh], [42]*3)

        del self.i3tag[self.mesh]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.i3tag[self.mesh])

    def testRootSetDblArrData(self):
        self.d3tag[self.mesh] = [42]*3
        self.assertArray(self.d3tag[self.mesh], [42]*3)

        del self.d3tag[self.mesh]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.d3tag[self.mesh])
        
    def testRootSetEHArrData(self):
        self.e3tag[self.mesh] = [self.ent]*3
        self.assertArray(self.e3tag[self.mesh], [self.ent]*3)

        del self.e3tag[self.mesh]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.e3tag[self.mesh])

    def testRootSetESHArrData(self):
        self.s3tag[self.mesh] = [self.set]*3
        self.assertArray(self.s3tag[self.mesh], [self.set]*3)

        del self.s3tag[self.mesh]
        self.assertRaises(iBase.TagNotFoundError, lambda: self.s3tag[self.mesh])


    def testGetAll(self):
        self.itag[self.ent] = 42
        self.dtag[self.ent] = 42

        self.assertArraySorted(self.mesh.getAllTags(self.ent),
                               iBase.Array([self.itag, self.dtag]))

    def testSetGetAll(self):
        self.itag[self.set] = 42
        self.dtag[self.set] = 42

        self.assertArraySorted(self.mesh.getAllTags(self.set),
                               iBase.Array([self.itag, self.dtag]))
