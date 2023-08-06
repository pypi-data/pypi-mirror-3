============================
 Working With Sets and Tags
============================

Both iMesh and iGeom make use of sets
(:class:`iMesh.EntitySet <itaps.iMesh.EntitySet>` and :class:`iGeom.EntitySet
<itaps.iGeom.EntitySet>`) to group entities (and other sets) as well as tags
(:class:`iMesh.Tag <itaps.iMesh.Tag>` and :class:`iGeom.Tag <itaps.iGeom.Tag>`)
to store data associated with entities or sets. Though the iMesh interface has
a few added methods to its entity sets, the behavior is largely the same.

Sets
====

Entity sets are arbitrary collections of elements (either entities or other
sets). They can also contain parent-child relationships with other sets. Sets
are an ideal way of storing groups of entities together to represent some
simulation-related information (e.g. using a set to contain the faces making up
the skin of a mesh).

As you might guess, Entity sets share a similar interface as core Python
:class:`sets <set>`.

The Root Set
------------

Meshes and geometries both contain a "root set": an entity set encompassing the
entire instance. All entities and sets are automatically members of this set.
The root set can be accessed explicitly as :data:`Mesh.rootSet
<itaps.iMesh.Mesh.rootSet>` (or :data:`Geom.rootSet <itaps.iGeom.Geom.rootSet>`)
or its methods can be implicitly called on the containing instance::

    >>> from itaps import iBase, iMesh
    >>> mesh = iMesh.Mesh()
    >>> mesh.load("mesh.vtk")
    >>> ents1 = mesh.getEntities()
    >>> ents2 = mesh.rootSet.getEntities()
    >>> (ents1 == ents2).all()
    True

In :doc:`imesh`, we saw the :meth:`~itaps.iMesh.EntitySet.getEntities` method,
but now we can see that this method actually belongs to entity sets. Calling it
from the mesh or geometry instance implicitly forwards these calls to the root
set.

Set Basics
----------

Creating new entity sets and adding elements to them is a simple matter::

    >>> from itaps import iBase, iMesh
    >>> mesh = iMesh.Mesh()
    >>> verts = mesh.createVtx([[0, 0, 0]]*16)
    >>> set1 = mesh.createEntSet(ordered=False)
    >>> set2 = mesh.createEntSet(ordered=False)
    >>> set1.add(verts)
    >>> set1.add(set2)

.. note::
   ITAPS entity sets can be either *ordered* or *unordered*. Ordered sets, as
   the name implies, store their contents in sorted order and don't store
   duplicates. Unordered sets store their contents in the order they were added
   and do store duplicates.

Getting elements back out of a set is similarly easy. We already saw above how
to get entities, and getting entity sets works similarly. When getting
entities, we can also filter the results by :class:`~itaps.iBase.Type` (and
:class:`~itaps.iMesh.Topology` in iMesh)::

    >>> v = set1.getEntities(iBase.Type.vertex)
    >>> (verts == v).all()
    True
    >>> s = set1.getEntSets()
    >>> s in set2
    True

Parent-Child Relationships
--------------------------

In addition to containment, entity sets can contain hierarchical relationships
to other sets in order to provide further structure of mesh/geometry data. This
works in much the same way as ordinary containment, except of course you can
only add relationships between sets::

    >>> from itaps import iBase, iMesh
    >>> mesh = iMesh.Mesh()
    >>> set1 = mesh.createEntSet(False)
    >>> set2 = mesh.createEntSet(False)
    >>> set3 = mesh.createEntSet(False)
    >>> set1.addChild(set2)
    >>> set2.addChild(set3)
    >>> kids = set1.getChildren()
    >>> set2 in kids and set3 in kids
    True
    >>> parents = set2.getParents()
    >>> set1 in parents
    True

You can also specify the maximum number of "hops" between the source set and its
children/parents to return::

    >>> kids = set1.getChildren(1)
    >>> set2 in kids and set3 not in kids
    True

Tags
====

Tags are a way of associating arbitrary data with entities or entity sets. Each
tag stores a fixed number of elements of a particulardata type: :class:`int`,
:class:`float` (C *double*), :class:`~itaps.iBase.Entity`, or
:class:`~numpy.bytes`. Just as entity sets "look like" Python
:class:`sets <set>`, tags look like Python :class:`dicts <dict>`.

Creating Tags
-------------

Creating tags is a straightforward process. Each tag has a string name, a
count of values stored per entity/set, and a data type::

    >>> from itaps import iBase, iMesh
    >>> mesh = iMesh.Mesh()
    >>> tag1 = mesh.createTag("tag1", 1, int)
    >>> tag2 = mesh.createTag("tag2", 3, float)

Getting/Setting Data
--------------------

Once we have some tags, we can get and set the data on particular entities
using a dict-like syntax::

    >>> verts = mesh.createVtx([[0, 0, 0]]*12)
    >>> tag1[verts[0]] = 12
    >>> print tag1[verts[0]]
    12
    >>> tag1[verts] = range(12)
    >>> print tag1[verts]
    [ 0  1  2  3  4  5  6  7  8  9 10 11]

When working with multi-valued tags, we pass in/get back arrays when working
with a single entity, and arrays of arrays when working with multiple entities
at once::

    >>> tag2[verts[0]] = [0, 1, 2]
    >>> print tag2[verts[0]]
    [ 0.  1.  2.]
    >>> tag2[verts] = [[0, 1, 2]]*12
    >>> print tag2[verts]
    [[ 0.  1.  2.]
     [ 0.  1.  2.]
     [ 0.  1.  2.]
     [ 0.  1.  2.]
     [ 0.  1.  2.]
     [ 0.  1.  2.]
     [ 0.  1.  2.]
     [ 0.  1.  2.]
     [ 0.  1.  2.]
     [ 0.  1.  2.]
     [ 0.  1.  2.]
     [ 0.  1.  2.]]

If the tag data on an entity is no longer relevant, we can delete it. However,
this means that attempting to get the data for that entity will fail::

    >>> del tag1[verts[0]]
    >>> tag1[verts[0]]
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    iBase.ITAPSError: iMesh_getArrData: tag not found for tag "tag1".  (MOAB Error Code: MB_TAG_NOT_FOUND)
