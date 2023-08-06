#include "errors.h"
#include "iGeom_Python.h"
#include "iBase_Python.h"
#include "structmember.h"

static PyObject *
iGeomEntSetObj_new(PyTypeObject *cls,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set","instance",0};
    iBaseEntitySet_Object *set;
    iGeom_Object *instance = NULL;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!|O!",kwlist,
                                    &iBaseEntitySet_Type,&set,&iGeom_Type,
                                    &instance))
        return NULL;

    if(instance)
    {
        if(iGeomEntitySet_Check(set))
        {
            PyErr_SetString(PyExc_ValueError,ERR_GEOM_SET_CTOR);
            return NULL;
        }
    }
    else
    {
        if(!iGeomEntitySet_Check(set))
        {
            PyErr_SetString(PyExc_ValueError,ERR_EXP_INSTANCE);
            return NULL;
        }
        instance = iGeomEntitySet_GET_INSTANCE(set);
    }

    return iGeomEntitySet_FromHandle(instance,set->handle);
}

static void
iGeomEntSetObj_dealloc(iGeomEntitySet_Object *self)
{
    Py_XDECREF(self->instance);
    ((PyObject*)self)->ob_type->tp_free((PyObject*)self);
}

static PyObject *
iGeomEntSetObj_getisList(iGeomEntitySet_Object *self,void *closure)
{
    int is_list,err;
    iGeom_isList(self->instance->handle,self->base.handle,&is_list,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyBool_FromLong(is_list);
}

static PyObject *
iGeomEntSetObj_getNumOfType(iGeomEntitySet_Object *self,PyObject *args,
                            PyObject *kw)
{
    static char *kwlist[] = {"type",0};
    int err;
    enum iBase_EntityType type;

    int num;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O&",kwlist,iBaseType_Cvt,&type))
        return NULL;

    iGeom_getNumOfType(self->instance->handle,self->base.handle,type,&num,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num);
}

static Py_ssize_t
iGeomEntSetObj_len(iGeomEntitySet_Object *self)
{
    int num,err;

    iGeom_getNumOfType(self->instance->handle,self->base.handle,iBase_ALL_TYPES,
                       &num,&err);
    if(checkError(self->instance->handle,err))
        return -1;

    return num;
}

static PyObject *
iGeomEntSetObj_getEntities(iGeomEntitySet_Object *self,PyObject *args,
                           PyObject *kw)
{
    static char *kwlist[] = {"type","out",0};
    int err;
    enum iBase_EntityType type = iBase_ALL_TYPES;

    iBase_OutArray entities = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"|O&O&",kwlist,iBaseType_Cvt,&type,
                                    iBaseBuffer_Cvt,&entities))
        return NULL;

    iGeom_getEntities(self->instance->handle,self->base.handle,type,
                      PASS_OUTARR_ENT(entities),&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {entities.size};
    return PyArray_NewFromOut(1,dims,NPY_IBASEENT,&entities);
}

static PyObject *
iGeomEntSetObj_getNumEntSets(iGeomEntitySet_Object *self,PyObject *args,
                             PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int err;
    int hops=-1;

    int num_sets;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"|i",kwlist,&hops))
        return NULL;

    iGeom_getNumEntSets(self->instance->handle,self->base.handle,hops,
                        &num_sets,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num_sets);
}

