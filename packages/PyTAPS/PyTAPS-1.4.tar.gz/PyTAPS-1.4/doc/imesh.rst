=================
 iMesh Interface
=================

.. module:: itaps.iMesh
   :synopsis: Basic services to manage a discrete mesh composed of sets of
              entities.

Mesh
====

.. autoclass:: Mesh([options])

   .. autoattribute:: rootSet
   .. autoattribute:: geometricDimension
   .. autoattribute:: defaultStorage
   .. autoattribute:: adjTable
   .. automethod:: optimize()
   .. automethod:: createVtx(coords[, storage_order, out])
   .. automethod:: createEnt(topo, entities)
   .. automethod:: createEntArr(topo, entities[, out])
   .. automethod:: deleteEnt(entities)
   .. automethod:: getVtxCoords(entities[, storage_order, out])
   .. automethod:: setVtxCoords(entities, coords[, storage_order, out])
   .. automethod:: getEntType(entities[, out])
   .. automethod:: getEntTopo(entities[, out])
   .. automethod:: getEntAdj(entities, type[, out])
   .. automethod:: getEnt2ndAdj(entities, bridge_type, type[, out])
   .. automethod:: createEntSet(ordered)
   .. automethod:: destroyEntSet(set)
   .. automethod:: createTag(name, size, type)
   .. automethod:: destroyTag(tag, force)
   .. automethod:: getTagHandle(name)
   .. automethod:: getAllTags(entities[, out])

Forwarding
----------

In addition to the methods listed above, :class:`Mesh` automatically forwards
method calls to the root :class:`EntitySet`. Thus, ::

  mesh.getEntities(iBase.Type.all, iMesh.Topology.all)

is equivalent to::

  mesh.rootSet.getEntities(iBase.Type.all, iMesh.Topology.all)

EntitySet
=========

.. autoclass:: EntitySet(set[, instance])

   .. describe:: len(entset)

      Return the number of entities in the entity set. Equivalent to
      ``entset.getNumOfType(iBase.Type.all)``.

   .. describe:: iter(entset)

      Return an iterator over the elements in the entity set. Equivalent to
      ``entset.iterate()``.

   .. autoattribute:: instance
   .. autoattribute:: isList
   .. automethod:: load(filename[, options])
   .. automethod:: save(filename[, options])
   .. automethod:: getNumOfType(type)
   .. automethod:: getNumOfTopo(topo)
   .. automethod:: getEntities([type=iBase.Type.all, topo=iMesh.Topology.all, out])
   .. automethod:: getAdjEntIndices(type, topo, adj_type)
   .. automethod:: getNumEntSets([hops=-1])
   .. automethod:: getEntSets([hops=-1, out])
   .. automethod:: add(entities)
   .. automethod:: remove(entities)
   .. automethod:: contains(entities)
   .. automethod:: isChild(set)
   .. automethod:: getNumChildren([hops=-1])
   .. automethod:: getNumParents([hops=-1])
   .. automethod:: getChildren([hops=-1, out])
   .. automethod:: getParents([hops=-1, out])
   .. automethod:: addChild(set)
   .. automethod:: removeChild(set)
   .. automethod:: iterate([type=iBase.Type.all, topo=iMesh.Topology.all, count=1])
   .. automethod:: difference(set)
   .. automethod:: intersection(set)
   .. automethod:: union(set)

Iterator
========

.. autoclass:: Iterator(set[,type=iBase.Type.all,topo=iMesh.Topology.all,count=1])

   .. autoattribute:: instance
   .. automethod:: reset()

Tag
===

.. autoclass:: Tag(tag[, instance])

   .. describe:: tag[entities]

      Get the tag data for an entity, entity set, or array of entities.

   .. describe:: tag[entities] = data

      Set the tag data for an entity, entity set, or array of entities to
      `data`.

   .. describe:: del tag[entities]

      Remove the tag data for an entity, entity set, or array of entities.

   .. autoattribute:: instance
   .. autoattribute:: name
   .. autoattribute:: sizeValues
   .. autoattribute:: sizeBytes
   .. autoattribute:: type
   .. automethod:: get(entities[, out])
   .. automethod:: getData(entities)
   .. automethod:: setData(entities, data)
   .. automethod:: remove(entities)

Enumerations
============

.. class:: Topology

   An enumeration of mesh element topologies corresponding to
   ``iMesh_EntityTopology``.

   .. data:: point

      A general zero-dimensional entity

   .. data:: line_segment

      A general one-dimensional entity

   .. data:: polygon

      A general two-dimensional element

   .. data:: triangle

      A three-sided, two-dimensional element

   .. data:: quadrilateral

      A four-sided, two-dimensional element

   .. data:: polyhedron

      A general three-dimensional element

   .. data:: tetrahedron

      A four-sided, three-dimensional element whose faces are triangles

   .. data:: hexahedron

      A six-sided, three-dimensional element whose faces are quadrilaterals

   .. data:: prism

      A five-sided, three-dimensional element which has three quadrilateral
      faces and two triangular faces

   .. data:: pyramid

      A five-sided, three-dimensional element which has one quadrilateral face
      and four triangular faces

   .. data:: septahedron

      A hexahedral entity with one collapsed edge

   .. data:: all

      Allows the user to request information about all the topology types
