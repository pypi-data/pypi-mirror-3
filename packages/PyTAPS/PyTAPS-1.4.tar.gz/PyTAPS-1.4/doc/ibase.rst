=================
 iBase Interface
=================

.. module:: itaps.iBase
   :synopsis: Utilities and definitions used in multiple ITAPS core interfaces.

iBase Types
===========

.. class:: ITAPSError

   The exception type used for all internal ITAPS errors.

.. class:: Base

   The base class for all PyTAPS interfaces (e.g. :class:`itaps.iMesh.Mesh`).

.. class:: Entity

   An individual entity from a specific interface.

.. class:: EntitySet

   The base class for all interface-specific entity set types (e.g.
   :class:`itaps.iMesh.EntitySet`).

.. class:: Tag

   The base class for all interface-specific tag types (e.g.
   :class:`itaps.iMesh.Tag`).

Exceptions
==========

.. class:: ITAPSError

   The base exception type used for all internal ITAPS errors.

.. class:: MeshAlreadyLoadedError

   Equivalent to ``iBase_MESH_ALREADY_LOADED``.

.. class:: NoMeshDataError

   Equivalent to ``iBase_NO_MESH_DATA``.

.. class:: FileNotFoundError

   Equivalent to ``iBase_FILE_NOT_FOUND``.

.. class:: FileWriteError

   Equivalent to ``iBase_FILE_WRITE_ERROR``.

.. class:: NilArrayError

   Equivalent to ``iBase_NIL_ARRAY``.

.. class:: ArraySizeError

   Equivalent to ``iBase_BAD_ARRAY_SIZE``.

.. class:: ArrayDimensionError

   Equivalent to ``iBase_BAD_ARRAY_DIMENSION``.

.. class:: EntityHandleError

   Equivalent to ``iBase_INVALID_ENTITY_HANDLE``.

.. class:: EntityCountError

   Equivalent to ``iBase_INVALID_ENTITY_COUNT``.

.. class:: EntityTypeError

   Equivalent to ``iBase_INVALID_ENTITY_TYPE``.

.. class:: EntityTopologyError

   Equivalent to ``iBase_INVALID_ENTITY_TOPOLOGY``.

.. class:: TypeAndTopoError

   Equivalent to ``iBase_BAD_TYPE_AND_TOPO``.

.. class:: EntityCreationError

   Equivalent to ``iBase_ENTITY_CREATION_ERROR``.

.. class:: TagHandleError

   Equivalent to ``iBase_INVALID_TAG_HANDLE``.

.. class:: TagNotFoundError

   Equivalent to ``iBase_TAG_NOT_FOUND``.

.. class:: TagAlreadyExistsError

   Equivalent to ``iBase_TAG_ALREADY_EXISTS``.

.. class:: TagInUseError

   Equivalent to ``iBase_TAG_IN_USE``.

.. class:: EntitySetHandleError

   Equivalent to ``iBase_INVALID_ENTITYSET_HANDLE``.

.. class:: IteratorHandleError

   Equivalent to ``iBase_INVALID_ITERATOR_HANDLE``.

.. class:: ArgumentError

   Equivalent to ``iBase_INVALID_ARGUMENT``.

.. class:: MemoryAllocationError

   Equivalent to ``iBase_MEMORY_ALLOCATION_FAILED``.

.. class:: NotSupportedError

   Equivalent to ``iBase_NOT_SUPPORTED``.

.. class:: UnknownError

   Equivalent to ``iBase_FAILURE``.


Enumerations
============

.. class:: Type

   An enumeration of entity types corresponding to ``iBase_EntityType``.

   .. data:: vertex

      A zero-dimensional entity

   .. data:: edge

      A one-dimensional entity

   .. data:: face

      A two-dimensional entity

   .. data:: region

      A three-dimensional entity

   .. data:: all

      Allows the user to request information about all the types

.. class:: AdjCost

   An enumeration of adjacency costs corresponding to ``iBase_AdjacencyCost``.

   .. data:: unavailable

      Adjacency information not supported

   .. data:: all_order_1

      No more than local mesh traversal required

   .. data:: all_order_logn

      Global tree search

   .. data:: all_order_n

      Global exhaustive search

   .. data:: some_order_1

      Only some adjacency info, local

   .. data:: some_order_logn

      Only some adjacency info, tree

   .. data:: some_order_n

      Only some adjacency info, exhaustive

   .. data:: available

      All intermediate entities available

.. class:: StorageOrder

   An enumeration of storage orders corresponding to ``iBase_StorageOrder``.

   .. data:: interleaved

      Coordinates are interleaved, e.g. ((x\ :sub:`1`\, y\ :sub:`1`\,
      z\ :sub:`1`\), (x\ :sub:`2`\, y\ :sub:`2`\, z\ :sub:`2`\), ...). This is
      the default.

   .. data:: blocked

      Coordinates are blocked, e.g. ((x\ :sub:`1`\, x\ :sub:`2`\, ...),
      (y\ :sub:`1`\, y\ :sub:`2`\, ...), (z\ :sub:`1`\, z\ :sub:`2`\, ...)).

.. class:: CreationStatus

   An enumeration of entity creation statuses corresponding to
   ``iBase_CreationStatus``.

   .. data:: new

      New entity was created

   .. data:: exists

      Entity already exists

   .. data:: duplicated

      Duplicate entity created

   .. data:: failed

      Creation failed
