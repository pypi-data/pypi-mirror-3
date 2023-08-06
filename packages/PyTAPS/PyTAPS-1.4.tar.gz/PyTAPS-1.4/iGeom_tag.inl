#include "iGeom_Python.h"
#include "iBase_Python.h"
#include "errors.h"
#include "structmember.h"

static PyObject *
iGeomTagObj_new(PyTypeObject *cls,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"tag","instance",0};
    iBaseTag_Object *tag;
    iGeom_Object *instance = NULL;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!|O!",kwlist,&iBaseTag_Type,&tag,
                                    &iGeom_Type,&instance))
        return NULL;

    if(instance)
    {
        if(iGeomTag_Check(tag))
        {
            PyErr_SetString(PyExc_ValueError,ERR_GEOM_TAG_CTOR);
            return NULL;
        }
    }
    else
    {
        if(!iGeomTag_Check(tag))
        {
            PyErr_SetString(PyExc_ValueError,ERR_EXP_INSTANCE);
            return NULL;
        }
        instance = iGeomTag_GET_INSTANCE(tag);
    }

    return iGeomTag_FromHandle(instance,tag->handle);
}

static void
iGeomTagObj_dealloc(iGeomTag_Object *self)
{
    Py_XDECREF(self->instance);
    ((PyObject*)self)->ob_type->tp_free((PyObject*)self);
}

static PyObject *
iGeomTagObj_getname(iGeomTag_Object *self,void *closure)
{
    int err;
    char name[512];

    iGeom_getTagName(self->instance->handle,self->base.handle,name,&err,
                     sizeof(name));
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyString_FromString(name);
}

