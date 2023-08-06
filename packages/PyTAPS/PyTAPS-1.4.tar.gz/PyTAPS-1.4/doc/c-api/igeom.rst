===========
 iGeom API
===========

.. ctype:: iGeom_Object

   This subtype of :ctype:`iBase_Object` represents an iGeom instance object.

.. ctype:: iGeomIter_Object

   This subtype of :ctype:`PyObject` represents an iGeom iterator object.

.. ctype:: iGeomEntitySet_Object

   This subtype of :ctype:`iBaseEntitySet_Object` represents an iGeom entity set
   object.

.. ctype:: iGeomTag_Object

   This subtype of :ctype:`iBaseTag_Object` represents an iGeom tag object.

.. cvar:: PyTypeObject iGeom_Type

   This instance of :ctype:`PyTypeObject` represents the iGeom instance type.
   This is the same object as :class:`itaps.iGeom.Geom`.

.. cvar:: PyTypeObject iGeomIter_Type

   This instance of :ctype:`PyTypeObject` represents the iGeom iterator type.
   This is the same object as :class:`itaps.iGeom.Iterator`.

.. cvar:: PyTypeObject iGeomEntitySet_Type

   This instance of :ctype:`PyTypeObject` represents the iGeom entity set type.
   This is the same object as :class:`itaps.iGeom.EntitySet`.

.. cvar:: PyTypeObject iGeomTag_Type

   This instance of :ctype:`PyTypeObject` represents the iGeom tag type. This is
   the same object as :class:`itaps.iGeom.Tag`.

.. cvar:: PyTypeObject NormalPl_Type

   `(Python 2.6+ only.)` This instance of :ctype:`PyTypeObject` represents the
   named tuple type returned from :meth:`~itaps.iGeom.Geom.getEntNormalPl`. This
   is the same object as :class:`itaps.iGeom.normal_pl`.

.. cvar:: PyTypeObject FaceEval_Type

   `(Python 2.6+ only.)` This instance of :ctype:`PyTypeObject` represents the
   named tuple type returned from :meth:`~itaps.iGeom.Geom.getEntEval` for
   faces. This is the same object as :class:`itaps.iGeom.face_eval`.

.. cvar:: PyTypeObject EdgeEval_Type

   `(Python 2.6+ only.)` This instance of :ctype:`PyTypeObject` represents the
   named tuple type returned from :meth:`~itaps.iGeom.Geom.getEntEval` for
   edges. This is the same object as :class:`itaps.iGeom.edge_eval`.

.. cvar:: PyTypeObject Deriv1st_Type

   `(Python 2.6+ only.)` This instance of :ctype:`PyTypeObject` represents the
   named tuple type returned from :meth:`~itaps.iGeom.Geom.getEnt1stDerivative`
   for edges. This is the same object as :class:`itaps.iGeom.deriv_1st`.

.. cvar:: PyTypeObject Deriv2nd_Type

   `(Python 2.6+ only.)` This instance of :ctype:`PyTypeObject` represents the
   named tuple type returned from :meth:`~itaps.iGeom.Geom.getEnt2ndDerivative`
   for edges. This is the same object as :class:`itaps.iGeom.deriv_2nd`.

.. cvar:: PyTypeObject Intersect_Type

   `(Python 2.6+ only.)` This instance of :ctype:`PyTypeObject` represents the
   named tuple type returned from :meth:`~itaps.iGeom.Geom.getPtRayIntersect`.
   This is the same object as :class:`itaps.iGeom.intersect`.

.. cvar:: PyTypeObject Tolerance_Type

   `(Python 2.6+ only.)` This instance of :ctype:`PyTypeObject` represents the
   named tuple type returned from :attr:`~itaps.iGeom.Geom.tolerance`.This is
   the same object as :class:`itaps.iGeom.tolerance`.

.. cvar:: PyTypeObject MinMax_Type

   `(Python 2.6+ only.)` This instance of :ctype:`PyTypeObject` represents the
   named tuple type returned from :meth:`~itaps.iGeom.Geom.getEntBoundBox` and
   :meth:`~itaps.iGeom.Geom.getEntRange`. This is the same object as
   :class:`itaps.iGeom.min_max`.

.. cfunction:: int iGeom_Check(PyObject *p)

   Return true if its argument is a :class:`~itaps.iGeom.Geom` or a subtype of
   :class:`~itaps.iGeom.Geom`.

.. cfunction:: int iGeomEntitySet_Check(PyObject *p)

   Return true if its argument is a :class:`~itaps.iGeom.EntitySet` or a subtype
   of :class:`~itaps.iGeom.EntitySet`.

.. cfunction:: int iGeomTag_Check(PyObject *p)

   Return true if its argument is a :class:`~itaps.iGeom.Tag` or a subtype of
   :class:`~itaps.iGeom.Tag`.

.. cfunction:: PyObject* iGeomEntitySet_New()

   Return a new uninitialized :class:`~itaps.iGeom.EntitySet`, or *NULL* on
   failure.

.. cfunction:: PyObject* iGeomTag_New()

   Return a new uninitialized :class:`~itaps.iGeom.Tag`, or *NULL* on failure.

.. cfunction:: PyObject* iGeom_FromInstance(iGeom_Instance instance)

   Return a new (unowned) :class:`~itaps.iGeom.Geom`, or *NULL* on failure.

.. cfunction:: PyObject* iGeomEntitySet_FromHandle(iGeom_Object *m, iBase_EntitySetHandle h)

   Return a new :class:`itaps.iGeom.EntitySet` from a
   :class:`~itaps.iGeom.Geom` object and a C ``iBase_EntitySetHandle``, or
   *NULL* on failure.

.. cfunction:: PyObject* iGeomTag_FromHandle(iGeom_Object *m, iBase_TagHandle h)

   Return a new :class:`itaps.iGeom.Tag` from a :class:`~itaps.iGeom.Geom`
   object and a C ``iBase_TagHandle``, or *NULL* on failure.

.. cfunction:: iGeom_Object* iGeomEntitySet_GetInstance(PyObject *p)

   Attempt to return the :class:`~itaps.iGeom.Geom` object of the object *p*.
   If there is an error, an exception is raised and *NULL* is returned.

.. cfunction:: iGeom_Object* iGeomEntitySet_GET_INSTANCE(PyObject *p)

   Return the :class:`~itaps.iGeom.Geom` object of the object *p*. No error
   checking is performed.

.. cfunction:: iGeom_Object* iGeomTag_GetInstance(PyObject *p)

   Attempt to return the :class:`~itaps.iGeom.Geom` object of the object *p*.
   If there is an error, an exception is raised and *NULL* is returned.

.. cfunction:: iGeom_Object * iGeomTag_GET_INSTANCE(PyObject *p)

   Return the :class:`~itaps.iGeom.Geom` object of the object *p*. No error
   checking is performed.

.. cfunction:: int iGeomBasis_Cvt(PyObject *obj, int *val)

   Convert any compatible Python object, *obj*, to a value in the enumeration
   ``iGeomExt_Basis``. Return *1* on success, and *0* on failure. This function 
   can be used with the ``"O&"`` character code in :cfunc:`PyArg_ParseTuple`
   processing.
