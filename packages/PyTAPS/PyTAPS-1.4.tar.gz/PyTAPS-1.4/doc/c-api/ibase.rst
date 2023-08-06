===========
 iBase API
===========

.. ctype:: iBase_Object

   This subtype of :ctype:`PyObject` represents an iBase instance object (the
   base type from which types like :ctype:`iMesh_Object` are derived).

.. ctype:: iBaseEntity_Object

   This subtype of :ctype:`PyObject` represents an ``iBase_EntityHandle`` in
   Python.

.. ctype:: iBaseEntitySet_Object

   This subtype of :ctype:`PyObject` represents an ``iBase_EntitySetHandle`` in
   Python.

.. ctype:: iBaseTag_Object

   This subtype of :ctype:`PyObject` represents an ``iBase_TagHandle`` in
   Python.

.. ctype:: iBaseArr_Object

   This subtype of :ctype:`PyObject` represents a NumPy array elements with
   a single iBase instance object in common (e.g. if the instance is a
   :class:`~itaps.iMesh.Mesh`, then this object would contain
   :class:`iMesh.EntitySets <itaps.iMesh.EntitySet>` or
   :class:`iMesh.Tags <itaps.iMesh.Tag>`).

.. cvar:: PyTypeObject iBase_Type

   This instance of :ctype:`PyTypeObject` represents the iBase instance type.
   This is the same object as :class:`itaps.iBase.Base`.

.. cvar:: PyTypeObject iBaseEntity_Type

   This instance of :ctype:`PyTypeObject` represents the iBase entity handle
   type. This is the same object as :class:`itaps.iBase.Entity`.

.. cvar:: PyTypeObject iBaseEntitySet_Type

   This instance of :ctype:`PyTypeObject` represents the iBase entity set handle
   type. This is the same object as :class:`itaps.iBase.EntitySet`.

.. cvar:: PyTypeObject iBaseTag_Type

   This instance of :ctype:`PyTypeObject` represents the iBase tag handle type.
   This is the same object as :class:`itaps.iBase.Tag`.

.. cvar:: PyTypeObject iBaseArr_Type

   This instance of :ctype:`PyTypeObject` represents the iBase NumPy array type.
   This is the same object as :class:`itaps.iBase.Array`.

.. cvar:: PyObject *PyExc_ITAPSError

   This instance of :ctype:`PyObject\*` is the exception type for internal ITAPS
   errors. This is the same object as :class:`itaps.iBase.ITAPSError`.

.. cvar:: PyObject **PyExc_Errors

   An array of of :ctype:`PyObject\*`\ s that holds the exception subtypes for
   internal ITAPS errors. The index in this array is equal to the corresponding
   value from :ctype:`iBase_ErrorType` minus 1.

.. cvar:: int NPY_IBASEENT

   The NumPy typenum for arrays of :class:`Entities <itaps.iBase.Entity>`.

.. cvar:: int NPY_IBASEENTSET

   The NumPy typenum for arrays of :class:`EntitySets <itaps.iBase.EntitySet>`.

.. cvar:: int NPY_IBASETAG

   The NumPy typenum for arrays of :class:`Tags <itaps.iBase.Tag>`.

.. cfunction:: int iBase_Check(PyObject *p)

   Return true if its argument is a :class:`~itaps.iBase.Base` or a subtype of
   :class:`~itaps.iBase.Base`.

.. cfunction:: int iBaseEntity_Check(PyObject *p)

   Return true if its argument is an :class:`~itaps.iBase.Entity` or a subtype
   of :class:`~itaps.iBase.Entity`.

.. cfunction:: int iBaseEntitySet_Check(PyObject *p)

   Return true if its argument is an :class:`~itaps.iBase.EntitySet` or a
   subtype of :class:`~itaps.iBase.EntitySet`.

.. cfunction:: int iBaseTag_Check(PyObject *p)

   Return true if its argument is a :class:`~itaps.iBase.Tag` or a subtype of
   :class:`~itaps.iBase.Tag`.

