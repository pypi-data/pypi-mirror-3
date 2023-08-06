#ifndef PYTAPS_IREL_PYTHON_H
#define PYTAPS_IREL_PYTHON_H

#include <Python.h>
#include <iRel.h>
#include "iBase_Python.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct
{
    PyObject_HEAD
    iRel_Instance handle;
    int owned;
} iRel_Object;

#define iRel_Check(o)                                  \
    PyObject_TypeCheck((PyObject*)(o),&iRel_Type)

typedef struct
{
    PyObject_HEAD
    struct iRelPair_Object *parent;
    int side;
} iRelPairSide_Object;

typedef struct iRelPair_Object
{
    PyObject_HEAD
    iRel_PairHandle handle;
    iRel_Object *instance;
    iBase_Object *related[2];
    iRelPairSide_Object *sides[2];
} iRelPair_Object;

#define iRelPairSide_New()                              \
    PyObject_New(iRelPairSide_Object,&iRelPairSide_Type)

#define iRelPairSide_Check(o)                           \
    PyObject_TypeCheck((PyObject*)(o),&iRelPairSide_Type)

#define iRelPair_New()                                  \
    PyObject_New(iRelPair_Object,&iRelPair_Type)

#define iRelPair_Check(o)                               \
    PyObject_TypeCheck((PyObject*)(o),&iRelPair_Type)

#define iRelPair_GET_INSTANCE(o)                        \
    ( ((iRelPair_Object*)(o))->instance )

#define iRelPair_GET_HANDLE(o)                          \
    ((iRelPair_Object*)(o))->handle

typedef PyObject * (*relfrominstfunc)(iRel_Instance);

#ifndef _IREL_MODULE

#if defined(PY_IREL_UNIQUE_SYMBOL)
#define IRel_API PY_IREL_UNIQUE_SYMBOL
#endif

#if defined(NO_IMPORT) || defined(NO_IMPORT_IREL)
extern void **IRel_API;
#elif defined(PY_IREL_UNIQUE_SYMBOL)
void **IRel_API;
#else
static void **IRel_API = NULL;
#endif

#define iRel_Type         (*(PyTypeObject*)  IRel_API[0])
#define iRelPair_Type     (*(PyTypeObject*)  IRel_API[1])
#define iRelPairSide_Type (*(PyTypeObject*)  IRel_API[2])
#define iRel_FromInstance ( (relfrominstfunc)IRel_API[3])


#if !defined(NO_IMPORT_IREL) && !defined(NO_IMPORT)
static int import_iRel(void)
{
    PyObject *module = PyImport_ImportModule("itaps.iRel");
    PyObject *c_api = NULL;

    if(module == NULL)
        return -1;

    c_api = PyObject_GetAttrString(module,"_C_API");
    if(c_api == NULL)
    {
        Py_DECREF(module);
        return -2;
    }

    if(PyCObject_Check(c_api))
        IRel_API = (void **)PyCObject_AsVoidPtr(c_api);

    Py_DECREF(c_api);
    Py_DECREF(module);

    if(IRel_API == NULL)
        return -3;
    return 0;
}
#endif

#endif


#ifdef __cplusplus
} // extern "C"
#endif

#endif
