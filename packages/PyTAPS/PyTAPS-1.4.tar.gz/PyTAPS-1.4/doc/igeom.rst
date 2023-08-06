=================
 iGeom Interface
=================

.. module:: itaps.iGeom
   :synopsis: Basic services to manage continuous geometry composed of sets of
              entities.

Geom
====

.. autoclass:: Geom([options])

   .. autoattribute:: rootSet
   .. autoattribute:: boundBox
   .. autoattribute:: topoLevel
   .. autoattribute:: parametric
   .. autoattribute:: tolerance
   .. automethod:: load(filename[, options])
   .. automethod:: save(filename[, options])

   .. _igeom-creation:

   .. automethod:: createSphere(radius)
   .. automethod:: createBrick(dimensions)
   .. automethod:: createCylinder(height, major_rad, minor_rad)
   .. automethod:: createPrism(height, sides, major_rad, minor_rad)
   .. automethod:: createCone(height, major_rad, minor_rad, top_rad)
   .. automethod:: createTorus(major_rad, minor_rad)
   .. automethod:: deleteAll()
   .. automethod:: deleteEnt(entity)
   .. automethod:: getVtxCoords(src[, dest, storage_order, out])
   .. automethod:: getEntCoords(coords[, src, dest, storage_order, out])
   .. automethod:: measure(entities[, out])
   .. automethod:: getEntType(entities[, out])
   .. automethod:: getFaceType(entity)
   .. automethod:: isEntParametric(entities[, out])
   .. automethod:: isEntPeriodic(entities[, out])
   .. automethod:: isFcDegenerate(entities[, out])
   .. automethod:: getEntBoundBox(entities[, storage_order, out])
   .. automethod:: getEntRange(entities[, basis, storage_order, out])
   .. automethod:: getEntTolerance(entities[, out])
   .. automethod:: getEntAdj(entities, type[, out])
   .. automethod:: getEnt2ndAdj(entities, bridge_type, type[, out])
   .. automethod:: isEntAdj(entities1, entities2[, out])
   .. automethod:: getEntClosestPt(entities, coords[, storage_order, out])
   .. automethod:: getEntNormal(entities, coords[, basis=Basis.xyz, storage_order, out])
   .. automethod:: getEntNormalPl(entities, coords[, storage_order, out])
   .. automethod:: getEntTangent(entities, coords[, basis=Basis.xyz, storage_order, out])
   .. automethod:: getEntCurvature(entities, coords[, basis=Basis.xyz, type, storage_order, out])
   .. automethod:: getEntEval(entities, coords[, type, storage_order, out])
   .. automethod:: getEnt1stDerivative(entities, coords[, storage_order, out])
   .. automethod:: getEnt2ndDerivative(entities, coords[, storage_order, out])
   .. automethod:: getPtRayIntersect(points, vectors[, storage_order, out])
   .. automethod:: getPtClass(points[, storage_order, out])
   .. automethod:: getEntNormalSense(faces, regions[, out])
   .. automethod:: getEgFcSense(edges, faces[, out])
   .. automethod:: getEgVtxSense(edges, vertices1, vertices2[, out])

   .. _igeom-transformation:

   .. automethod:: copyEnt(entity)
   .. automethod:: moveEnt(entity, direction)
   .. automethod:: rotateEnt(entity, angle, axis)
   .. automethod:: reflectEnt(entity, axis)
   .. automethod:: scaleEnt(entity, scale)
   .. automethod:: sweepEntAboutAxis(entity, angle, axis)
   .. automethod:: uniteEnts(entities)
   .. automethod:: subtractEnts(entity1, entity2)
   .. automethod:: intersectEnts(entity1, entity2)
   .. automethod:: sectionEnt(entity, normal, offest, reverse)
   .. automethod:: imprintEnts(entities)
   .. automethod:: mergeEnts(entities, tolerance)
   .. automethod:: createEntSet(ordered)
   .. automethod:: destroyEntSet(set)
   .. automethod:: createTag(name, size, type)
   .. automethod:: destroyTag(tag, force)
   .. automethod:: getTagHandle(name)
   .. automethod:: getAllTags(entities[, out])

Forwarding
----------

In addition to the methods listed above, :class:`Geom` automatically forwards
method calls to the root :class:`EntitySet`. Thus, ::

  geom.getEntities(iBase.Type.all)

is equivalent to::

  geom.rootSet.getEntities(iBase.Type.all)

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
   .. automethod:: getNumOfType(type)
   .. automethod:: getEntities([type=iBase.Type.all, out])
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
   .. automethod:: iterate([type=iBase.Type.all, count=1])
   .. automethod:: difference(set)
   .. automethod:: intersection(set)
   .. automethod:: union(set)

Iterator
========

.. autoclass:: Iterator(set, [type=iBase.Type.all, count=1])

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

.. class:: Basis

   An enumeration of geometric bases for use in querying different coordinate
   systems.

   .. data:: xyz

      Standard (world-space) coordinates

   .. data:: uv

      Parametric coordinates for two-dimensional objects (faces)

   .. data:: u

      Parametric coordinates for one-dimensional objects (edges)