static PyObject *
iGeomEntSetObj_getEntSets(iGeomEntitySet_Object *self,PyObject *args,
                          PyObject *kw)
{
    static char *kwlist[] = {"hops","out",0};
    int err;
    int hops=-1;

    iBase_OutArray sets = {0};
  
    if(!PyArg_ParseTupleAndKeywords(args,kw,"|iO&",kwlist,&hops,
                                    iBaseBuffer_Cvt,&sets))
        return NULL;

    iGeom_getEntSets(self->instance->handle,self->base.handle,hops,
                     PASS_OUTARR_SET(sets),&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {sets.size};
    return PyArray_NewFromOutBase(1,dims,NPY_IBASEENTSET,&sets,
                                  (iBase_Object*)self->instance);
}

static PyObject *
iGeomEntSetObj_add(iGeomEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    int err;
    PyObject *in_ents,*ents;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&in_ents))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int size = PyArray_SIZE(ents);

        iGeom_addEntArrToSet(self->instance->handle,entities,size,
                             self->base.handle,&err);
        Py_DECREF(ents);
    }
    else if(iBaseEntitySet_Check(in_ents))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GET_HANDLE(in_ents);
        iGeom_addEntSet(self->instance->handle,set,self->base.handle,&err);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        iGeom_addEntToSet(self->instance->handle,entity,self->base.handle,&err);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return NULL;
    }

    if(checkError(self->instance->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomEntSetObj_remove(iGeomEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    int err;
    PyObject *in_ents,*ents;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&in_ents))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int size = PyArray_SIZE(ents);

        iGeom_rmvEntArrFromSet(self->instance->handle,entities,size,
                               self->base.handle,&err);
        Py_DECREF(ents);
    }
    else if(iBaseEntitySet_Check(in_ents))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GET_HANDLE(in_ents);
        iGeom_rmvEntSet(self->instance->handle,set,self->base.handle,&err);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        iGeom_rmvEntFromSet(self->instance->handle,entity,self->base.handle,
                            &err);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return NULL;
    }

    if(checkError(self->instance->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomEntSetObj_contains(iGeomEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","out",0};
    int err;
    PyObject *in_ents,*ents;

    iBase_OutArray contains = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&",kwlist,&in_ents,
                                    iBaseBuffer_Cvt,&contains))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int size = PyArray_SIZE(ents);

        iGeom_isEntArrContained(self->instance->handle,self->base.handle,
                                entities,size,PASS_OUTARR(int,contains),&err);
        Py_DECREF(ents);
        if(checkError(self->instance->handle,err))
            return NULL;

        npy_intp dims[] = {contains.size};
        npy_intp strides[] = {sizeof(int)/sizeof(npy_bool)};
        return PyArray_NewFromOutStrided(1,dims,strides,NPY_BOOL,&contains);
    }
    else if(iBaseEntitySet_Check(in_ents))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GET_HANDLE(in_ents);
        int contains;

        iGeom_isEntSetContained(self->instance->handle,self->base.handle,set,
                                &contains,&err);
        if(checkError(self->instance->handle,err))
            return NULL;

        return PyBool_FromLong(contains);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        int contains;

        iGeom_isEntContained(self->instance->handle,self->base.handle,entity,
                             &contains,&err);
        if(checkError(self->instance->handle,err))
            return NULL;

        return PyBool_FromLong(contains);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return NULL;
    }
}

static int
iGeomEntSetObj_in(iGeomEntitySet_Object *self,PyObject *value)
{
    int err;
    int contains;

    if(iBaseEntitySet_Check(value))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GET_HANDLE(value);
        iGeom_isEntSetContained(self->instance->handle,self->base.handle,set,
                                &contains,&err);
        if(checkError(self->instance->handle,err))
            return -1;

        return contains;
    }
    else if(iBaseEntity_Check(value))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(value);
        iGeom_isEntContained(self->instance->handle,self->base.handle,entity,
                             &contains,&err);
        if(checkError(self->instance->handle,err))
            return -1;

        return contains;
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTSET);
        return -1;
    }
}

/* TODO: add/removeParent? */

static PyObject *
iGeomEntSetObj_addChild(iGeomEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    int err;
    iBaseEntitySet_Object *set;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntitySet_Type,
                                    &set))
        return NULL;

    iGeom_addPrntChld(self->instance->handle,self->base.handle,set->handle,
                      &err);
    if(checkError(self->instance->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iGeomEntSetObj_removeChild(iGeomEntitySet_Object *self,PyObject *args,
                           PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    int err;
    iBaseEntitySet_Object *set;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntitySet_Type,
                                    &set))
        return NULL;

    iGeom_rmvPrntChld(self->instance->handle,self->base.handle,set->handle,
                      &err);
    if(checkError(self->instance->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iGeomEntSetObj_isChild(iGeomEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    int err;
    iBaseEntitySet_Object *set;

    int is_child;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntitySet_Type,
                                    &set))
        return NULL;

    iGeom_isChildOf(self->instance->handle,self->base.handle,set->handle,
                    &is_child,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyBool_FromLong(is_child);
}

static PyObject *
iGeomEntSetObj_getNumChildren(iGeomEntitySet_Object *self,PyObject *args,
                              PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int err;
    int hops=-1;

    int num_children;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"|i",kwlist,&hops))
        return NULL;

    iGeom_getNumChld(self->instance->handle,self->base.handle,hops,
                     &num_children,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num_children);
}

static PyObject *
iGeomEntSetObj_getNumParents(iGeomEntitySet_Object *self,PyObject *args,
                             PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int err;
    int hops=-1;

    int num_parents;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"|i",kwlist,&hops))
        return NULL;

    iGeom_getNumPrnt(self->instance->handle,self->base.handle,hops,
                     &num_parents,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num_parents);
}

