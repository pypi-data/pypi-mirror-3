from itaps import iBase, iMesh, iMeshExtensions
from .. import testhelper as unittest

class TestExtensions(unittest.TestCase):
    def setUp(self):
        self.mesh = iMesh.Mesh()

    def testStructuredMesh(self):
        # TODO: make this do more actual testing
        self.mesh.createStructuredMesh([0, 0, -1, 64, 64, -1],
                                       [0, 0, -1, 64, 64, -1],
                                       i=[0],j=[0],k=[0])

    def testIterStep(self):
        ents = self.mesh.createVtx([[0,0,0]]*8)

        iterator = self.mesh.iterate()
        self.assertFalse(iterator.step(4))
        self.assertTrue(iterator.step(4))

        iterator = self.mesh.iterate(size=2)
        self.assertFalse(iterator.step(4))
        self.assertTrue(iterator.step(4))
