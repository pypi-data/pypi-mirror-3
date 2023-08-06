#include "iMesh_Python.h"
#include "iBase_Python.h"
#include "errors.h"
#include "structmember.h"

static PyObject *
iMeshTagObj_new(PyTypeObject *cls,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"tag","instance",0};
    iBaseTag_Object *tag;
    iMesh_Object *instance = NULL;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!|O!",kwlist,&iBaseTag_Type,&tag,
                                    &iMesh_Type,&instance))
        return NULL;

    if(instance)
    {
        if(iMeshTag_Check(tag))
        {
            PyErr_SetString(PyExc_ValueError,ERR_MESH_TAG_CTOR);
            return NULL;
        }
    }
    else
    {
        if(!iMeshTag_Check(tag))
        {
            PyErr_SetString(PyExc_ValueError,ERR_EXP_INSTANCE);
            return NULL;
        }
        instance = iMeshTag_GET_INSTANCE(tag);
    }

    return iMeshTag_FromHandle(instance,tag->handle);
}

static void
iMeshTagObj_dealloc(iMeshTag_Object *self)
{
    Py_XDECREF(self->instance);
    ((PyObject*)self)->ob_type->tp_free((PyObject*)self);
}

static PyObject *
iMeshTagObj_getname(iMeshTag_Object *self,void *closure)
{
    int err;
    char name[512];

    iMesh_getTagName(self->instance->handle,self->base.handle,name,&err,
                     sizeof(name));
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyString_FromString(name);
}