static PyObject *
iGeomEntSetObj_getChildren(iGeomEntitySet_Object *self,PyObject *args,
                           PyObject *kw)
{
    static char *kwlist[] = {"hops","out",0};
    int err;
    int hops=-1;

    iBase_OutArray sets = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"|iO&",kwlist,&hops,
                                    iBaseBuffer_Cvt,&sets))
        return NULL;

    iGeom_getChldn(self->instance->handle,self->base.handle,hops,
                   PASS_OUTARR_SET(sets),&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {sets.size};
    return PyArray_NewFromOutBase(1,dims,NPY_IBASEENTSET,&sets,
                                  (iBase_Object*)self->instance);
}

static PyObject *
iGeomEntSetObj_getParents(iGeomEntitySet_Object *self,PyObject *args,
                          PyObject *kw)
{
    static char *kwlist[] = {"hops","out",0};
    int err;
    int hops=-1;

    iBase_OutArray sets = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"|iO&",kwlist,&hops,
                                    iBaseBuffer_Cvt,&sets))
        return NULL;

    iGeom_getPrnts(self->instance->handle,self->base.handle,hops,
                   PASS_OUTARR_SET(sets),&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {sets.size};
    return PyArray_NewFromOutBase(1,dims,NPY_IBASEENTSET,&sets,
                                  (iBase_Object*)self->instance);
}

static PyObject *
iGeomEntSetObj_iterate(iGeomEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    PyObject *first = PyTuple_Pack(1,self);
    PyObject *tuple = PyNumber_Add(first,args);
    PyObject *ret;

    Py_DECREF(first);
    ret = PyObject_Call((PyObject*)&iGeomIter_Type,tuple,kw);
    Py_DECREF(tuple);

    return ret;
}

static PyObject *
iGeomEntSetObj_iter(iGeomEntitySet_Object *self)
{
    PyObject *args;
    PyObject *ret;

    args = PyTuple_Pack(1,self);
    ret = PyObject_CallObject((PyObject*)&iGeomIter_Type,args);
    Py_DECREF(args);

    return ret;
}

static PyObject *
iGeomEntSetObj_sub(iGeomEntitySet_Object *lhs,iGeomEntitySet_Object *rhs)
{
    int err;
    iBase_EntitySetHandle result = NULL;

    if(lhs->instance->handle != rhs->instance->handle)
        return NULL;

    iGeom_subtract(lhs->instance->handle,lhs->base.handle,rhs->base.handle,
                   &result,&err);
    if(checkError(lhs->instance->handle,err))
        return NULL;

    return iGeomEntitySet_FromHandle(lhs->instance,result);
}

static PyObject *
iGeomEntSetObj_bitand(iGeomEntitySet_Object *lhs,iGeomEntitySet_Object *rhs)
{
    int err;
    iBase_EntitySetHandle result = NULL;

    if(lhs->instance->handle != rhs->instance->handle)
        return NULL;

    iGeom_intersect(lhs->instance->handle,lhs->base.handle,rhs->base.handle,
                    &result,&err);
    if(checkError(lhs->instance->handle,err))
        return NULL;

    return iGeomEntitySet_FromHandle(lhs->instance,result);
}

static PyObject *
iGeomEntSetObj_bitor(iGeomEntitySet_Object *lhs,iGeomEntitySet_Object *rhs)
{
    int err;
    iBase_EntitySetHandle result = NULL;

    if(lhs->instance->handle != rhs->instance->handle)
        return NULL;

    iGeom_unite(lhs->instance->handle,lhs->base.handle,rhs->base.handle,
                &result,&err);
    if(checkError(lhs->instance->handle,err))
        return NULL;

    return iGeomEntitySet_FromHandle(lhs->instance,result);
}


static PyObject *
iGeomEntSetObj_difference(iGeomEntitySet_Object *self,PyObject *args,
                          PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    iGeomEntitySet_Object *rhs;
    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iGeomEntitySet_Type,
                                    &rhs))
        return NULL;

    return iGeomEntSetObj_sub(self,rhs);
}

static PyObject *
iGeomEntSetObj_intersection(iGeomEntitySet_Object *self,PyObject *args,
                            PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    iGeomEntitySet_Object *rhs;
    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iGeomEntitySet_Type,
                                    &rhs))
        return NULL;

    return iGeomEntSetObj_bitand(self,rhs);
}

static PyObject *
iGeomEntSetObj_union(iGeomEntitySet_Object *self,PyObject *args,
                     PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    iGeomEntitySet_Object *rhs;
    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iGeomEntitySet_Type,
                                    &rhs))
        return NULL;

    return iGeomEntSetObj_bitor(self,rhs);
}

static PyObject *
iGeomEntSetObj_repr(iGeomEntitySet_Object *self)
{
    return PyString_FromFormat("<%s %p>",self->base.ob_type->tp_name,
                               self->base.handle);
}

