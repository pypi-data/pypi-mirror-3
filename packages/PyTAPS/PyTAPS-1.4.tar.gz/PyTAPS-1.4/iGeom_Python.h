#ifndef PYTAPS_IGEOM_PYTHON_H
#define PYTAPS_IGEOM_PYTHON_H

#include <Python.h>
#include <iGeom.h>
#include "iBase_Python.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct
{
    PyObject_HEAD
    iGeom_Instance handle;
    int owned;
} iGeom_Object;

#define iGeom_Check(o)                                 \
    PyObject_TypeCheck((PyObject*)(o),&iGeom_Type)

typedef struct
{
    PyObject_HEAD
    iGeom_Object *instance;
    int is_arr;
    union
    {
        iBase_EntityIterator    one;
        iBase_EntityArrIterator arr;
    } iter;
} iGeomIter_Object;

typedef struct
{
    iBaseEntitySet_Object base;
    iGeom_Object *instance;
} iGeomEntitySet_Object;

#define iGeomEntitySet_New()                            \
    PyObject_AllocNew(iGeomEntitySet_Object,&iGeomEntitySet_Type)

#define iGeomEntitySet_Check(o)                         \
    PyObject_TypeCheck((PyObject*)(o),&iGeomEntitySet_Type)

#define iGeomEntitySet_GET_INSTANCE(o)                  \
    ( ((iGeomEntitySet_Object*)(o))->instance )

typedef struct
{
    iBaseTag_Object base;
    iGeom_Object *instance;
} iGeomTag_Object;

#define iGeomTag_New()                                  \
    PyObject_AllocNew(iGeomTag_Object,&iGeomTag_Type)

#define iGeomTag_Check(o)                               \
    PyObject_TypeCheck((PyObject*)(o),&iGeomTag_Type)

#define iGeomTag_GET_INSTANCE(o)                        \
    ( ((iGeomTag_Object*)(o))->instance )

enum iGeomExt_Basis
{
    iGeomExt_XYZ,
    iGeomExt_UV,
    iGeomExt_U
};

typedef PyObject * (*geomfrominstfunc)(iGeom_Instance);
typedef PyObject * (*geomfromsetfunc)(iGeom_Object *,iBase_EntitySetHandle);
typedef PyObject * (*geomfromtagfunc)(iGeom_Object *,iBase_TagHandle);
typedef iGeom_Object * (*geomgetinstfunc)(PyObject *o);

#ifndef _IGEOM_MODULE

#if defined(PY_IGEOM_UNIQUE_SYMBOL)
#define IGeom_API PY_IGEOM_UNIQUE_SYMBOL
#endif

#if defined(NO_IMPORT) || defined(NO_IMPORT_IGEOM)
extern void **IGeom_API;
#elif defined(PY_IGEOM_UNIQUE_SYMBOL)
void **IGeom_API;
#else
static void **IGeom_API = NULL;
#endif

#define iGeom_Type                 (*(PyTypeObject*)   IGeom_API[ 0])
#define iGeomIter_Type             (*(PyTypeObject*)   IGeom_API[ 1])
#define iGeomEntitySet_Type        (*(PyTypeObject*)   IGeom_API[ 2])
#define iGeomTag_Type              (*(PyTypeObject*)   IGeom_API[ 3])
#define iGeom_FromInstance         ( (geomfrominstfunc)IGeom_API[ 4])
#define iGeomEntitySet_FromHandle  ( (geomfromsetfunc) IGeom_API[ 5])
#define iGeomEntitySet_GetInstance ( (geomgetinstfunc) IGeom_API[ 6])
#define iGeomTag_FromHandle        ( (geomfromtagfunc) IGeom_API[ 7])
#define iGeomTag_GetInstance       ( (geomgetinstfunc) IGeom_API[ 8])
#define NormalPl_Type              (*(PyTypeObject*)   IGeom_API[ 9])
#define FaceEval_Type              (*(PyTypeObject*)   IGeom_API[10])
#define EdgeEval_Type              (*(PyTypeObject*)   IGeom_API[11])
#define Deriv1st_Type              (*(PyTypeObject*)   IGeom_API[12])
#define Deriv2nd_Type              (*(PyTypeObject*)   IGeom_API[13])
#define Intersect_Type             (*(PyTypeObject*)   IGeom_API[14])
#define Tolerance_Type             (*(PyTypeObject*)   IGeom_API[15])
#define iGeomBasis_Cvt             ( (cvtfunc)         IGeom_API[16])


#if !defined(NO_IMPORT_IGEOM) && !defined(NO_IMPORT)
static int import_iGeom(void)
{
    PyObject *module = PyImport_ImportModule("itaps.iGeom");
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
        IGeom_API = (void **)PyCObject_AsVoidPtr(c_api);

    Py_DECREF(c_api);
    Py_DECREF(module);

    if(IGeom_API == NULL)
        return -3;
    return 0;
}
#endif

#endif


#ifdef __cplusplus
} /* extern "C" */
#endif

#endif
