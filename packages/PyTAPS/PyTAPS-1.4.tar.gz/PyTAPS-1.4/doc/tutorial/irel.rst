===============================
 A Gentle Introduction to iRel
===============================

:mod:`~itaps.iRel` is an interface for relating pairs of entities from other
ITAPS interfaces, e.g. relating :mod:`itaps.iMesh mesh` to :mod:`itaps.iGeom
geometry`. An iRel instance contains a list of pairs of ITAPS interfaces. Each
pair contains relations between entities from each of the interfaces.

Starting Out
============

Before we can get started working with iRel, we'll need to create a mesh and a
geometry with a few entities each::

    >>> from itaps import iMesh, iGeom, iRel
    >>> mesh = iMesh.Mesh()
    >>> geom = iGeom.Geom()
    >>> mesh_ents = mesh.createVtx([[0,0,0], [1,1,1], [2,2,2]])
    >>> geom_ents = [ geom.createBrick(1,1,1),
                      geom.createBrick(1,1,1),
                      geom.createBrick(1,1,1) ]

From here, we can create the iRel instance and a pair relating our newly-created
mesh and geometry::

    >>> rel = iRel.Rel()
    >>> pair = rel.createPair(mesh, iRel.Type.entity, geom, iRel.Type.entity)

These snippets contain the prelude for most PyTAPS programs using iRel: we
import the :mod:`~itaps.iBase`, :mod:`~itaps.iMesh`, :mod:`~itaps.iGeom`, and
:mod:`~itaps.iRel` modules, create (or load) our mesh and geometry, then create
an iRel instance and a relation pair. The relation pair object works like a
bidirectional map, where keys on one side point to values on the other, and
vice-versa. In the examples below, we'll assume that the above snippets have
already been executed.

Setting Relations
=================

There are a few ways to set a relation between a pair of entities. All of the
following are equivalent::

    >>> pair.relate(mesh_ents[0], geom_ents[0])
    >>> pair.left[ mesh_ents[0] ] = geom_ents[0]
    >>> pair.right[ geom_ents[0] ] = mesh_ents[0]

Getting Relations
=================

It's equally straightforward to get a relation if you have one of the related
entities::

    >>> pair.left[ mesh_ents[0] ]
    <itaps.iBase.Entity 0x2b80dc0>
    >>> pair.left[ mesh_ents[0] ] == geom_ents[0]
    True
    >>> pair.right[ geom_ents[0] ]
    <itaps.iBase.Entity 0x1>
    >>> pair.right[ geom_ents[0] ] = mesh_ents[0]


Removing Relations
==================

Naturally, one can delete a relation, too::

    >>> del pair.left[ mesh_ents[0] ]

If we then attempt to retrieve this relation (from either side), we'll get an
exception:

    >>> pair.left[ mesh_ents[0] ]
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    iBase.TagNotFoundError: iMesh_getArrData: tag not foundfor tag "__MESH_ASSOCIATION0".  (MOAB Error Code: MB_TAG_NOT_FOUND)
    >>> pair.right[ geom_ents[0] ]
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    iBase.TagNotFoundError: Tag does not exist