static PyObject *
iGeomEntSetObj_richcompare(iGeomEntitySet_Object *lhs,
                           iGeomEntitySet_Object *rhs,int op)
{
    if(!iGeomEntitySet_Check(lhs) || !iGeomEntitySet_Check(rhs))
    {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    switch(op)
    {
    case Py_EQ:
        return PyBool_FromLong(lhs->base.handle == rhs->base.handle &&
                               lhs->instance->handle == rhs->instance->handle);
    case Py_NE:
        return PyBool_FromLong(lhs->base.handle != rhs->base.handle ||
                               lhs->instance->handle != rhs->instance->handle);
    default:
        PyErr_SetNone(PyExc_TypeError);
        return NULL;
    }
}

static long
iGeomEntSetObj_hash(iGeomEntitySet_Object *self)
{
    return (long)self->base.handle;
}


static PyMethodDef iGeomEntSetObj_methods[] = {
    IGEOM_METHOD(iGeomEntSet, getNumOfType,     METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomEntSet, getEntities,      METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomEntSet, getNumEntSets,    METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomEntSet, getEntSets,       METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomEntSet, add,              METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomEntSet, remove,           METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomEntSet, contains,         METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomEntSet, isChild,          METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomEntSet, getNumChildren,   METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomEntSet, getNumParents,    METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomEntSet, getChildren,      METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomEntSet, getParents,       METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomEntSet, addChild,         METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomEntSet, removeChild,      METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomEntSet, iterate,          METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomEntSet, difference,       METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomEntSet, intersection,     METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomEntSet, union,            METH_VARARGS|METH_KEYWORDS),
    {0}
};

static PyMemberDef iGeomEntSetObj_members[] = {
    { "instance", T_OBJECT_EX, offsetof(iGeomEntitySet_Object, instance),
      READONLY,  IGEOMDOC_iGeomEntSet_instance },
    {0}
};

static PyGetSetDef iGeomEntSetObj_getset[] = {
    IGEOM_GET(iGeomEntSet, isList),
    {0}
};

static PyNumberMethods iGeomEntSetObj_num = {
    0,                                        /* nb_add */
    (binaryfunc)iGeomEntSetObj_sub,           /* nb_subtract */
    0,                                        /* nb_multiply */
    0,                                        /* nb_divide */
    0,                                        /* nb_remainder */
    0,                                        /* nb_divmod */
    0,                                        /* nb_power */
    0,                                        /* nb_negative */
    0,                                        /* nb_positive */
    0,                                        /* nb_absolute */
    0,                                        /* nb_nonzero */
    0,                                        /* nb_invert */
    0,                                        /* nb_lshift */
    0,                                        /* nb_rshift */
    (binaryfunc)iGeomEntSetObj_bitand,        /* nb_and */
    0,                                        /* nb_xor */
    (binaryfunc)iGeomEntSetObj_bitor,         /* nb_or */
    0,                                        /* nb_coerce */
    0,                                        /* nb_int */
    0,                                        /* nb_long */
    0,                                        /* nb_float */
    0,                                        /* nb_oct */
    0,                                        /* nb_hex */
};

static PySequenceMethods iGeomEntSetObj_seq = {
    (lenfunc)iGeomEntSetObj_len,              /* sq_length */
    0,                                        /* sq_concat */
    0,                                        /* sq_repeat */
    0,                                        /* sq_item */
    0,                                        /* sq_slice */
    0,                                        /* sq_ass_item */
    0,                                        /* sq_ass_slice */
    (objobjproc)iGeomEntSetObj_in,            /* sq_contains */
    0,                                        /* sq_inplace_concat */
    0,                                        /* sq_inplace_repeat */
};

static PyTypeObject iGeomEntitySet_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iGeom.EntitySet",                  /* tp_name */
    sizeof(iGeomEntitySet_Object),            /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)iGeomEntSetObj_dealloc,       /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    (reprfunc)iGeomEntSetObj_repr,            /* tp_repr */
    &iGeomEntSetObj_num,                      /* tp_as_number */
    &iGeomEntSetObj_seq,                      /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    (hashfunc)iGeomEntSetObj_hash,            /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str */
    0,                                        /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    IGEOMDOC_iGeomEntSet,                     /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    (richcmpfunc)iGeomEntSetObj_richcompare,  /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    (getiterfunc)iGeomEntSetObj_iter,         /* tp_iter */
    0,                                        /* tp_iternext */
    iGeomEntSetObj_methods,                   /* tp_methods */
    iGeomEntSetObj_members,                   /* tp_members */
    iGeomEntSetObj_getset,                    /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    iGeomEntSetObj_new,                       /* tp_new */
};