static PyObject *
iMeshTagObj_getsizeValues(iMeshTag_Object *self,void *closure)
{
    int size,err;
    iMesh_getTagSizeValues(self->instance->handle,self->base.handle,&size,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(size);
}

static PyObject *
iMeshTagObj_getsizeBytes(iMeshTag_Object *self,void *closure)
{
    int size,err;
    iMesh_getTagSizeBytes(self->instance->handle,self->base.handle,&size,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(size);
}

static PyObject *
iMeshTagObj_gettype(iMeshTag_Object *self,void *closure)
{
    int err;
    enum iBase_TagValueType type;

    iMesh_getTagType(self->instance->handle,self->base.handle,(int*)&type,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return Py_BuildValue("c",iBaseTagType_ToChar(type));
}

static PyObject *
iMeshTagObj_retrieve(iMeshTag_Object *self,PyObject *in_ents,
                     iBase_OutArray *data)
{
    int err;
    PyObject *ents;
    int size;
    enum iBase_TagValueType type;

    iMesh_getTagSizeValues(self->instance->handle,self->base.handle,&size,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    iMesh_getTagType(self->instance->handle,self->base.handle,(int*)&type,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int ent_size = PyArray_SIZE(ents);

        iMesh_getArrData(self->instance->handle,entities,ent_size,
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

        iMesh_getEntSetData(self->instance->handle,set,self->base.handle,
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

        iMesh_getData(self->instance->handle,entity,self->base.handle,
                      PASS_OUTARR(void,*data),&err);
        if(checkError(self->instance->handle,err))
            return NULL;

        int ndim = (size == 1) ? 0:1;
        npy_intp dims[] = {size};
        return PyArray_Return((PyArrayObject*)PyArray_NewFromOut(
            ndim,dims,iBaseTagType_ToTypenum(type),data
            ));
    }
    else if(iMesh_Check(in_ents))
    {
        iBase_EntitySetHandle set;

        if(self->instance->handle != ((iMesh_Object*)in_ents)->handle)
        {
            PyErr_SetString(PyExc_ValueError,ERR_WRONG_INSTANCE);
            return NULL;
        }

        iMesh_getRootSet(self->instance->handle,&set,&err);
        if(checkError(self->instance->handle,err))
          return NULL;

        iMesh_getEntSetData(self->instance->handle,set,self->base.handle,
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
iMeshTagObj_assign(iMeshTag_Object *self,PyObject *in_ents,PyObject *in_data)
{
    int err;
    PyObject *ents;
    PyObject *data;
    int size;
    enum iBase_TagValueType type;

    iMesh_getTagSizeValues(self->instance->handle,self->base.handle,&size,&err);
    if(checkError(self->instance->handle,err))
        return -1;

    iMesh_getTagType(self->instance->handle,self->base.handle,(int*)&type,&err);
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

        iMesh_setArrData(self->instance->handle,entities,ent_size,
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

        iMesh_setEntSetData(self->instance->handle,set,self->base.handle,
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

        iMesh_setData(self->instance->handle,entity,self->base.handle,cdata,
                      cdata_size,&err);
        Py_DECREF(data);
    }
    else if(iMesh_Check(in_ents))
    {
        iBase_EntitySetHandle set;

        if(self->instance->handle != ((iMesh_Object*)in_ents)->handle)
        {
            PyErr_SetString(PyExc_ValueError,ERR_WRONG_INSTANCE);
            return -1;
        }

        iMesh_getRootSet(self->instance->handle,&set,&err);
        if(checkError(self->instance->handle,err))
          return -1;

        data = PyArray_ToVectors(in_data,iBaseTagType_ToTypenum(type),1,size,0);
        if(data == NULL)
            return -1;

        void *cdata = PyArray_DATA(data);
        int cdata_size = PyArray_NBYTES(data);

        iMesh_setEntSetData(self->instance->handle,set,self->base.handle,
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
iMeshTagObj_del(iMeshTag_Object *self,PyObject *in_ents)
{
    int err;
    PyObject *ents;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int ent_size = PyArray_SIZE(ents);

        iMesh_rmvArrTag(self->instance->handle,entities,ent_size,
                        self->base.handle,&err);
        Py_DECREF(ents);
    }
    else if(iBaseEntitySet_Check(in_ents))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GET_HANDLE(in_ents);
        iMesh_rmvEntSetTag(self->instance->handle,set,self->base.handle,&err);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        iMesh_rmvTag(self->instance->handle,entity,self->base.handle,&err);
    }
    else if(iMesh_Check(in_ents))
    {
        iBase_EntitySetHandle set;

        if(self->instance->handle != ((iMesh_Object*)in_ents)->handle)
        {
            PyErr_SetString(PyExc_ValueError,ERR_WRONG_INSTANCE);
            return -1;
        }

        iMesh_getRootSet(self->instance->handle,&set,&err);
        if(checkError(self->instance->handle,err))
          return -1;

        iMesh_rmvEntSetTag(self->instance->handle,set,self->base.handle,&err);
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
iMeshTagObj_subscript(iMeshTag_Object *self,PyObject *in_ents)
{
    iBase_OutArray data = {0};
    return iMeshTagObj_retrieve(self,in_ents,&data);
}

static int
iMeshTagObj_ass_subscript(iMeshTag_Object *self,PyObject *in_ents,
                          PyObject *in_data)
{
    if(in_data)
        return iMeshTagObj_assign(self,in_ents,in_data);
    else
        return iMeshTagObj_del(self,in_ents);
}

static PyObject *
iMeshTagObj_get(iMeshTag_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","out",0};
    PyObject *in_ents;

    iBase_OutArray data = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&",kwlist,&in_ents,
                                    iBaseBuffer_Cvt,&data))
        return NULL;

    return iMeshTagObj_retrieve(self,in_ents,&data);
}

static PyObject *
iMeshTagObj_getData(iMeshTag_Object *self,PyObject *args,PyObject *kw)
{
    PyErr_WarnEx(PyExc_DeprecationWarning,WARN_TAG_GET,1);

    return iMeshTagObj_get(self,args,kw);
}

static PyObject *
iMeshTagObj_setData(iMeshTag_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","data",0};
    PyObject *in_ents;
    PyObject *in_data;

    PyErr_WarnEx(PyExc_DeprecationWarning,WARN_TAG_SET,1);

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO",kwlist,&in_ents,&in_data))
        return NULL;

    if(iMeshTagObj_assign(self,in_ents,in_data) == -1)
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iMeshTagObj_remove(iMeshTag_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    PyObject *in_ents;

    PyErr_WarnEx(PyExc_DeprecationWarning,WARN_TAG_REMOVE,1);

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&in_ents))
        return NULL;

    if(iMeshTagObj_del(self,in_ents) == -1)
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iMeshTagObj_repr(iMeshTag_Object *self)
{
    int err;
    char name[512];

    iMesh_getTagName(self->instance->handle,self->base.handle,name,&err,
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
iMeshTagObj_richcompare(iMeshTag_Object *lhs,
                        iMeshTag_Object *rhs,int op)
{
    if(!iMeshTag_Check(lhs) || !iMeshTag_Check(rhs))
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
iMeshTagObj_hash(iMeshTag_Object *self)
{
    return (long)self->base.handle;
}


static PyMethodDef iMeshTagObj_methods[] = {
    IMESH_METHOD(iMeshTag, get,     METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshTag, setData, METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshTag, getData, METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshTag, remove,  METH_VARARGS|METH_KEYWORDS),
    {0}
};

static PyMemberDef iMeshTagObj_members[] = {
    { "instance", T_OBJECT_EX, offsetof(iMeshTag_Object, instance), READONLY,
      IMESHDOC_iMeshTag_instance },
    {0}
};

static PyGetSetDef iMeshTagObj_getset[] = {
    IMESH_GET(iMeshTag, name),
    IMESH_GET(iMeshTag, sizeValues),
    IMESH_GET(iMeshTag, sizeBytes),
    IMESH_GET(iMeshTag, type),
    {0}
};

static PyMappingMethods iMeshTagObj_map = {
    0,                                        /* mp_length */
    (binaryfunc)iMeshTagObj_subscript,        /* mp_subscript */
    (objobjargproc)iMeshTagObj_ass_subscript, /* mp_ass_subscript */
};

static PyTypeObject iMeshTag_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iMesh.Tag",                        /* tp_name */
    sizeof(iMeshTag_Object),                  /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)iMeshTagObj_dealloc,          /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    (reprfunc)iMeshTagObj_repr,               /* tp_repr */
    0,                                        /* tp_as_number */
    0,                                        /* tp_as_sequence */
    &iMeshTagObj_map,                         /* tp_as_mapping */
    (hashfunc)iMeshTagObj_hash,               /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str */
    0,                                        /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    IMESHDOC_iMeshTag,                        /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    (richcmpfunc)iMeshTagObj_richcompare,     /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    iMeshTagObj_methods,                      /* tp_methods */
    iMeshTagObj_members,                      /* tp_members */
    iMeshTagObj_getset,                       /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    iMeshTagObj_new,                          /* tp_new */
};
