#ifndef PYTAPS_NUMPY_EXTENSIONS_H
#define PYTAPS_NUMPY_EXTENSIONS_H

#include <numpy/arrayobject.h>
#include "iBase_Python.h"

#ifdef __GNUC__
#define MAYBE_UNUSED __attribute__ ((unused))
#else
#define MAYBE_UNUSED
#endif

static PyObject *
PyArray_NewFromSubStrided(PyTypeObject *type,int nd,npy_intp *dims,
                          npy_intp *strides,int typenum,void *data,
                          PyObject *base) MAYBE_UNUSED;
static PyObject *
PyArray_TryFromObject(PyObject *obj,int typenum,int min_depth,int max_depth)
    MAYBE_UNUSED;
static int
PyArray_CheckVectors(PyObject *obj,int nd,npy_intp vec_dim,int index)
    MAYBE_UNUSED;
static PyObject *
PyArray_ToVectors(PyObject *obj,int typenum,int nd,npy_intp vec_dim,int index)
    MAYBE_UNUSED;


#define PyArray_NewFromOut(nd,dims,typenum,out)                                \
    PyArray_NewFromOutSubStrided(&PyArray_Type,(nd),(dims),NULL,(typenum),     \
                                 (out))

#define PyArray_NewFromOutSub(type,nd,dims,typenum,out)                        \
    PyArray_NewFromOutSubStrided((type),(nd),(dims),NULL,(typenum),(out))

#define PyArray_NewFromOutStrided(nd,dims,strides,typenum,out)                 \
    PyArray_NewFromOutSubStrided(&PyArray_Type,(nd),(dims),(strides),          \
                                 (typenum),(out))

#define PyArray_NewFromOutSubStrided(type,nd,dims,strides,typenum,out)        \
    PyArray_NewFromSubStrided((type),(nd),(dims),(strides),(typenum),         \
                              (out->data),(out->base))


#define PyArray_NewFromMalloc(nd,dims,typenum,data)                            \
    PyArray_NewFromMallocSubStrided(&PyArray_Type,(nd),(dims),NULL,(typenum),  \
                                    (data))

#define PyArray_NewFromMallocSub(type,nd,dims,typenum,data)                    \
    PyArray_NewFromMallocSubStrided((type),(nd),(dims),NULL,(typenum),(data))

#define PyArray_NewFromMallocStrided(nd,dims,strides,typenum,data)             \
    PyArray_NewFromMallocSubStrided(&PyArray_Type,(nd),(dims),(strides),       \
                                    (typenum),(data))

#define PyArray_NewFromMallocSubStrided(type,nd,dims,strides,typenum,data)     \
    PyArray_NewFromSubStrided((type),(nd),(dims),(strides),(typenum),          \
                              (data),NULL)


static PyObject *
PyArray_NewFromSubStrided(PyTypeObject *type,int nd,npy_intp *dims,
                          npy_intp *strides,int typenum,void *data,
                          PyObject *base)
{
    PyObject *arr = PyArray_New(type,nd,dims,typenum,strides,data,0,NPY_CARRAY,
                                NULL);

    if(base)
    {
        PyArray_BASE(arr) = base;
        Py_INCREF(base);
    }
    else
        PyArray_BASE(arr) = (PyObject*)ArrDealloc_New(data);

    return arr;
}


static PyObject *
PyArray_TryFromObject(PyObject *obj,int typenum,int min_depth,int max_depth)
{
    PyObject *ret = PyArray_FromAny(obj,PyArray_DescrFromType(typenum),
                                    min_depth,max_depth,NPY_C_CONTIGUOUS,NULL);
    PyErr_Clear();
    return ret;
}

static int
PyArray_CheckVectors(PyObject *obj,int nd,npy_intp vec_dim,int index)
{
    if((nd == PyArray_NDIM(obj)+1 && vec_dim == 1) ||
       (nd == PyArray_NDIM(obj)   && vec_dim == PyArray_DIM(obj,index)))
        return 1;

    if(PyArray_NDIM(obj) != nd)
        PyErr_Format(PyExc_ValueError,"Expected %dd array",nd);
    else if(nd == 1)
        PyErr_Format(PyExc_ValueError,"Expected %zdd vector",vec_dim);
    else
        PyErr_Format(PyExc_ValueError,"Expected array of %zdd vectors",vec_dim);

    return 0;
}

static PyObject *
PyArray_ToVectors(PyObject *obj,int typenum,int nd,npy_intp vec_dim,int index)
{
    int mindim = (vec_dim == 1) ? nd-1:nd;
    PyObject *ret = PyArray_FromAny(obj,PyArray_DescrFromType(typenum),mindim,
                                    nd,NPY_C_CONTIGUOUS,NULL);
    if(ret == NULL)
        return NULL;

    if(PyArray_CheckVectors(ret,nd,vec_dim,index))
        return ret;
    else
    {
        Py_DECREF(ret);
        return NULL;
    }
}

#endif
