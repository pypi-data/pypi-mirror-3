==========
iMesh API
==========

.. ctype:: iMesh_Object

   This subtype of :ctype:`iBase_Object` represents an iMesh instance object.

.. ctype:: iMeshIter_Object

   This subtype of :ctype:`PyObject` represents an iMesh iterator object.

.. ctype:: iMeshEntitySet_Object

   This subtype of :ctype:`iBaseEntitySet_Object` represents an iMesh entity set
   object.

.. ctype:: iMeshTag_Object

   This subtype of :ctype:`iBaseTag_Object` represents an iMesh tag object.

.. cvar:: PyTypeObject iMesh_Type

   This instance of :ctype:`PyTypeObject` represents the iMesh instance type.
   This is the same object as :class:`itaps.iMesh.Mesh`.

.. cvar:: PyTypeObject iMeshIter_Type

   This instance of :ctype:`PyTypeObject` represents the iMesh iterator type.
   This is the same object as :class:`itaps.iMesh.Iterator`.

.. cvar:: PyTypeObject iMeshEntitySet_Type

   This instance of :ctype:`PyTypeObject` represents the iMesh entity set type.
   This is the same object as :class:`itaps.iMesh.EntitySet`.

.. cvar:: PyTypeObject iMeshTag_Type

   This instance of :ctype:`PyTypeObject` represents the iMesh tag type. This is
   the same object as :class:`itaps.iMesh.Tag`.

.. cvar:: PyTypeObject CreateEnt_Type

   `(Python 2.6+ only.)` This instance of :ctype:`PyTypeObject` represents the
   named tuple type returned from :meth:`~itaps.iMesh.Mesh.createEnt`. This is
   the same object as :class:`itaps.iMesh.create_ent`.

.. cvar:: PyTypeObject AdjEntIndices_Type

   `(Python 2.6+ only.)` This instance of :ctype:`PyTypeObject` represents the
   named tuple type returned from
   :meth:`~itaps.iMesh.EntitySet.getAdjEntIndices`. This is the same object as
   :class:`itaps.iMesh.adj_ent`.

.. cfunction:: int iMesh_Check(PyObject *p)

   Return true if its argument is a :class:`~itaps.iMesh.Mesh` or a subtype of
   :class:`~itaps.iMesh.Mesh`.

.. cfunction:: int iMeshEntitySet_Check(PyObject *p)

   Return true if its argument is a :class:`~itaps.iMesh.EntitySet` or a subtype
   of :class:`~itaps.iMesh.EntitySet`.

.. cfunction:: int iMeshTag_Check(PyObject *p)

   Return true if its argument is a :class:`~itaps.iMesh.Tag` or a subtype of
   :class:`~itaps.iMesh.Tag`.

.. cfunction:: PyObject* iMeshEntitySet_New()

   Return a new uninitialized :class:`~itaps.iMesh.EntitySet`, or *NULL* on
   failure.

.. cfunction:: PyObject* iMeshTag_New()

   Return a new uninitialized :class:`~itaps.iMesh.Tag`, or *NULL* on failure.

.. cfunction:: PyObject* iMesh_FromInstance(iMesh_Instance instance)

   Return a new (unowned) :class:`~itaps.iMesh.Mesh`, or *NULL* on failure.

.. cfunction:: PyObject* iMeshEntitySet_FromHandle(iMesh_Object *m, iBase_EntitySetHandle h)

   Return a new :class:`itaps.iMesh.EntitySet` from a
   :class:`~itaps.iMesh.Mesh` object and a C ``iBase_EntitySetHandle``, or
   *NULL* on failure.

.. cfunction:: PyObject* iMeshTag_FromHandle(iMesh_Object *m, iBase_TagHandle h)

   Return a new :class:`itaps.iMesh.Tag` from a :class:`~itaps.iMesh.Mesh`
   object and a C ``iBase_TagHandle``, or *NULL* on failure.

.. cfunction:: iMesh_Object* iMeshEntitySet_GetInstance(PyObject *p)

   Attempt to return the  :class:`~itaps.iMesh.Mesh` object of the object *p*.
   If there is an error, an exception is raised and *NULL* is returned.

.. cfunction:: iMesh_Object* iMeshEntitySet_GET_INSTANCE(PyObject *p)

   Return the :class:`~itaps.iMesh.Mesh` object of the object *p*. No error
   checking is performed.

.. cfunction:: iMesh_Object * iMeshTag_GetInstance(PyObject *p)

   Attempt to return the :class:`~itaps.iMesh.Mesh` object of the object *p*.
   If there is an error, an exception is raised and *NULL* is returned.

.. cfunction:: iMesh_Object * iMeshTag_GET_INSTANCE(PyObject *p)

   Return the :class:`~itaps.iMesh.Mesh` object of the object *p*. No error
   checking is performed.

.. cfunction:: int iMeshTopology_Cvt(PyObject *obj, int *val)

   Convert any compatible Python object, *obj*, to a value in the enumeration
   ``iMesh_EntityTopology``. Return *1* on success, and *0* on failure. This
   function can be used with the ``"O&"`` character code in
   :cfunc:`PyArg_ParseTuple` processing.