static PyObject *
iGeomTagObj_getsizeValues(iGeomTag_Object *self,void *closure)
{
    int size,err;
    iGeom_getTagSizeValues(self->instance->handle,self->base.handle,&size,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(size);
}

static PyObject *
iGeomTagObj_getsizeBytes(iGeomTag_Object *self,void *closure)
{
    int size,err;
    iGeom_getTagSizeBytes(self->instance->handle,self->base.handle,&size,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(size);
}

static PyObject *
iGeomTagObj_gettype(iGeomTag_Object *self,void *closure)
{
    int err;
    enum iBase_TagValueType type;

    iGeom_getTagType(self->instance->handle,self->base.handle,(int*)&type,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return Py_BuildValue("c",iBaseTagType_ToChar(type));
}

static PyObject *
iGeomTagObj_retrieve(iGeomTag_Object *self,PyObject *in_ents,
                     iBase_OutArray *data)
{
    int err;
    PyObject *ents;
    int size;
    enum iBase_TagValueType type;

    iGeom_getTagSizeValues(self->instance->handle,self->base.handle,&size,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    iGeom_getTagType(self->instance->handle,self->base.handle,(int*)&type,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int ent_size = PyArray_SIZE(ents);

        iGeom_getArrData(self->instance->handle,entities,ent_size,
                         self->base.handle,PASS_OUTARR(void,*data),&err);
        Py_DECREF(ents);
        if(checkError(self->instance->handle,err))
            return NULL;

        int ndim = (size == 1) ? 1:2;
        npy_intp dims[] = {ent_size,size};
        return PyArray_NewFromOut(ndim,dims,iBaseTagType_ToTypenum(type),data);
    }
    else if(iBaseEntitySet_Check(in_ents))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GET_HANDLE(in_ents);

        iGeom_getEntSetData(self->instance->handle,set,self->base.handle,
                            PASS_OUTARR(void,*data),&err);
        if(checkError(self->instance->handle,err))
            return NULL;

        int ndim = (size == 1) ? 0:1;
        npy_intp dims[] = {size};
        return PyArray_Return((PyArrayObject*)PyArray_NewFromOut(
            ndim,dims,iBaseTagType_ToTypenum(type),data
            ));
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);

        iGeom_getData(self->instance->handle,entity,self->base.handle,
                      PASS_OUTARR(void,*data),&err);
        if(checkError(self->instance->handle,err))
            return NULL;

        int ndim = (size == 1) ? 0:1;
        npy_intp dims[] = {size};
        return PyArray_Return((PyArrayObject*)PyArray_NewFromOut(
            ndim,dims,iBaseTagType_ToTypenum(type),data
            ));
    }
    else if(iGeom_Check(in_ents))
    {
        iBase_EntitySetHandle set;

        if(self->instance->handle != ((iGeom_Object*)in_ents)->handle)
        {
            PyErr_SetString(PyExc_ValueError,ERR_WRONG_INSTANCE);
            return NULL;
        }

        iGeom_getRootSet(self->instance->handle,&set,&err);
        if(checkError(self->instance->handle,err))
          return NULL;

        iGeom_getEntSetData(self->instance->handle,set,self->base.handle,
                            PASS_OUTARR(void,*data),&err);
        if(checkError(self->instance->handle,err))
            return NULL;

        int ndim = (size == 1) ? 0:1;
        npy_intp dims[] = {size};
        return PyArray_Return((PyArrayObject*)PyArray_NewFromOut(
            ndim,dims,iBaseTagType_ToTypenum(type),data
            ));
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return NULL;
    }
}

static int
iGeomTagObj_assign(iGeomTag_Object *self,PyObject *in_ents,PyObject *in_data)
{
    int err;
    PyObject *ents;
    PyObject *data;
    int size;
    enum iBase_TagValueType type;

    iGeom_getTagSizeValues(self->instance->handle,self->base.handle,&size,&err);
    if(checkError(self->instance->handle,err))
        return -1;

    iGeom_getTagType(self->instance->handle,self->base.handle,(int*)&type,&err);
    if(checkError(self->instance->handle,err))
        return -1;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int ent_size = PyArray_SIZE(ents);

        data = PyArray_ToVectors(in_data,iBaseTagType_ToTypenum(type),2,size,1);
        if(data == NULL)
        {
            Py_DECREF(ents);
            return -1;
        }

        void *cdata = PyArray_DATA(data);
        int cdata_size = PyArray_NBYTES(data);

        iGeom_setArrData(self->instance->handle,entities,ent_size,
                         self->base.handle,cdata,cdata_size,&err);

        Py_DECREF(ents);
        Py_DECREF(data);
    }
    else if(iBaseEntitySet_Check(in_ents))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GET_HANDLE(in_ents);

        data = PyArray_ToVectors(in_data,iBaseTagType_ToTypenum(type),1,size,0);
        if(data == NULL)
            return -1;

        void *cdata = PyArray_DATA(data);
        int cdata_size = PyArray_NBYTES(data);

        iGeom_setEntSetData(self->instance->handle,set,self->base.handle,
                            cdata,cdata_size,&err);
        Py_DECREF(data);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);

        data = PyArray_ToVectors(in_data,iBaseTagType_ToTypenum(type),1,size,0);
        if(data == NULL)
            return -1;

        void *cdata = PyArray_DATA(data);
        int cdata_size = PyArray_NBYTES(data);

        iGeom_setData(self->instance->handle,entity,self->base.handle,cdata,
                      cdata_size,&err);
        Py_DECREF(data);
    }
    else if(iGeom_Check(in_ents))
    {
        iBase_EntitySetHandle set;

        if(self->instance->handle != ((iGeom_Object*)in_ents)->handle)
        {
            PyErr_SetString(PyExc_ValueError,ERR_WRONG_INSTANCE);
            return -1;
        }

        iGeom_getRootSet(self->instance->handle,&set,&err);
        if(checkError(self->instance->handle,err))
          return -1;

        data = PyArray_ToVectors(in_data,iBaseTagType_ToTypenum(type),1,size,0);
        if(data == NULL)
            return -1;

        void *cdata = PyArray_DATA(data);
        int cdata_size = PyArray_NBYTES(data);

        iGeom_setEntSetData(self->instance->handle,set,self->base.handle,
                            cdata,cdata_size,&err);
        Py_DECREF(data);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return -1;
    }

    if(checkError(self->instance->handle,err))
        return -1;
    return 0;
}

static int
iGeomTagObj_del(iGeomTag_Object *self,PyObject *in_ents)
{
    int err;
    PyObject *ents;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int ent_size = PyArray_SIZE(ents);

        iGeom_rmvArrTag(self->instance->handle,entities,ent_size,
                        self->base.handle,&err);
        Py_DECREF(ents);
    }
    else if(iBaseEntitySet_Check(in_ents))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GET_HANDLE(in_ents);
        iGeom_rmvEntSetTag(self->instance->handle,set,self->base.handle,&err);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        iGeom_rmvTag(self->instance->handle,entity,self->base.handle,&err);
    }
    else if(iGeom_Check(in_ents))
    {
        iBase_EntitySetHandle set;

        if(self->instance->handle != ((iGeom_Object*)in_ents)->handle)
        {
            PyErr_SetString(PyExc_ValueError,ERR_WRONG_INSTANCE);
            return -1;
        }

        iGeom_getRootSet(self->instance->handle,&set,&err);
        if(checkError(self->instance->handle,err))
          return -1;

        iGeom_rmvEntSetTag(self->instance->handle,set,self->base.handle,&err);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return -1;
    }

    if(checkError(self->instance->handle,err))
        return -1;
    return 0;
}

