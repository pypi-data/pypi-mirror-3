================================
 A Gentle Introduction to iMesh
================================

:mod:`~itaps.iMesh` is an interface for working with discrete
polygonal/polyhedral meshes. Meshes are composed of sets of entities, such as
vertices, edges, faces or volumes, with tags associated with these entities or
sets. Below, we'll go through some of the basics of working with the iMesh
interface to query and manipulate mesh data.

"Hello, World!"
===============

To illustrate the most basic usage of iMesh, let's start with a simple "Hello,
world!" script, run from the interactive shell. Since iMesh isn't a string
processing module, we won't actually print "Hello, world!", but instead we'll
just load a file and print out how many entities are contained in that file::

    >>> from itaps import iBase, iMesh
    >>> mesh = iMesh.Mesh()
    >>> mesh.load("mesh.vtk")
    >>> mesh.getNumOfType(iBase.Type.all)
    256

This simple script contains the basic elements that we'll see in most PyTAPS
programs: we import the :mod:`~itaps.iBase` and :mod:`~itaps.iMesh` modules,
create a :class:`~itaps.iMesh.Mesh` instance, and then do some work with that
instance.

Creating Entities
=================

Oftentimes, we'll also want to create new entities in our mesh. For vertices,
this is about what you'd expect: define the coordinates for the vertex (or an
array of coordinates to create several vertices at once) and then pass them to
:meth:`~itaps.iMesh.Mesh.createVtx`::

    >>> from itaps import iBase, iMesh
    >>> mesh = iMesh.Mesh()
    >>> verts = mesh.createVtx([[0,0,0], [0,0,1], [0,1,1], [0,1,0]])

For higher-dimension entities, like triangles or hexahedra, supply the entity
topology (shape) and the appropriate number of lower-dimension entities to
:meth:`~itaps.iMesh.Mesh.createEnt`. In this case, we're supplying the vertices
we just created, though we could just as well supply edges if we had them::

    >>> quad, status = mesh.createEnt(iMesh.Topology.quadrilateral, verts)
    >>> mesh.getNumOfType(iBase.Type.face)
    1

Getting Entity Data
===================

Continuing from above, we now have a few entities that we can examine. First
we'll try getting the adjacent vertices of the quad we just created::

    >>> adj = mesh.getEntAdj(quad, iBase.Type.vertex)
    >>> (adj == verts).all()
    True

Notice that :meth:`~itaps.iMesh.Mesh.getEntAdj` returns an array of adjacent
entities, and as expected, these are exactly the same as the vertex entities we
created above.

.. note::
   This behavior depends on the adjacent vertices being returned in the same
   order as they were when passed into :meth:`~itaps.iMesh.Mesh.createEnt`.
   This may vary depending on the underlying iMesh implementation.

We can also get the coordinate data from our adjacent vertices, and we notice
that they match up with the coordinates we specified when creating them::

    >>> mesh.getVtxCoords(adj)
    array([[ 0.,  0.,  0.],
           [ 0.,  0.,  1.],
           [ 0.,  1.,  1.],
           [ 0.,  1.,  0.]])

Furthermore, we can get an array of all the entities in our mesh using
:meth:`~itaps.iMesh.EntitySet.getEntities`. If we preferred, we could have
restricted this based on the type (dimension) and/or topology (shape) of the
entities. To confirm that we have the entities we expect, we can check their
dimension and notice that we have four 0-dimensional entities and one
2-dimensional entity::

    >>> ents = mesh.getEntities()
    >>> mesh.getEntType(ents)
    array([0, 0, 0, 0, 2], dtype=int32)

.. note::
   We'll return to :meth:`~itaps.iMesh.EntitySet.getEntities` in
   :doc:`sets-tags` and see what's really happening with this method.

Working With Arrays
===================

Many iMesh functions accept either single values for arguments or arrays of
values. In general, the same function is used in both cases; we've already seen
this work with :meth:`~itaps.iMesh.Mesh.createVtx` above. However, this would be
ambigious with :meth:`~itaps.iMesh.Mesh.createEnt`, so the array form is a
separate function, :meth:`~itaps.iMesh.Mesh.createEntArr`::

    >>> from itaps import iBase, iMesh
    >>> mesh = iMesh.Mesh()
    >>> coords = []
    >>> for i in range(10):
    ...     coords += [[i,0,0], [i,0,1], [i,1,1], [i,1,0]]
    ... 
    >>> verts = mesh.createVtx(coords)
    >>> quads, status = mesh.createEntArr(iMesh.Topology.quadrilateral, verts)
    >>> len(quads)
    10

When using :meth:`~itaps.iMesh.Mesh.getEntAdj` above, you may have noticed that
we passed in a single entity and got back an array of entities. Then what
happens if we pass in an array of entities? Does it return an array of arrays?
Well, not quite. In fact, when called with an array of entities as input,
:meth:`~itaps.iMesh.Mesh.getEntAdj` returns an
:class:`~itaps.helpers.OffsetListSingle` instance.

Offset lists are jagged 2-dimensional arrays implemented as a 1-D array of data
and an array of offsets into that data. However, most of the time we can just
treat these as jagged arrays::

    >>> adj = mesh.getEntAdj(quads, iBase.Type.vertex)
    >>> for i in adj:
    ...     print mesh.getVtxCoords(i).tolist()
    ... 
    [[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 1.0], [0.0, 1.0, 0.0]]
    [[1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 0.0]]
    [[2.0, 0.0, 0.0], [2.0, 0.0, 1.0], [2.0, 1.0, 1.0], [2.0, 1.0, 0.0]]
    [[3.0, 0.0, 0.0], [3.0, 0.0, 1.0], [3.0, 1.0, 1.0], [3.0, 1.0, 0.0]]
    [[4.0, 0.0, 0.0], [4.0, 0.0, 1.0], [4.0, 1.0, 1.0], [4.0, 1.0, 0.0]]
    [[5.0, 0.0, 0.0], [5.0, 0.0, 1.0], [5.0, 1.0, 1.0], [5.0, 1.0, 0.0]]
    [[6.0, 0.0, 0.0], [6.0, 0.0, 1.0], [6.0, 1.0, 1.0], [6.0, 1.0, 0.0]]
    [[7.0, 0.0, 0.0], [7.0, 0.0, 1.0], [7.0, 1.0, 1.0], [7.0, 1.0, 0.0]]
    [[8.0, 0.0, 0.0], [8.0, 0.0, 1.0], [8.0, 1.0, 1.0], [8.0, 1.0, 0.0]]
    [[9.0, 0.0, 0.0], [9.0, 0.0, 1.0], [9.0, 1.0, 1.0], [9.0, 1.0, 0.0]]

Sets and Tags
=============

To learn about how to work with sets and tags, continue on to :doc:`sets-tags`.