.. cfunction:: PyObject* iBaseEntity_New()

   Return a new uninitialized :class:`~itaps.iBase.Entity`, or *NULL* on
   failure.

.. cfunction:: PyObject* iBaseEntitySet_New()

   Return a new uninitialized :class:`~itaps.iBase.EntitySet`, or *NULL* on
   failure.

.. cfunction:: PyObject* iBaseTag_New()

   Return a new uninitialized :class:`~itaps.iBase.Tag`, or *NULL* on failure.

.. cfunction:: PyObject* iBaseEntity_FromHandle(iBase_EntityHandle h)

   Return a new :class:`~itaps.iBase.Entity` from a C ``iBase_EntityHandle``, or
   *NULL* on failure.

.. cfunction:: PyObject* iBaseEntitySet_FromHandle(iBase_EntitySetHandle h)

   Return a new :class:`~itaps.iBase.EntitySet` from a C
   ``iBase_EntitySetHandle``, or *NULL* on failure.

.. cfunction:: PyObject* iBaseTag_FromHandle(iBase_TagHandle h)

   Return a new :class:`~itaps.iBase.Tag` from a C ``iBase_TagHandle``, or
   *NULL* on failure.

.. cfunction:: iBase_EntityHandle iBaseEntity_GetHandle(PyObject *p)

   Attempt to return the entity handle held by the object. If there is an error,
   *NULL* is returned, and the caller should check ``PyErr_Occurred()`` to find
   out whether there was an error, or whether the value just happened to be
   *NULL*.

.. cfunction:: iBase_EntityHandle iBaseEntity_GET_HANDLE(PyObject *p)

   Return the entity handle of the object *p*. No error checking is performed.

.. cfunction:: iBase_EntitySetHandle iBaseEntitySet_GetHandle(PyObject *p)

   Attempt to return the entity set handle held by the object. If there is an
   error, *NULL* is returned, and the caller should check ``PyErr_Occurred()``
   to find out whether there was an error, or whether the value just happened to
   be *NULL*.

.. cfunction:: iBase_EntitySetHandle iBaseEntitySet_GET_HANDLE(PyObject *p)

   Return the entity set handle of the object *p*. No error checking is
   performed.

.. cfunction:: iBase_TagHandle iBaseTag_GetHandle(PyObject *p)

   Attempt to return the tag handle held by the object. If there is an error,
   *NULL* is returned, and the caller should check ``PyErr_Occurred()`` to find
   out whether there was an error, or whether the value just happened to be
   *NULL*.

.. cfunction:: iBase_TagHandle iBaseTag_GET_HANDLE(PyObject *p)

   Return the tag handle of the object *p*. No error checking is performed.

.. cfunction:: int iBaseType_Cvt(PyObject *o, int *val)

   Convert any compatible Python object, *obj*, to a value in the enumeration
   ``iBase_EntityType``. Return *1* on success, and *0* on failure. This
   function can be used with the ``"O&"`` character code in
   :cfunc:`PyArg_ParseTuple` processing.

.. cfunction:: int iBaseStorageOrder_Cvt(PyObject *obj, int *val)

   Convert any compatible Python object, *obj*, to a value in the enumeration
   ``iBase_StorageOrder``. Return *1* on success, and *0* on failure. This
   function can be used with the ``"O&"`` character code in
   :cfunc:`PyArg_ParseTuple` processing.

.. cfunction:: int iBaseTagType_Cvt(PyObject *obj, int *val)

   Convert any compatible Python object, *obj*, to a value in the enumeration
   ``iBase_TagValueType``. Return *1* on success, and *0* on failure. This
   function can be used with the ``"O&"`` character code in
   :cfunc:`PyArg_ParseTuple` processing.

.. cfunction:: char iBaseTagType_ToChar(enum iBase_TagValueType t)

   Convert a value in the enumeration ``iBase_TagValueType`` to the character
   code used to represent it in Python.

.. cfunction:: int iBaseTagType_ToTypenum(enum iBase_TagValueType t)

   Convert a value in the enumeration ``iBase_TagValueType`` to the
   corresponding NumPy typenum used to represent that value type.