static PyObject *
iGeomTagObj_subscript(iGeomTag_Object *self,PyObject *in_ents)
{
    iBase_OutArray data = {0};
    return iGeomTagObj_retrieve(self,in_ents,&data);
}

static int
iGeomTagObj_ass_subscript(iGeomTag_Object *self,PyObject *in_ents,
                          PyObject *in_data)
{
    if(in_data)
        return iGeomTagObj_assign(self,in_ents,in_data);
    else
        return iGeomTagObj_del(self,in_ents);
}

static PyObject *
iGeomTagObj_get(iGeomTag_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","out",0};
    PyObject *in_ents;

    iBase_OutArray data = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&",kwlist,&in_ents,
                                    iBaseBuffer_Cvt,&data))
        return NULL;

    return iGeomTagObj_retrieve(self,in_ents,&data);
}

static PyObject *
iGeomTagObj_getData(iGeomTag_Object *self,PyObject *args,PyObject *kw)
{
    PyErr_WarnEx(PyExc_DeprecationWarning,WARN_TAG_GET,1);

    return iGeomTagObj_get(self,args,kw);
}

static PyObject *
iGeomTagObj_setData(iGeomTag_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","data",0};
    PyObject *in_ents;
    PyObject *in_data;

    PyErr_WarnEx(PyExc_DeprecationWarning,WARN_TAG_SET,1);

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO",kwlist,&in_ents,&in_data))
        return NULL;

    if(iGeomTagObj_assign(self,in_ents,in_data) == -1)
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iGeomTagObj_remove(iGeomTag_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    PyObject *in_ents;

    PyErr_WarnEx(PyExc_DeprecationWarning,WARN_TAG_REMOVE,1);

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&in_ents))
        return NULL;

    if(iGeomTagObj_del(self,in_ents) == -1)
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iGeomTagObj_repr(iGeomTag_Object *self)
{
    int err;
    char name[512];

    iGeom_getTagName(self->instance->handle,self->base.handle,name,&err,
                     sizeof(name));
    if(checkError(self->instance->handle,err))
    {
        PyErr_Clear();
        return PyString_FromFormat("<%s %p>",self->base.ob_type->tp_name,
                                   self->base.handle);
    }
    else
    {
        return PyString_FromFormat("<%s '%s' %p>",self->base.ob_type->tp_name,
                                   name,self->base.handle);
    }
}

static PyObject *
iGeomTagObj_richcompare(iGeomTag_Object *lhs,
                        iGeomTag_Object *rhs,int op)
{
    if(!iGeomTag_Check(lhs) || !iGeomTag_Check(rhs))
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
iGeomTagObj_hash(iGeomTag_Object *self)
{
    return (long)self->base.handle;
}


static PyMethodDef iGeomTagObj_methods[] = {
    IGEOM_METHOD(iGeomTag, get,     METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomTag, setData, METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomTag, getData, METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeomTag, remove,  METH_VARARGS|METH_KEYWORDS),
    {0}
};

static PyMemberDef iGeomTagObj_members[] = {
    { "instance", T_OBJECT_EX, offsetof(iGeomTag_Object, instance), READONLY,
      IGEOMDOC_iGeomTag_instance },
    {0}
};

static PyGetSetDef iGeomTagObj_getset[] = {
    IGEOM_GET(iGeomTag, name),
    IGEOM_GET(iGeomTag, sizeValues),
    IGEOM_GET(iGeomTag, sizeBytes),
    IGEOM_GET(iGeomTag, type),
    {0}
};

static PyMappingMethods iGeomTagObj_map = {
    0,                                        /* mp_length */
    (binaryfunc)iGeomTagObj_subscript,        /* mp_subscript */
    (objobjargproc)iGeomTagObj_ass_subscript, /* mp_ass_subscript */
};

static PyTypeObject iGeomTag_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iGeom.Tag",                        /* tp_name */
    sizeof(iGeomTag_Object),                  /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)iGeomTagObj_dealloc,          /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    (reprfunc)iGeomTagObj_repr,               /* tp_repr */
    0,                                        /* tp_as_number */
    0,                                        /* tp_as_sequence */
    &iGeomTagObj_map,                         /* tp_as_mapping */
    (hashfunc)iGeomTagObj_hash,               /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str */
    0,                                        /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    IGEOMDOC_iGeomTag,                        /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    (richcmpfunc)iGeomTagObj_richcompare,     /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    iGeomTagObj_methods,                      /* tp_methods */
    iGeomTagObj_members,                      /* tp_members */
    iGeomTagObj_getset,                       /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    iGeomTagObj_new,                          /* tp_new */
};
