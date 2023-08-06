#ifndef PYTAPS_IBASE_PYTHON_H
#define PYTAPS_IBASE_PYTHON_H

#include <Python.h>
#include <iBase.h>
#include <numpy/ndarrayobject.h>

#ifdef __cplusplus
extern "C" {
#endif

#define PyObject_AllocNew(obj,type)                         \
    ( (obj*) PyObject_INIT((type)->tp_alloc((type),0),0) )

typedef int (*cvtfunc)(PyObject *,int *);

typedef PyObject * (*fromentfunc)(iBase_EntityHandle);
typedef PyObject * (*fromsetfunc)(iBase_EntitySetHandle);
typedef PyObject * (*fromtagfunc)(iBase_TagHandle);

typedef iBase_EntityHandle (*getentfunc)(PyObject *);
typedef iBase_EntitySetHandle (*getsetfunc)(PyObject *);
typedef iBase_TagHandle (*gettagfunc)(PyObject *);

typedef char (*typetochfunc)(enum iBase_TagValueType t);
typedef int (*typetotnfunc)(enum iBase_TagValueType t);

typedef PyObject * (*arrgetfunc)(PyObject *);
typedef PyObject * (*arrcreatefunc)(PyObject *,void *);
typedef void (*regfunc)(int,PyTypeObject *,PyTypeObject *,arrgetfunc,
                        arrcreatefunc);

typedef struct
{
    PyObject_HEAD
    void *memory;
} ArrDealloc_Object;

typedef ArrDealloc_Object* (*arr_func)(void *);

#define ArrDealloc_Check(o)                             \
  PyObject_TypeCheck((PyObject*)(o),&ArrDealloc_Type)

typedef struct
{
    PyObject_HEAD
    iBase_Instance handle;
} iBase_Object;

#define iBase_Check(o)                                  \
    PyObject_TypeCheck((PyObject*)(o),&iBase_Type)

typedef struct
{
    PyObject_HEAD
    iBase_EntityHandle handle;
} iBaseEntity_Object;

#define iBaseEntity_New()                               \
    PyObject_AllocNew(iBaseEntity_Object,&iBaseEntity_Type)

#define iBaseEntity_Check(o)                            \
    PyObject_TypeCheck((PyObject*)(o),&iBaseEntity_Type)

#define iBaseEntity_GET_HANDLE(o)                       \
    ((iBaseEntity_Object*)(o))->handle

typedef struct
{
    PyObject_HEAD
    iBase_EntitySetHandle handle;
} iBaseEntitySet_Object;

#define iBaseEntitySet_New()                            \
    PyObject_AllocNew(iBaseEntitySet_Object,&iBaseEntitySet_Type)

#define iBaseEntitySet_Check(o)                         \
  PyObject_TypeCheck((PyObject*)(o),&iBaseEntitySet_Type)

#define iBaseEntitySet_GET_HANDLE(o)                    \
  ((iBaseEntitySet_Object*)(o))->handle

typedef struct
{
    PyObject_HEAD
    iBase_TagHandle handle;
} iBaseTag_Object;

#define iBaseTag_New()                                  \
    PyObject_AllocNew(iBaseTag_Object,&iBaseTag_Type)

#define iBaseTag_Check(o)                               \
    PyObject_TypeCheck((PyObject*)(o),&iBaseTag_Type)

#define iBaseTag_GET_HANDLE(o)                          \
    ((iBaseTag_Object*)(o))->handle

typedef struct
{
    int dtype;
    PyTypeObject *inst_type;
    PyTypeObject *el_type;
    arrgetfunc getter;
    arrcreatefunc creator;
} subarray_t;

typedef struct
{
    PyArrayObject array;
    PyObject *instance;
    subarray_t *funcs;
} iBaseArr_Object;

#define iBaseArr_Check(o)                               \
    PyObject_TypeCheck((PyObject*)(o),&iBaseArr_Type)

#define iBaseArr_GET_INSTANCE(o)                        \
    ((iBaseArr_Object*)(o))->instance


typedef struct
{
    PyObject *base;
    void *data;
    int alloc;
    int size;
} iBase_OutArray;

typedef int (*bufcvtfunc)(PyObject *,iBase_OutArray *);
typedef PyObject * (*basearrfunc)(int,npy_intp *,int,iBase_OutArray *,
                                  iBase_Object *);


#define PASS_OUTARR(type,arr) (type**)&(arr).data,&(arr).alloc,&(arr).size
#define PASS_OUTARR_ENT(arr) PASS_OUTARR(iBase_EntityHandle,arr)
#define PASS_OUTARR_SET(arr) PASS_OUTARR(iBase_EntitySetHandle,arr)
#define PASS_OUTARR_TAG(arr) PASS_OUTARR(iBase_TagHandle,arr)


#ifndef _IBASE_MODULE

#if defined(PY_IBASE_UNIQUE_SYMBOL)
#define IBase_API PY_IBASE_UNIQUE_SYMBOL
#endif

#if defined(NO_IMPORT) || defined(NO_IMPORT_IBASE)
extern void **IBase_API;
#elif defined(PY_IBASE_UNIQUE_SYMBOL)
void **IBase_API;
#else
static void **IBase_API = NULL;
#endif

#define PyExc_ITAPSError           ( (PyObject*)    IBase_API[ 0])
#define PyExc_Errors               ( (PyObject**)   IBase_API[ 1])
#define ArrDealloc_Type            (*(PyTypeObject*)IBase_API[ 2])
#define ArrDealloc_New             ( (arr_func)     IBase_API[ 3])
#define iBase_Type                 (*(PyTypeObject*)IBase_API[ 4])
#define iBaseEntity_Type           (*(PyTypeObject*)IBase_API[ 5])
#define iBaseEntitySet_Type        (*(PyTypeObject*)IBase_API[ 6])
#define iBaseTag_Type              (*(PyTypeObject*)IBase_API[ 7])
#define iBaseEntity_FromHandle     ( (fromentfunc)  IBase_API[ 8])
#define iBaseEntitySet_FromHandle  ( (fromsetfunc)  IBase_API[ 9])
#define iBaseTag_FromHandle        ( (fromtagfunc)  IBase_API[10])
#define iBaseEntity_GetHandle      ( (getentfunc)   IBase_API[11])
#define iBaseEntitySet_GetHandle   ( (getsetfunc)   IBase_API[12])
#define iBaseTag_GetHandle         ( (gettagfunc)   IBase_API[13])
#define NPY_IBASEENT               (*(int*)         IBase_API[14])
#define NPY_IBASEENTSET            (*(int*)         IBase_API[15])
#define NPY_IBASETAG               (*(int*)         IBase_API[16])
#define iBaseType_Cvt              ( (cvtfunc)      IBase_API[17])
#define iBaseStorageOrder_Cvt      ( (cvtfunc)      IBase_API[18])
#define iBaseTagType_Cvt           ( (cvtfunc)      IBase_API[19])
#define iBaseBuffer_Cvt            ( (bufcvtfunc)   IBase_API[20])
#define iBaseTagType_ToChar        ( (typetochfunc) IBase_API[21])
#define iBaseTagType_ToTypenum     ( (typetotnfunc) IBase_API[22])
#define iBase_RegisterSubArray     ( (regfunc)      IBase_API[23])
#define PyArray_NewFromOutBase     ( (basearrfunc)  IBase_API[24])


#if !defined(NO_IMPORT_IBASE) && !defined(NO_IMPORT)
static int import_iBase(void)
{
    PyObject *module = PyImport_ImportModule("itaps.iBase");
    PyObject *c_api = NULL;

    if(module == NULL)
        return -1;

    c_api = PyObject_GetAttrString(module,"_C_API");
    if(c_api == NULL)
    {
        Py_DECREF(module);
        return -1;
    }

    if(PyCObject_Check(c_api))
        IBase_API = (void **)PyCObject_AsVoidPtr(c_api);

    Py_DECREF(c_api);
    Py_DECREF(module);

    if(IBase_API == NULL)
        return -1;
    return 0;
}
#endif

#endif

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif
