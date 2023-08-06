#ifndef PYTAPS_HELPERS_H
#define PYTAPS_HELPERS_H

#include <Python.h>
#include "errors.h"

/* NOTE: these are never freed! (Fix in Python 3.x?) */
static PyObject *OffsetList;
static PyObject *OffsetListSingle_TypeObj;
static PyObject *OffsetListTuple_TypeObj;
static PyObject *IndexedList_TypeObj;

#define OffsetListSingle_Type (*(PyTypeObject*)OffsetListSingle_TypeObj)
#define OffsetListTuple_Type (*(PyTypeObject*)OffsetListTuple_TypeObj)
#define IndexedList_Type (*(PyTypeObject*)IndexedList_TypeObj)

#define OffsetList_Check(o)                                              \
    (PyObject_TypeCheck((PyObject*)(o),&OffsetListSingle_Type) ||        \
     PyObject_TypeCheck((PyObject*)(o),&OffsetListTuple_Type))

#define IndexedList_Check(o)                                             \
    PyObject_TypeCheck((PyObject*)(o),&IndexedList_Type)

/* NOTE: steals references to offsets and data */
#define OffsetList_New(offsets,data)                                     \
    PyObject_CallFunction(OffsetList,"NN",(offsets),(data))

/* NOTE: steals references to offsets and data */
#define IndexedList_New(offsets,indices,data)                            \
    PyObject_CallFunction(IndexedList_TypeObj,"NNN",(offsets),(indices), \
                          (data))

#if PY_VERSION_HEX >= 0x020600f0

static PyObject *g_namedtuple;

static PyObject *
NamedTuple_New(PyTypeObject *type,const char *fmt,...)
{
    va_list args;
    va_start(args,fmt);
    PyObject *py_args = Py_VaBuildValue(fmt,args);
    va_end(args);

    PyObject *res = PyObject_Call((PyObject*)type,py_args,NULL);
    Py_DECREF(py_args);

    return res;
}

static PyTypeObject *
NamedTuple_CreateType(PyObject *module,const char *name,const char *fields)
{
    PyObject *type = PyObject_CallFunction(g_namedtuple,"ss",name,fields);
    if(module)
        PyModule_AddObject(module,name,type);
    return (PyTypeObject*)type;
}

#else

static PyObject *
NamedTuple_New(PyTypeObject *type,const char *fmt,...)
{
    va_list args;
    va_start(args,fmt);
    PyObject *res = Py_VaBuildValue(fmt,args);
    va_end(args);

    return res;
}

static PyTypeObject *
NamedTuple_CreateType(PyObject *module,const char *name,const char *fields)
{
	return 0;
}

#endif

static int
OffsetListBuffer_Cvt(PyObject *obj,iBase_OutArray *off,int n,...)
{
    PyObject *offsets = NULL;
    PyObject *data = NULL;
    int ret = 0;

    va_list ap;
    va_start(ap,n);

    if(PyTuple_Check(obj))
    {
        int i;

        if(PyTuple_GET_SIZE(obj) != n+1)
            goto err;
        if(!iBaseBuffer_Cvt(PyTuple_GET_ITEM(obj,0),off))
            goto err;

        for(i=1; i<n+1; i++)
        {
            if(!iBaseBuffer_Cvt(PyTuple_GET_ITEM(obj,i),
                                va_arg(ap,iBase_OutArray*)))
                goto err;
        }
    }
    else if(OffsetList_Check(obj))
    {
        PyObject *offsets = PyObject_GetAttrString(obj,"offsets");
        PyObject *data = PyObject_GetAttrString(obj,"data");

        if(n > 1 && !PyTuple_Check(data))
            goto err;
        if(!iBaseBuffer_Cvt(offsets,off))
            goto err;

        if(!PyTuple_Check(data))
        {
            if(!iBaseBuffer_Cvt(data,va_arg(ap,iBase_OutArray*)))
                goto err;
        }
        else
        {
            int i;
            for(i=0; i<n; i++)
            {
                if(!iBaseBuffer_Cvt(PyTuple_GET_ITEM(data,i),
                                    va_arg(ap,iBase_OutArray*)))
                    goto err; 
            }
        }
    }
    else
    {
        goto err;
    }

    ret = 1;
err:
    Py_XDECREF(offsets);
    Py_XDECREF(data);
    va_end(ap);
    return ret;
}

static int
IndexedListBuffer_Cvt(PyObject *obj,iBase_OutArray *off,iBase_OutArray *ind,
                      iBase_OutArray *arr)
{
    if(PyTuple_Check(obj))
    {
        return PyArg_ParseTuple(obj,"O&O&O&",iBaseBuffer_Cvt,off,
                                             iBaseBuffer_Cvt,ind,
                                             iBaseBuffer_Cvt,arr);
    }

    if(IndexedList_Check(obj))
    {
        PyObject *offsetlist = PyObject_GetAttrString(obj,"indices");
        PyObject *offsets = PyObject_GetAttrString(offsetlist,"offsets");
        PyObject *indices = PyObject_GetAttrString(offsetlist,"data");
        PyObject *data = PyObject_GetAttrString(obj,"data");

        int ret = iBaseBuffer_Cvt(offsets,off) &&
                  iBaseBuffer_Cvt(indices,ind) &&
                  iBaseBuffer_Cvt(data,arr);

        Py_DECREF(offsetlist);
        Py_DECREF(offsets);
        Py_DECREF(indices);
        Py_DECREF(data);

        return ret;
    }

    return 0;
}

static int import_helpers(void)
{
    PyObject *helper_module;

    if( (helper_module = PyImport_ImportModule("itaps.helpers")) == NULL)
        return -1;
    if( (OffsetList = PyObject_GetAttrString(helper_module,
        "OffsetList")) == NULL)
        return -1;
    if( (OffsetListSingle_TypeObj = PyObject_GetAttrString(helper_module,
        "OffsetListSingle")) == NULL)
        return -1;
    if( (OffsetListTuple_TypeObj = PyObject_GetAttrString(helper_module,
        "OffsetListTuple")) == NULL)
        return -1;
    if( (IndexedList_TypeObj = PyObject_GetAttrString(helper_module,
        "IndexedList")) == NULL)
        return -1;
    Py_DECREF(helper_module);

#if PY_VERSION_HEX >= 0x020600f0
    PyObject *collections_module;

    if( (collections_module = PyImport_ImportModule("collections")) == NULL)
        return -1;
    if( (g_namedtuple = PyObject_GetAttrString(collections_module,
        "namedtuple")) == NULL)
        return -1;
    Py_DECREF(collections_module);
#endif

    return 0;

    /* Suppress warnings if this function isn't used */
    (void)NamedTuple_New;
    (void)NamedTuple_CreateType;
    (void)OffsetListBuffer_Cvt;
    (void)IndexedListBuffer_Cvt;
}

#endif
