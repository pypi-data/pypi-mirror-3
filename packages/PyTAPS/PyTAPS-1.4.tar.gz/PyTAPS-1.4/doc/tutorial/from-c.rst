===============
 Coming from C
===============

Compared to the C interface for ITAPS, PyTAPS has some important differences
designed to take advantage of Python language features. Users familiar with the
C interface should review the changes below.

Overloads
=========

To reduce the number of methods that must be memorized when using these
interfaces, PyTAPS coalesces all entity, entity array, and entity set functions
into a single function where appropriate. For instance, the iMesh functions
``iMesh_addEntToSet``, ``iMesh_addEntArrToSet``, and ``iMesh_addEntSet`` are all
called by :meth:`itaps.iMesh.EntitySet.add`. Which C API function is ultimately
called is determined by the type of the argument passed to ``add``.

One notable exception to this rule is :meth:`itaps.iMesh.Mesh.createEnt` and
:meth:`itaps.iMesh.Mesh.createEntArr`, which have the same signatures and so
cannot be overloaded based on the types of the arguments.

Return Values
=============

Instead of relying on out-values to return data from interface functions, PyTAPS
uses the simpler method of merely returning the data. In cases where multiple
return values are needed, PyTAPS returns a tuple of the values (or a namedtuple
in Python 2.6+). As a notable exception to this, return values that contain
offset arrays are wrapped into helper classes, located in :mod:`itaps.helpers`.

Error Handling
==============

All instances of the out-value ``int *err`` in functions have been replaced with
Python ``ITAPSError``\ s that are raised if an error of some kind occurs.

Arrays
======

In the C interface, arrays are passed as pairs of parameters when used as input
(``type *data, int size``) and as triples of parameters when used as output
(``type **data, int *alloc, int *size``). The PyTAPS interface uses `Numpy
<http://numpy.scipy.org/>`_ for all array data, and so the size is passed
implicitly along with the array. Since Python programs (generally) do not
manually manage their own memory, the ``alloc`` parameter is similarly
eliminated.

Storage Order
-------------

By default, PyTAPS uses interleaved storage -- that is, coordinates are arranged
as ((x\ :sub:`1`\, y\ :sub:`1`\, z\ :sub:`1`\), (x\ :sub:`2`\, y\ :sub:`2`\,
z\ :sub:`2`\), ...) -- regardless of the default storage order in the
underlying ITAPS interface. This is done to allow more idiomatic use of arrays
of coordinates in Python.

The *out* Argument
------------------

Most functions that return arrays also accept an optional argument named *out*.
Supply this argument if you'd like to use the memory buffer of another array to
hold the result of the function call.
