================================
 A Gentle Introduction to iGeom
================================

:mod:`~itaps.iGeom` is an interface for working with continuous geometry (e.g.
CAD files). Geometries are composed of sets of entities, such as vertices,
edges, faces or volumes, with tags associated with these entities or sets.
Below, we'll go through some of the basics of working with the iGeom interface
to query and manipulate geometric data.

"Hello, World!"
===============

To illustrate the most basic usage of iGeom, let's start with a simple "Hello,
world!" script, run from the interactive shell. If you've read :doc:`imesh`,
this should be eerily familiar to you. To recap, we'll just load a file and
print out how many entities are contained in that file::

    >>> from itaps import iBase, iGeom
    >>> geom = iGeom.Geom()
    >>> geom.load("geom.cub")
    >>> geom.getNumOfType(iBase.Type.all)
    256

This simple script contains the basic elements that we'll see in most PyTAPS
programs: we import the :mod:`~itaps.iBase` and :mod:`~itaps.iGeom` modules,
create a :class:`~itaps.iGeom.Geom` instance, and then do some work with that
instance.

Creating Entities
=================

Sometimes, we'll also want to create new entities in our geometry. iGeom
supports creation of a variety of primitive geometric types. Let's try creating
a cube of side length 1 (a "brick")::

    >>> from itaps import iBase, iGeom
    >>> geom = iGeom.Geom()
    >>> brick = geom.createBrick(1, 1, 1)
    >>> print geom.getNumOfType(iBase.Type.all)
    27

Notice that even though we only created one entity, iGeom reports that we now
have 27 entities in our geometry. This is because iGeom implicitly creates the
necessary lower-dimensional entities (1 volume + 6 faces + 12 edges + 8 vertices
= 27 entities).

.. note::
   For a full list of the creation methods supported in iGeom, consult
   :ref:`Creation Methods <igeom-creation>`.

Getting Entity Data
===================

Continuing from above, we have a brick in our geometry, but where did iGeom put
it? To determine this, we can print out the coordinates of its vertices::

    >>> verts = geom.getEntAdj(brick, iBase.Type.vertex)
    >>> coords = geom.getVtxCoords(verts)
    >>> for i in coords:
    ...     print i
    ... 
    [ 0.5 -0.5  0.5]
    [ 0.5  0.5  0.5]
    [-0.5  0.5  0.5]
    [-0.5 -0.5  0.5]
    [ 0.5  0.5 -0.5]
    [ 0.5 -0.5 -0.5]
    [-0.5 -0.5 -0.5]
    [-0.5  0.5 -0.5]

From this, we can see that the brick is centered at the origin. To figure this
out, we first had to get the vertices adjacent to the brick and then get the
coordinates of those vertices.

Transforming Entities
=====================

As we saw above, our brick was created at the origin. In fact, this is the case
for all the various creation methods. In order to center the brick on some other
coordinate, we need to transform the entity::

    >>> geom.moveEnt(brick, [0.5, 0.5, 0.5])
    >>> coords = geom.getVtxCoords(verts)
    >>> for i in coords:
    ...     print i
    ... 
    [ 1.  0.  1.]
    [ 1.  1.  1.]
    [ 0.  1.  1.]
    [ 0.  0.  1.]
    [ 1.  1.  0.]
    [ 1.  0.  0.]
    [ 0.  0.  0.]
    [ 0.  1.  0.]

.. note::
   For a full list of the transformation methods supported in iGeom, consult
   :ref:`Transformation Methods <igeom-transformation>`.

Working With Arrays
===================

Many iGeom functions accept either single values for arguments or arrays of
values. In general, the same function is used in both cases; we've already seen
this work with :meth:`~itaps.iGeom.Geom.getVtxCoords` above. In this case, the
function returns an array of the results and is equivalent to (except 
:meth:`~itaps.iGeom.Geom.getVtxCoords` returns a NumPy array instead of a
list)::

    coords = []
    for v in verts:
        coords.append(geom.getVtxCoords(v))

However, when using :meth:`~itaps.iGeom.Geom.getEntAdj` above, you may have
noticed that we passed in a single entity and got back an array of entities. 
hen what happens if we pass in an array of entities? Does it return an array of
arrays? Well, not quite. In fact, when called with an array of entities as
input, :meth:`~itaps.iGeom.Geom.getEntAdj` returns an
:class:`~itaps.helpers.OffsetListSingle` instance.

Offset lists are jagged 2-dimensional arrays implemented as a 1-D array of data
and an array of offsets into that data. However, most of the time we can just
treat these as jagged arrays::

    >>> from itaps import iBase, iGeom
    >>> geom = iGeom.Geom()
    >>> brick = geom.createBrick(1, 1, 1)
    >>> geom.moveEnt(brick, [0.5, 0.5, 0.5])
    >>> faces = geom.getEntAdj(brick, iBase.Type.face)
    >>> verts = geom.getEntAdj(faces, iBase.Type.vertex)
    >>> for v in verts:
    ...     print geom.getVtxCoords(v).tolist()
    ... 
    [[1.0, 0.0, 1.0], [1.0, 1.0, 1.0], [0.0, 1.0, 1.0], [0.0, 0.0, 1.0]]
    [[1.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    [[0.0, 0.0, 1.0], [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 1.0]]
    [[0.0, 1.0, 1.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.0]]
    [[1.0, 1.0, 1.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0]]
    [[1.0, 0.0, 1.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]]

Sets and Tags
=============

To learn about how to work with sets and tags, continue on to :doc:`sets-tags`.

