================
 PyTAPS Helpers
================

.. module:: itaps.helpers
   :synopsis: Helper classes to simplify common operations.

OffsetList
==========

An :func:`OffsetList` is a multi-dimensional jagged array. The data array is
stored as a one-dimensional array which is then indexed into with an array of
offsets.

For example::

    >>> point = namedtuple('point', 'x y z')
    >>> o = OffsetList([0,2,4], point([1,2,3,4], [5,6,7,8], [9,0,1,2]))
    >>> o
    <itaps.helpers.OffsetListTuple object at 0x7f3d9922b110>
    >>> o[0]
    point(x=[1, 2], y=[5, 6], z=[9, 0])
    >>> o[0,1]
    point(x=2, y=6, z=0)
    >>> o.x
    <itaps.helpers.OffsetListSingle object at 0x7f3d9922b7d0>

.. function:: OffsetList(offsets, data)

   If `data` is a tuple, return a new :class:`OffsetListTuple` instance with the
   specified offsets and data. Otherwise, return a new :class:`OffsetListSingle`
   instance.

.. class:: OffsetListSingle(offsets, data)

   Return a new :class:`OffsetListSingle` with the specified offsets and data.

   .. describe:: len(o)

      Return the number of sub-arrays in the object `o`. Equivalent to
      ``o.length()``.

      :return: The number of sub-arrays

   .. describe:: o[i]

      Return the `i`\ th sub-array of `o`. Equivalent to
      ``o.data[ o.offsets[i]:o.offsets[i+1] ]``.

      :param i: Outer dimension of the list
      :return: The `i`\ th sub-array

   .. describe:: o[i, j]

      Return the element in the `j`\ th position of the `i`\ th sub-array of
      `o`. Equivalent to ``o.data[ o.offsets[i]+j ]``.

      :param i: Outer dimension of the list
      :param j: Index into the `i`\ th array's sub-array
      :return: The `j`\ th element of the `i`\ th sub-array

   .. attribute:: offsets

      Return the raw offset array.

   .. attribute:: data

      Return the raw data array.

   .. method:: length([i])

      Return the number of sub-arrays that are stored in this object.
      If `i` is specified, return the number of elements for the `i`\ th
      sub-array.

      :param i: Index of the sub-array to query
      :return: If `i` is `None`, the number of sub-arrays stored in this
               object. Otherwise, the number of elements for the `i`\ th
               sub-array.


.. class:: OffsetListTuple(offsets, data)

   Return a new :class:`OffsetListTuple` with the specified offsets and data.
   This is a subclass of :class:`OffsetListSingle`. In addition to the methods
   defined in ``OffsetListSingle``, ``OffsetListTuple`` provides the following
   methods.
   
   .. describe:: o.x

      Return a new :class:`OffsetListSingle` with the same offsets as `o` and
      data equal to ``o.data.x``. Equivalent to ``o.slice('x')``. Requires
      Python 2.6+.

      :return: A new :class:`OffsetListSingle`

   .. attribute:: fields

      Return the fields of the namedtuple used by this instance. Requires Python
      2.6+.

   .. method:: slice(field)

      Return a new :class:`OffsetListSingle` derived from this instance. If
      `field` is an integer, set the :class:`OffsetListSingle`\ 's data to
      ``data[field]``. Otherwise, set the data to ``getattr(data, field)``.
      Using non-integer values requires Python 2.6+.

      :return: A new :class:`OffsetListSingle`

   .. describe:: o[i]
                 o[i, j]

      These methods work as in an :class:`OffsetListSingle`, but return a tuple
      (or namedtuple in Python 2.6+) of the requested data.


IndexedList
===========

An :class:`IndexedList` is a multi-dimensional jagged array. The data array is
stored as a one-dimensional array which is then indexed into with an array of
offsets and an array of indices.

For example::

    >>> import numpy
    >>> o = IndexedList(numpy.array([0, 3, 6]),
    ...                 numpy.array([0, 1, 2,
    ...                              1, 2, 3,
    ...                              2, 3, 4]),
    ...                 numpy.array([10, 11, 12, 13, 14]))
    >>> o[0]
    array([10, 11, 12])
    >>> o[0, 1]
    11
    >>> o.indices[0]
    array([0, 1, 2])

.. class:: IndexedList(offsets, indices, data)

   Return a new :class:`IndexedList` with the specified offsets, indices, and
   data.

   .. describe:: len(o)

      Return the number of entities in the object `o`. Equivalent to
      ``o.length()``.

   .. describe:: o[i]

      Return the `i`\ th sub-array of `o`. Equivalent to
      ``o.data[ o.indices[i] ]``.

      :param i: Outer dimension of the list
      :return: The `i`\ th sub-array

      .. note::

         This method relies on the special indexing features of NumPy, namely
         indexing an array with another array.

   .. describe:: o[i, j]

      Return the element in the `j`\ th position of the `i`\ th sub-array of
      `o`. Equivalent to ``o.data[ o.indices[i, j] ]``.

      :param i: Outer dimension of the list
      :param j: Index into the `i`\ th array's sub-array
      :return: The `j`\ th element of the `i`\ th sub-array

   .. attribute:: indices

      Return the offsets and indices as an :class:`OffsetListSingle` instance.

   .. attribute:: data

      Return the raw data array.

   .. method:: length([i])

      Return the number of entities whose adjacencies are stored in this object.
      If `i` is specified, return the number of adjacencies for the `i`\ th
      entity.

      :param i: Index of the entity to query
      :return: If `i` is `None`, the number of entities whose adjacencies
               are stored. Otherwise, the number of adjacencies for the
               `i`\ th entity.
