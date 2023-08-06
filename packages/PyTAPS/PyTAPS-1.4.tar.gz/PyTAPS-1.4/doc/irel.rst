================
 iRel Interface
================

.. module:: itaps.iRel
   :synopsis: Basic services to relate entities and sets in pairs of interfaces.

Rel
===

.. autoclass:: Rel([options])

   .. automethod:: createPair(left, left_type[, left_status], right, right_type[, right_status])
   .. automethod:: destroyPair(pair)
   .. automethod:: findPairs(interface)

Pair
====

.. autoclass:: Pair

   .. autoattribute:: instance
   .. autoattribute:: left
   .. autoattribute:: right
   .. automethod:: relate(left, right)
   .. automethod:: inferAllRelations()

PairSide
========

.. autoclass:: PairSide

   .. describe:: side[entities]

      Get the related entities for an entity, entity set, or array of entities.

   .. describe:: side[entities1] = entities2

      Set the related entities for an entity, entity set, or array of entities
      to `entities2`.

   .. describe:: del side[entities]

      Remove the relation data for an entity, entity set, or array of entities.

   .. autoattribute:: instance
   .. autoattribute:: type
   .. autoattribute:: status
   .. automethod:: get(entities[, out])
   .. automethod:: inferRelations(entities)

Enumerations
============

.. class:: Type

   An enumeration of relation types corresponding to ``iRel_RelationType``.

   .. data:: entity

      The relation relates entities on this side to/from the other side.

   .. data:: set

      The relation relates sets on this side to/from the other side.

   .. data:: both

      The relation relates sets on this side to/from the other side,
      and entities to (not from) the other side.

.. class:: Status

   An enumeration of relation statuses corresponding to ``iRel_RelationStatus``.

   .. data:: active

      The relation on this side is active and up to date.

   .. data:: inactive

      The relation on this side is inactive, and may be out of date.

   .. data:: notexist

      The relation on this side is not stored.
