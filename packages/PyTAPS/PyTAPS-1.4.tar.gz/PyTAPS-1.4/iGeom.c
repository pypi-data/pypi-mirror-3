#define _IGEOM_MODULE
#include "iGeom_Python.h"
#include "iGeom_doc.h"
#include "errors.h"
#include "common.h"
#include "helpers.h"
#include "numpy_extensions.h"

#include <numpy/ufuncobject.h>

static PyTypeObject *NormalPl_Type_;
static PyTypeObject *FaceEval_Type_;
static PyTypeObject *EdgeEval_Type_;
static PyTypeObject *Deriv1st_Type_;
static PyTypeObject *Deriv2nd_Type_;
static PyTypeObject *Intersect_Type_;
static PyTypeObject *Tolerance_Type_;
static PyTypeObject *MinMax_Type_;

#define NormalPl_Type *NormalPl_Type_
#define FaceEval_Type *FaceEval_Type_
#define EdgeEval_Type *EdgeEval_Type_
#define Deriv1st_Type *Deriv1st_Type_
#define Deriv2nd_Type *Deriv2nd_Type_
#define Intersect_Type *Intersect_Type_
#define Tolerance_Type *Tolerance_Type_
#define MinMax_Type *MinMax_Type_

static PyTypeObject iGeom_Type;
static PyTypeObject iGeomIter_Type;
static PyTypeObject iGeomEntitySet_Type;
static PyTypeObject iGeomTag_Type;

/* automatic method/property declarators */
#define IGEOM_METHOD(cls, name, type)                    \
    { #name, (PyCFunction)(cls ## Obj_ ## name), (type), \
      IGEOMDOC_ ## cls ## _ ## name }

#define IGEOM_GET(cls, name)                      \
    { #name, (getter)(cls ## Obj_get ## name), 0, \
      IGEOMDOC_ ## cls ## _ ## name, 0 }

#define IGEOM_GETSET(cls, name)                \
    { #name, (getter)(cls ## Obj_get ## name), \
             (setter)(cls ## Obj_set ## name), \
      IGEOMDOC_ ## cls ## _ ## name, 0 }

static int
checkError(iGeom_Instance geom,int err)
{
    if(err)
    {
        char descr[120];
        iGeom_getDescription(geom,descr,sizeof(descr)-1);
        PyErr_SetString(PyExc_Errors[err-1],descr);
        return 1;
    }
    else
        return 0;
}

static int
iGeomBasis_Cvt(PyObject *object,int *val)
{
    int tmp = PyInt_AsLong(object);
    if(PyErr_Occurred())
        return 0;
    if(tmp < iGeomExt_XYZ || tmp > iGeomExt_U)
    {
        PyErr_SetString(PyExc_ValueError,ERR_INVALID_STG);
        return 0;
    }

    *val = tmp;
    return 1;
}

static enum iGeomExt_Basis
infer_basis(iGeom_Instance instance,iBase_EntityHandle entity)
{
    int type,err;
    iGeom_getEntType(instance,entity,&type,&err);
    if(checkError(instance,err))
        return -1;

    if(type == iBase_EDGE)
        return iGeomExt_U;
    else if(type == iBase_FACE)
        return iGeomExt_UV;

    PyErr_SetString(PyExc_ValueError,ERR_INFER_BASIS);
    return -1;
}

static int
get_dimension(enum iGeomExt_Basis basis)
{
    switch(basis)
    {
    case iGeomExt_XYZ:
        return 3;
    case iGeomExt_UV:
        return 2;
    case iGeomExt_U:
        return 1;
    default:
        return -1;
    }
}

static int
get_entity_data(PyObject *obj,PyObject **array,iBase_EntityHandle **entities,
                int *size)
{
    if((*array = PyArray_TryFromObject(obj,NPY_IBASEENT,1,1)) != NULL)
    {
        *entities = PyArray_DATA(*array);
        *size = PyArray_SIZE(*array);
    }
    else if(iBaseEntity_Check(obj))
    {
        *entities = &iBaseEntity_GET_HANDLE(obj);
        *size = 1;
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return 0;
    }
    return 1;
}

static PyObject *
iGeom_FromInstance(iGeom_Instance instance)
{
    iGeom_Object *o = PyObject_AllocNew(iGeom_Object,&iGeom_Type);
    if(o == NULL)
        return NULL;

    o->handle = instance;
    o->owned = 0;
    return (PyObject*)o;
}

static PyObject *
iGeomEntitySet_FromHandle(iGeom_Object *instance,iBase_EntitySetHandle handle)
{
    iGeomEntitySet_Object *o = iGeomEntitySet_New();
    if(o == NULL)
        return NULL;

    o->instance = instance;
    o->base.handle = handle;
    Py_INCREF(o->instance);
    return (PyObject*)o;
}

static iGeom_Object *
iGeomEntitySet_GetInstance(PyObject *o)
{
    if(iGeomEntitySet_Check(o))
        return iGeomEntitySet_GET_INSTANCE(o);

    if(o == NULL)
        PyErr_BadArgument();
    else
        PyErr_SetString(PyExc_TypeError,"iGeom.EntitySet is required");
    return NULL;
}

static PyObject *
iGeomTag_FromHandle(iGeom_Object *instance,iBase_TagHandle handle)
{
    iGeomTag_Object *o = iGeomTag_New();
    if(o == NULL)
        return NULL;

    o->instance = instance;
    o->base.handle = handle;
    Py_INCREF(o->instance);
    return (PyObject*)o;
}

static iGeom_Object *
iGeomTag_GetInstance(PyObject *o)
{
    if(iGeomTag_Check(o))
        return iGeomTag_GET_INSTANCE(o);

    if(o == NULL)
        PyErr_BadArgument();
    else
        PyErr_SetString(PyExc_TypeError,"iGeom.Tag is required");
    return NULL;
}

static int
iGeomObj_init(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"options",0};
    int err;
    const char *options = "";

    if(!PyArg_ParseTupleAndKeywords(args,kw,"|s",kwlist,&options))
        return -1;

    /* __init__ can be called multiple times, so destroy the old interface
       if necessary */
    if(self->handle && self->owned)
    {
        iGeom_dtor(self->handle,&err);
        if(checkError(self->handle,err))
            return -1;
    }
    iGeom_newGeom(options,&self->handle,&err,strlen(options));
    if(checkError(self->handle,err))
        return -1;
    self->owned = 1;
    return 0;
}

static void
iGeomObj_dealloc(iGeom_Object *self)
{
    if(self->handle && self->owned)
    {
        int err;
        iGeom_dtor(self->handle,&err);
    }
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
iGeomObj_getrootSet(iGeom_Object *self,void *closure)
{
    int err;
    iBase_EntitySetHandle handle;

    iGeom_getRootSet(self->handle,&handle,&err);
    if(checkError(self->handle,err))
        return NULL;

    return iGeomEntitySet_FromHandle(self,handle);
}

static PyObject *
iGeomObj_getboundBox(iGeom_Object *self,void *closure)
{
    int err;
    double *box = malloc(sizeof(double)*6);

    iGeom_getBoundBox(self->handle,box+0,box+1,box+2,box+3,box+4,box+5,&err);
    if(checkError(self->handle,err))
    {
        free(box);
        return NULL;
    }

    npy_intp dims[] = {2,3};
    return PyArray_NewFromMalloc(2,dims,NPY_DOUBLE,box);
}

static PyObject *
iGeomObj_gettopoLevel(iGeom_Object *self,void *closure)
{
    int level,err;
    iGeom_getTopoLevel(self->handle,&level,&err);
    if(checkError(self->handle,err))
        return NULL;

    return PyInt_FromLong(level);
}

static PyObject *
iGeomObj_getparametric(iGeom_Object *self,void *closure)
{
    int parametric,err;

    iGeom_getParametric(self->handle,&parametric,&err);
    if(checkError(self->handle,err))
        return NULL;
    return PyBool_FromLong(parametric);
}

static PyObject *
iGeomObj_gettolerance(iGeom_Object *self,void *closure)
{
    int err;
    int type;
    double tolerance;

    iGeom_getTolerance(self->handle,&type,&tolerance,&err);
    if(checkError(self->handle,err))
        return NULL;
    return NamedTuple_New(&Tolerance_Type,"(id)",
        PyInt_FromLong(type),
        PyFloat_FromDouble(tolerance)
        );
}

static PyObject *
iGeomObj_load(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"filename","options",0};
    int err;
    const char *name = NULL;
    const char *options = "";

    if(!PyArg_ParseTupleAndKeywords(args,kw,"s|s",kwlist,&name,&options))
        return NULL;

    iGeom_load(self->handle,name,options,&err,strlen(name),strlen(options));
    if(checkError(self->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_save(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"filename","options",0};
    int err;
    const char *name = NULL;
    const char *options = "";

    if(!PyArg_ParseTupleAndKeywords(args,kw,"s|s",kwlist,&name,&options))
        return NULL;

    iGeom_save(self->handle,name,options,&err,strlen(name),strlen(options));
    if(checkError(self->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_createSphere(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"radius",0};
    int err;
    double radius;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"d",kwlist,&radius))
        return NULL;

    iBaseEntity_Object *entity = iBaseEntity_New();
    iGeom_createSphere(self->handle,radius,&entity->handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF(entity);
        return NULL;
    }
    return (PyObject*)entity;
}

static PyObject *
iGeomObj_createBrick(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"dimensions",0};
    int err;
    PyObject *in_vec,*vec;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&in_vec))
        in_vec = args;

    vec = PyArray_ToVectors(in_vec,NPY_DOUBLE,1,3,0);
    if(vec == NULL)
        return NULL;

    double *v = PyArray_DATA(vec);
    iBaseEntity_Object *entity = iBaseEntity_New();

    iGeom_createBrick(self->handle,v[0],v[1],v[2],&entity->handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF(entity);
        return NULL;
    }
    return (PyObject*)entity;
}

static PyObject *
iGeomObj_createCylinder(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"height","major_rad","minor_rad",0};
    int err;
    double height,major_rad,minor_rad;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"ddd",kwlist,&height,&major_rad,
                                    &minor_rad))
        return NULL;

    iBaseEntity_Object *entity = iBaseEntity_New();
    iGeom_createCylinder(self->handle,height,major_rad,minor_rad,
                         &entity->handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF(entity);
        return NULL;
    }
    return (PyObject*)entity;
}

static PyObject *
iGeomObj_createPrism(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"height","sides","major_rad","minor_rad",0};
    int err;
    double height,major_rad,minor_rad;
    int sides;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"didd",kwlist,&height,&sides,
                                    &major_rad,&minor_rad))
        return NULL;

    iBaseEntity_Object *entity = iBaseEntity_New();
    iGeom_createPrism(self->handle,height,sides,major_rad,minor_rad,
                      &entity->handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF(entity);
        return NULL;
    }
    return (PyObject*)entity;
}

static PyObject *
iGeomObj_createCone(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"height","major_rad","minor_rad","top_rad",0};
    int err;
    double height,major_rad,minor_rad,top_rad;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"dddd",kwlist,&height,&major_rad,
                                    &minor_rad,&top_rad))
        return NULL;

    iBaseEntity_Object *entity = iBaseEntity_New();
    iGeom_createCone(self->handle,height,major_rad,minor_rad,top_rad,
                     &entity->handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF(entity);
        return NULL;
    }
    return (PyObject*)entity;
}

static PyObject *
iGeomObj_createTorus(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"major_rad","minor_rad",0};
    int err;
    double major_rad,minor_rad;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"dd",kwlist,&major_rad,&minor_rad))
        return NULL;

    iBaseEntity_Object *entity = iBaseEntity_New();
    iGeom_createTorus(self->handle,major_rad,minor_rad,&entity->handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF(entity);
        return NULL;
    }
    return (PyObject*)entity;
}

static PyObject *
iGeomObj_deleteAll(iGeom_Object *self)
{
    int err;
    iGeom_deleteAll(self->handle,&err);
    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_deleteEnt(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity",0};
    int err;
    PyObject *in_ents;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&in_ents))
        return NULL;

    /*ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        int size = PyArray_SIZE(ents);
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        iGeom_deleteEntArr(self->handle,entities,size,&err);
        Py_DECREF(ents);
    }
    else*/ if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        iGeom_deleteEnt(self->handle,entity,&err);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }

    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_getVtxCoords(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"src","dest","storage_order","out",0};
    int err;
    PyObject *in_src,*src;
    PyObject *in_dst = NULL, *dst = NULL;
    enum iGeomExt_Basis dst_basis = -1;
    int storage_order = iBase_INTERLEAVED;

    iBase_OutArray coords = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|OO&O&",kwlist,&in_src,&in_dst,
                                    iBaseStorageOrder_Cvt,&storage_order,
                                    iBaseBuffer_Cvt,&coords))
        return NULL;
    if(in_dst && PyTuple_Check(in_dst))
    {
        if(!PyArg_ParseTuple(in_dst,"OO&",&in_dst,iGeomBasis_Cvt,&dst_basis))
            return NULL;
    }

    iBase_EntityHandle *src_entities;
    int src_size;
    iBase_EntityHandle *dst_entities = NULL;
    int dst_size = 0;

    if(!get_entity_data(in_src,&src,&src_entities,&src_size))
        goto err;

    if(in_dst)
    {
        if(!get_entity_data(in_dst,&dst,&dst_entities,&dst_size))
            goto err;

        if(dst_basis == -1 && (dst_basis = infer_basis(self->handle,
           dst_entities[0])) == -1)
            goto err;
    }
    else
        dst_basis = iGeomExt_XYZ;


    if(src || dst)
    {
        if(dst_basis == iGeomExt_XYZ)
            iGeom_getVtxArrCoords(self->handle,src_entities,src_size,
                                  storage_order,PASS_OUTARR(double,coords),
                                  &err);
        else if(dst_basis == iGeomExt_UV)
            iGeom_getVtxArrToUV(self->handle,src_entities,src_size,dst_entities,
                                dst_size,storage_order,
                                PASS_OUTARR(double,coords),&err);
        else /* iGeomExt_U */
            iGeom_getVtxArrToU(self->handle,src_entities,src_size,dst_entities,
                               dst_size,PASS_OUTARR(double,coords),&err);

        Py_XDECREF(src);
        Py_XDECREF(dst);

        if(checkError(self->handle,err))
            return NULL;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = get_dimension(dst_basis);
        dims[!vec_index] = coords.size/get_dimension(dst_basis);
        return PyArray_NewFromOut(2,dims,NPY_DOUBLE,&coords);
    }
    else
    {
        double *v = malloc(get_dimension(dst_basis)*sizeof(double));

        if(dst_basis == iGeomExt_XYZ)
            iGeom_getVtxCoord(self->handle,src_entities[0],v+0,v+1,v+2,&err);
        else if(dst_basis == iGeomExt_UV)
            iGeom_getVtxToUV(self->handle,src_entities[0],dst_entities[0],
                             v+0,v+1,&err);
        else /* iGeomExt_U */
            iGeom_getVtxToU(self->handle,src_entities[0],dst_entities[0],v+0,
                            &err);

        if(checkError(self->handle,err))
        {
            free(v);
            return NULL;
        }

        npy_intp dims[] = {get_dimension(dst_basis)};
        return PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,v);
    }

err:
    Py_XDECREF(src);
    Py_XDECREF(dst);
    return NULL;
}

static PyObject *
iGeomObj_getEntCoords(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    /* TODO: add hint */
    static char *kwlist[] = {"coords","src","dest","storage_order","out",0};
    int err;
    PyObject *in_verts,*verts;
    PyObject *in_src = NULL, *src = NULL;
    PyObject *in_dst = NULL, *dst = NULL;
    enum iGeomExt_Basis src_basis = -1;
    enum iGeomExt_Basis dst_basis = -1;
    int storage_order = iBase_INTERLEAVED;

    iBase_OutArray dst_coords = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|OOO&O&",kwlist,&in_verts,&in_src,
                                    &in_dst,iBaseStorageOrder_Cvt,
                                    &storage_order,iBaseBuffer_Cvt,&dst_coords))
        return NULL;

    /***** 1: parse src/dest *****/
    if(in_src == NULL && in_dst == NULL)
    {
        PyErr_SetString(PyExc_ValueError,ERR_NO_SRC_DST);
        return NULL;
    }

    if(in_src && PyTuple_Check(in_src))
    {
        if(!PyArg_ParseTuple(in_src,"OO&",&in_src,iGeomBasis_Cvt,&src_basis))
            return NULL;
    }
    if(in_dst && PyTuple_Check(in_dst))
    {
        if(!PyArg_ParseTuple(in_dst,"OO&",&in_dst,iGeomBasis_Cvt,&dst_basis))
            return NULL;
    }

    /***** 2: extract verts/entities *****/
    iBase_EntityHandle *src_entities;
    int src_size;
    iBase_EntityHandle *dst_entities;
    int dst_size;

    if((verts = PyArray_TryFromObject(in_verts,NPY_DOUBLE,1,2)) == NULL)
    {
        PyErr_SetString(PyExc_ValueError,ERR_ARR_DIMS);
        return NULL;
    }

    double *src_coords = PyArray_DATA(verts);
    int src_coord_size = PyArray_SIZE(verts);

    if(in_src)
    {
        if(!get_entity_data(in_src,&src,&src_entities,&src_size))
            goto err;

        if(src_basis == -1 && (src_basis = infer_basis(self->handle,
           src_entities[0])) == -1)
            goto err;
    }
    else
        src_basis = iGeomExt_XYZ;

    if(in_dst)
    {
        if(!get_entity_data(in_dst,&dst,&dst_entities,&dst_size))
            goto err;

        if(dst_basis == -1 && (dst_basis = infer_basis(self->handle,
           dst_entities[0])) == -1)
            goto err;
    }
    else
        dst_basis = iGeomExt_XYZ;

    if(src_basis == dst_basis)
    {
        PyErr_SetString(PyExc_ValueError,ERR_INVALID_BASIS);
        return NULL;
    }

    /***** 3: determine which form to use (array vs. single) *****/
    if(PyArray_NDIM(verts) == 2 || src || dst)
    {
        /***** 4a: validate vertex data *****/
        if(PyArray_NDIM(verts) == 2 && !PyArray_CheckVectors(verts,2,
           get_dimension(src_basis),storage_order==iBase_INTERLEAVED))
            goto err;
        if(PyArray_NDIM(verts) == 1 && !PyArray_CheckVectors(verts,1,
           get_dimension(src_basis),0))
            goto err;

        /***** 5a: find and call the appropriate function *****/
        if(src_basis == iGeomExt_XYZ)
        {
            if(dst_basis == iGeomExt_UV)
                iGeom_getArrXYZtoUV(self->handle,dst_entities,dst_size,
                                    storage_order,src_coords,src_coord_size,
                                    PASS_OUTARR(double,dst_coords),&err);
            else /* iGeomExt_U */
                iGeom_getArrXYZtoU(self->handle,dst_entities,dst_size,
                                   storage_order,src_coords,src_coord_size,
                                   PASS_OUTARR(double,dst_coords),&err);
        }
        else if(src_basis == iGeomExt_UV)
        {
            if(dst_basis == iGeomExt_XYZ)
                iGeom_getArrUVtoXYZ(self->handle,src_entities,src_size,
                                    storage_order,src_coords,src_coord_size,
                                    PASS_OUTARR(double,dst_coords),&err);
            else /* iGeomExt_U */
            {
                goto err; /* not currently supported */
            }
        }
        else /* iGeomExt_U */
        {
            if(dst_basis == iGeomExt_XYZ)
                iGeom_getArrUtoXYZ(self->handle,src_entities,src_size,
                                   src_coords,src_coord_size,storage_order,
                                   PASS_OUTARR(double,dst_coords),&err);
            else /* iGeomExt_UV */
                iGeom_getArrUtoUV(self->handle,src_entities,src_size,
                                  dst_entities,dst_size,
                                  src_coords,src_coord_size,storage_order,
                                  PASS_OUTARR(double,dst_coords),&err);
        }
        Py_DECREF(verts);
        Py_XDECREF(src);
        Py_XDECREF(dst);

        if(checkError(self->handle,err))
            return NULL;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = get_dimension(dst_basis);
        dims[!vec_index] = dst_coords.size/get_dimension(dst_basis);
        return PyArray_NewFromOut(2,dims,NPY_DOUBLE,&dst_coords);
    }
    else
    {
        /***** 4b: validate vertex data *****/
        if(!PyArray_CheckVectors(verts,1,get_dimension(src_basis),0))
            goto err;

        double *dst_coords = malloc(get_dimension(dst_basis)*sizeof(double));

        /***** 5b: find and call the appropriate function *****/
        if(src_basis == iGeomExt_XYZ)
        {
            if(dst_basis == iGeomExt_UV)
                iGeom_getEntXYZtoUV(self->handle,dst_entities[0],
                                    src_coords[0],src_coords[1],src_coords[2],
                                    dst_coords+0, dst_coords+1,
                                    &err);
            else /* iGeomExt_U */
                iGeom_getEntXYZtoU(self->handle,dst_entities[0],
                                   src_coords[0],src_coords[1],src_coords[2],
                                   dst_coords+0,
                                   &err);
        }
        else if(src_basis == iGeomExt_UV)
        {
            if(dst_basis == iGeomExt_XYZ)
                iGeom_getEntUVtoXYZ(self->handle,src_entities[0],
                                    src_coords[0],src_coords[1],
                                    dst_coords+0, dst_coords+1, dst_coords+2,
                                    &err);
            else /* iGeomExt_U */
            {
                goto err; /* not currently supported */
            }
        }
        else /* iGeomExt_U */
        {
            if(dst_basis == iGeomExt_XYZ)
                iGeom_getEntUtoXYZ(self->handle,src_entities[0],
                                   src_coords[0],
                                   dst_coords+0, dst_coords+1, dst_coords+2,
                                   &err);
            else /* iGeomExt_UV */
                iGeom_getEntUtoUV(self->handle,src_entities[0],dst_entities[0],
                                  src_coords[0],
                                  dst_coords+0, dst_coords+1,
                                  &err);
        }

        if(checkError(self->handle,err))
        {
            free(dst_coords);
            return NULL;
        }

        npy_intp dims[] = {get_dimension(dst_basis)};
        return PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,dst_coords);
    }

err:
    Py_XDECREF(verts);
    Py_XDECREF(src);
    Py_XDECREF(dst);
    return NULL;
}

static PyObject *
iGeomObj_measure(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","out",0};
    int err;
    PyObject *in_ents,*ents;

    iBase_OutArray measures = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&",kwlist,&in_ents,
                                    iBaseBuffer_Cvt,&measures))
        return NULL;

    ents = PyArray_FROMANY(in_ents,NPY_IBASEENT,1,1,NPY_C_CONTIGUOUS);
    if(ents == NULL)
        return NULL;

    iBase_EntityHandle *entities = PyArray_DATA(ents);
    int ent_size = PyArray_SIZE(ents);

    iGeom_measure(self->handle,entities,ent_size,PASS_OUTARR(double,measures),
                  &err);
    Py_DECREF(ents);

    if(checkError(self->handle,err))
        return NULL;

    npy_intp dims[] = {measures.size};
    return PyArray_NewFromOut(1,dims,NPY_DOUBLE,&measures);
}

static PyObject *
iGeomObj_getEntType(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","out",0};
    int err;
    PyObject *in_ents,*ents;

    iBase_OutArray types = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&",kwlist,&in_ents,
                                    iBaseBuffer_Cvt,&types))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int size = PyArray_SIZE(ents);

        iGeom_getArrType(self->handle,entities,size,PASS_OUTARR(int,types),
                         &err);
        Py_DECREF(ents);
        if(checkError(self->handle,err))
            return NULL;
    
        npy_intp dims[] = {types.size};
        return PyArray_NewFromOut(1,dims,NPY_INT,&types);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        int type;

        iGeom_getEntType(self->handle,entity,&type,&err);
        if(checkError(self->handle,err))
            return NULL;
    
        return PyInt_FromLong(type);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iGeomObj_getFaceType(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity",0};
    int err;
    iBaseEntity_Object *entity;

    char type[512];
    int len = sizeof(type);

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntity_Type,
                                    &entity))
        return NULL;

    iGeom_getFaceType(self->handle,entity->handle,type,&err,&len);
    if(checkError(self->handle,err))
        return NULL;
    return PyString_FromString(type);
}

static PyObject *
iGeomObj_isEntParametric(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","out",0};
    int err;
    PyObject *in_ents,*ents;

    iBase_OutArray param = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&",kwlist,&in_ents,
                                    iBaseBuffer_Cvt,&param))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int size = PyArray_SIZE(ents);

        iGeom_isArrParametric(self->handle,entities,size,PASS_OUTARR(int,param),
                              &err);
        Py_DECREF(ents);

        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {param.size};
        npy_intp strides[] = {sizeof(int)/sizeof(npy_bool)};
        return PyArray_NewFromOutStrided(1,dims,strides,NPY_BOOL,&param);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        int param;

        iGeom_isEntParametric(self->handle,entity,&param,&err);
        if(checkError(self->handle,err))
            return NULL;
        return PyBool_FromLong(param);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iGeomObj_isEntPeriodic(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","out",0};
    int err;
    PyObject *in_ents,*ents;

    iBase_OutArray uv = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&",kwlist,&in_ents,
                                    iBaseBuffer_Cvt,&uv))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int size = PyArray_SIZE(ents);

        iGeom_isArrPeriodic(self->handle,entities,size,PASS_OUTARR(int,uv),
                            &err);
        Py_DECREF(ents);

        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {uv.size/2,2};
        npy_intp strides[] = {0,sizeof(int)/sizeof(npy_bool)};
        return PyArray_NewFromOutStrided(2,dims,strides,NPY_BOOL,&uv);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        int *uv = malloc(sizeof(int)*2);

        iGeom_isEntPeriodic(self->handle,entity,uv+0,uv+1,&err);
        if(checkError(self->handle,err))
        {
            free(uv);
            return NULL;
        }

        npy_intp dims[] = {2};
        npy_intp strides[] = {sizeof(int)/sizeof(npy_bool)};
        return PyArray_NewFromMallocStrided(1,dims,strides,NPY_BOOL,uv);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iGeomObj_isFcDegenerate(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","out",0};
    int err;
    PyObject *in_ents,*ents;

    iBase_OutArray degenerate = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&",kwlist,&in_ents,
                                    iBaseBuffer_Cvt,&degenerate))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int size = PyArray_SIZE(ents);

        iGeom_isFcArrDegenerate(self->handle,entities,size,
                                PASS_OUTARR(int,degenerate),&err);
        Py_DECREF(ents);

        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {degenerate.size};
        npy_intp strides[] = {sizeof(int)/sizeof(npy_bool)};
        return PyArray_NewFromOutStrided(1,dims,strides,NPY_BOOL,&degenerate);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        int degenerate;

        iGeom_isFcDegenerate(self->handle,entity,&degenerate,&err);
        if(checkError(self->handle,err))
            return NULL;
        return PyBool_FromLong(degenerate);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iGeomObj_getEntBoundBox(iGeom_Object *self,PyObject *args,PyObject *kw)
{

    static char *kwlist[] = {"entities","storage_order","out",0};
    int err;
    PyObject *in_ents,*ents;
    int storage_order = iBase_INTERLEAVED;
    PyObject *out = NULL;

    iBase_OutArray min = {0};
    iBase_OutArray max = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&O!",kwlist,&in_ents,
                                    iBaseStorageOrder_Cvt,&storage_order,
                                    &PyTuple_Type,&out))
        return NULL;

    if(out && !PyArg_ParseTuple(out,"O&O&",iBaseBuffer_Cvt,&min,
                                           iBaseBuffer_Cvt,&max))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int size = PyArray_SIZE(ents);

        iGeom_getArrBoundBox(self->handle,entities,size,storage_order,
                             PASS_OUTARR(double,min),PASS_OUTARR(double,max),
                             &err);
        Py_DECREF(ents);
        if(checkError(self->handle,err))
            return NULL;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = 3;
        dims[!vec_index] = min.size/3;
        return NamedTuple_New(&MinMax_Type,"(NN)",
            PyArray_NewFromOut(2,dims,NPY_DOUBLE,&min),
            PyArray_NewFromOut(2,dims,NPY_DOUBLE,&max)
            );
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);

        double *min = malloc(3*sizeof(double));
        double *max = malloc(3*sizeof(double));
        iGeom_getEntBoundBox(self->handle,entity,min+0,min+1,min+2,
                             max+0,max+1,max+2,&err);
        if(checkError(self->handle,err))
        {
            free(min);
            free(max);
            return NULL;
        }

        npy_intp dims[] = {3};
        return NamedTuple_New(&MinMax_Type,"(NN)",
            PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,min),
            PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,max)
            );
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iGeomObj_getEntRange(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","basis","storage_order","out",0};
    int err;
    PyObject *in_ents,*ents;
    enum iGeomExt_Basis basis = -1;
    int storage_order = iBase_INTERLEAVED;
    PyObject *out = NULL;

    iBase_OutArray min = {0};
    iBase_OutArray max = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&O&O!",kwlist,&in_ents,
                                    iGeomBasis_Cvt,&basis,
                                    iBaseStorageOrder_Cvt,&storage_order,
                                    &PyTuple_Type,&out))
        return NULL;

    if(out && !PyArg_ParseTuple(out,"O&O&",iBaseBuffer_Cvt,&min,
                                           iBaseBuffer_Cvt,&max))
        return NULL;

    if(basis == iGeomExt_XYZ)
    {
        PyErr_SetString(PyExc_ValueError,ERR_INVALID_BASIS);
        return NULL;
    }

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int size = PyArray_SIZE(ents);

        if(basis == -1 && (basis = infer_basis(self->handle,entities[0])) == -1)
        {
            Py_DECREF(ents);
            return NULL;
        }

        if(basis == iGeomExt_UV)
            iGeom_getArrUVRange(self->handle,entities,size,storage_order,
                                PASS_OUTARR(double,min),PASS_OUTARR(double,max),
                                &err);
        else
            iGeom_getArrURange(self->handle,entities,size,
                               PASS_OUTARR(double,min),PASS_OUTARR(double,max),
                               &err);
        Py_DECREF(ents);

        if(checkError(self->handle,err))
            return NULL;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = get_dimension(basis);
        dims[!vec_index] = min.size/get_dimension(basis);
        return NamedTuple_New(&MinMax_Type,"(NN)",
            PyArray_NewFromOut(2,dims,NPY_DOUBLE,&min),
            PyArray_NewFromOut(2,dims,NPY_DOUBLE,&max)
            );
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        if(basis == -1 && (basis = infer_basis(self->handle,entity)) == -1)
            return NULL;

        double *min = malloc(get_dimension(basis)*sizeof(double));
        double *max = malloc(get_dimension(basis)*sizeof(double));
        if(basis == iGeomExt_UV)
            iGeom_getEntUVRange(self->handle,entity,min+0,min+1,max+0,max+1,
                                &err);
        else
            iGeom_getEntURange(self->handle,entity,min,max,&err);

        if(checkError(self->handle,err))
        {
            free(min);
            free(max);
            return NULL;
        }

        npy_intp dims[] = {get_dimension(basis)};
        return NamedTuple_New(&MinMax_Type,"(NN)",
            PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,min),
            PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,max)
            );
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iGeomObj_getEntTolerance(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","out",0};
    int err;
    PyObject *in_ents,*ents;

    iBase_OutArray tolerance = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&",kwlist,&in_ents,
                                    iBaseBuffer_Cvt,&tolerance))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int size = PyArray_SIZE(ents);

        iGeom_getArrTolerance(self->handle,entities,size,
                              PASS_OUTARR(double,tolerance),&err);
        Py_DECREF(ents);

        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {tolerance.size};
        return PyArray_NewFromOut(1,dims,NPY_DOUBLE,&tolerance);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        double tol;

        iGeom_getEntTolerance(self->handle,entity,&tol,&err);
        if(checkError(self->handle,err))
            return NULL;
        return PyFloat_FromDouble(tol);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iGeomObj_getEntAdj(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","type","out",0};
    int err;
    PyObject *in_ents,*ents;
    int type_req;
    PyObject *out = NULL;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO&|O",kwlist,&in_ents,
                                    iBaseType_Cvt,&type_req,&out))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int size = PyArray_SIZE(ents);

        iBase_OutArray adj = {0};
        iBase_OutArray offsets = {0};

        if(out && !OffsetListBuffer_Cvt(out,&offsets,1,&adj))
        {
            PyErr_SetString(PyExc_ValueError,ERR_INVALID_OUT);
            return NULL;
        }

        iGeom_getArrAdj(self->handle,entities,size,type_req,
                        PASS_OUTARR_ENT(adj),PASS_OUTARR(int,offsets),&err);
        Py_DECREF(ents);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp adj_dims[] = {adj.size};
        npy_intp off_dims[] = {offsets.size};

        return OffsetList_New(
            PyArray_NewFromOut(1,off_dims,NPY_INT,&offsets),
            PyArray_NewFromOut(1,adj_dims,NPY_IBASEENT,&adj)
            );
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);

        iBase_OutArray adj = {0};

        if(out && !iBaseBuffer_Cvt(out,&adj))
        {
            PyErr_SetString(PyExc_ValueError,ERR_INVALID_OUT);
            return NULL;
        }

        iGeom_getEntAdj(self->handle,entity,type_req,PASS_OUTARR_ENT(adj),&err);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {adj.size};
        return PyArray_NewFromOut(1,dims,NPY_IBASEENT,&adj);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iGeomObj_getEnt2ndAdj(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","bridge_type","type","out",0};
    int err;
    PyObject *in_ents,*ents;
    int bridge_type,type_req;
    PyObject *out = NULL;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO&O&|O",kwlist,&in_ents,
                                    iBaseType_Cvt,&bridge_type,iBaseType_Cvt,
                                    &type_req,&out))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int size = PyArray_SIZE(ents);

        iBase_OutArray adj = {0};
        iBase_OutArray offsets = {0};

        if(out && !OffsetListBuffer_Cvt(out,&offsets,1,&adj))
        {
            PyErr_SetString(PyExc_ValueError,ERR_INVALID_OUT);
            return NULL;
        }

        iGeom_getArr2ndAdj(self->handle,entities,size,bridge_type,type_req,
                           PASS_OUTARR_ENT(adj),PASS_OUTARR(int,offsets),
                           &err);
        Py_DECREF(ents);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp adj_dims[] = {adj.size};
        npy_intp off_dims[] = {offsets.size};

        return OffsetList_New(
            PyArray_NewFromOut(1,off_dims,NPY_INT,&offsets),
            PyArray_NewFromOut(1,adj_dims,NPY_IBASEENT,&adj)
            );
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);

        iBase_OutArray adj = {0};

        if(out && !iBaseBuffer_Cvt(out,&adj))
        {
            PyErr_SetString(PyExc_ValueError,ERR_INVALID_OUT);
            return NULL;
        }

        iGeom_getEnt2ndAdj(self->handle,entity,bridge_type,type_req,
                           PASS_OUTARR_ENT(adj),&err);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {adj.size};
        return PyArray_NewFromOut(1,dims,NPY_IBASEENT,&adj);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iGeomObj_isEntAdj(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities1","entities2","out",0};
    PyObject *in_ents1,*ents1 = NULL;
    PyObject *in_ents2,*ents2 = NULL;
    int err;

    iBase_OutArray adj = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|O&",kwlist,&in_ents1,&in_ents2,
                                    iBaseBuffer_Cvt,&adj))
        return NULL;

    iBase_EntityHandle *entities1;
    int ent1_size;
    iBase_EntityHandle *entities2;
    int ent2_size;

    if(!get_entity_data(in_ents1,&ents1,&entities1,&ent1_size))
        goto err;
    if(!get_entity_data(in_ents2,&ents2,&entities2,&ent2_size))
        goto err;

    if(ents1 || ents2)
    {
        iGeom_isArrAdj(self->handle,entities1,ent1_size,entities2,ent2_size,
                       PASS_OUTARR(int,adj),&err);
        Py_XDECREF(ents1);
        Py_XDECREF(ents2);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {adj.size};
        npy_intp strides[] = {sizeof(int)/sizeof(npy_bool)};
        return PyArray_NewFromOutStrided(1,dims,strides,NPY_BOOL,&adj);
    }
    else
    {
        int adj;

        iGeom_isEntAdj(self->handle,entities1[0],entities2[0],&adj,&err);
        if(checkError(self->handle,err))
            return NULL;

        return PyBool_FromLong(adj);
    }
err:
    Py_XDECREF(ents1);
    Py_XDECREF(ents2);
    return NULL;
}

static PyObject *
iGeomObj_getEntClosestPt(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","storage_order","out",0};
    int err;
    PyObject *in_ents,*ents;
    PyObject *in_verts,*verts;
    int storage_order = iBase_INTERLEAVED;

    iBase_OutArray on_coords = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|O&O&",kwlist,&in_ents,&in_verts,
                                    iBaseStorageOrder_Cvt,&storage_order,
                                    iBaseBuffer_Cvt,&on_coords))
        return NULL;

    iBase_EntityHandle *entities;
    int ent_size;

    if(!get_entity_data(in_ents,&ents,&entities,&ent_size))
        return NULL;

    verts = PyArray_FROMANY(in_verts,NPY_DOUBLE,1,2,NPY_C_CONTIGUOUS);
    if(verts == NULL)
        goto err;

    double *coords = PyArray_DATA(verts);
    int coord_size = PyArray_SIZE(verts);

    if(ents || PyArray_NDIM(verts) == 2)
    {
        if(PyArray_NDIM(verts) == 2 && !PyArray_CheckVectors(verts,2,3,
           storage_order==iBase_INTERLEAVED))
            goto err;
        if(PyArray_NDIM(verts) == 1 && !PyArray_CheckVectors(verts,1,3,0))
            goto err;

        iGeom_getArrClosestPt(self->handle,entities,ent_size,storage_order,
                              coords,coord_size,PASS_OUTARR(double,on_coords),
                              &err);
        Py_XDECREF(ents);
        Py_DECREF(verts);
        if(checkError(self->handle,err))
            return NULL;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = 3;
        dims[!vec_index] = on_coords.size/3;
        return PyArray_NewFromOut(2,dims,NPY_DOUBLE,&on_coords);
    }
    else
    {
        if(!PyArray_CheckVectors(verts,1,3,0))
            goto err;

        double *on_coords = malloc(sizeof(double)*3);

        iGeom_getEntClosestPt(self->handle,entities[0],
                              coords[0],coords[1],coords[2],
                              on_coords+0,on_coords+1,on_coords+2,&err);
        Py_DECREF(verts);
        if(checkError(self->handle,err))
        {
            free(on_coords);
            return NULL;
        }

        npy_intp dims[] = {3};
        return PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,on_coords);
    }

err:
    Py_XDECREF(ents);
    Py_XDECREF(verts);
    return NULL;
}

static PyObject *
iGeomObj_getEntNormal(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","basis","storage_order","out",
                             0};
    int err;
    PyObject *in_ents,*ents;
    PyObject *in_verts,*verts;
    enum iGeomExt_Basis basis = iGeomExt_XYZ;
    int storage_order = iBase_INTERLEAVED;

    iBase_OutArray normals = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|O&O&O&",kwlist,&in_ents,
                                    &in_verts,iGeomBasis_Cvt,&basis,
                                    iBaseStorageOrder_Cvt,&storage_order,
                                    iBaseBuffer_Cvt,&normals))
        return NULL;

    if(basis == iGeomExt_U)
    {
        PyErr_SetString(PyExc_ValueError,ERR_INVALID_BASIS);
        return NULL;
    }

    iBase_EntityHandle *entities;
    int ent_size;

    if(!get_entity_data(in_ents,&ents,&entities,&ent_size))
        return NULL;

    verts = PyArray_FROMANY(in_verts,NPY_DOUBLE,1,2,NPY_C_CONTIGUOUS);
    if(verts == NULL)
        goto err;

    double *coords = PyArray_DATA(verts);
    int coord_size = PyArray_SIZE(verts);

    if(ents || PyArray_NDIM(verts) == 2)
    {
        if(PyArray_NDIM(verts) == 2 && !PyArray_CheckVectors(verts,2,
           get_dimension(basis),storage_order==iBase_INTERLEAVED))
            goto err;
        if(PyArray_NDIM(verts) == 1 && !PyArray_CheckVectors(verts,1,
           get_dimension(basis),0))
            goto err;

        if(basis == iGeomExt_XYZ)
            iGeom_getArrNrmlXYZ(self->handle,entities,ent_size,storage_order,
                                coords,coord_size,PASS_OUTARR(double,normals),
                                &err);
        else
            iGeom_getArrNrmlUV(self->handle,entities,ent_size,storage_order,
                               coords,coord_size,PASS_OUTARR(double,normals),
                               &err);
        Py_XDECREF(ents);
        Py_DECREF(verts);

        if(checkError(self->handle,err))
            goto err;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = 3;
        dims[!vec_index] = normals.size/3;
        return PyArray_NewFromOut(2,dims,NPY_DOUBLE,&normals);
    }
    else
    {
        if(!PyArray_CheckVectors(verts,1,get_dimension(basis),0))
            goto err;

        double *normal = malloc(3*sizeof(double));

        if(basis == iGeomExt_XYZ)
            iGeom_getEntNrmlXYZ(self->handle,entities[0],
                                coords[0],coords[1],coords[2],
                                normal+0,normal+1,normal+2,&err);
        else
            iGeom_getEntNrmlUV(self->handle,entities[0],
                               coords[0],coords[1],
                               normal+0,normal+1,normal+2,&err);
        Py_DECREF(verts);

        if(checkError(self->handle,err))
        {
            free(normal);
            goto err;
        }

        npy_intp dims[] = {3};
        return PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,normal);
    }

err:
    Py_XDECREF(ents);
    Py_XDECREF(verts);
    return NULL;
}

static PyObject *
iGeomObj_getEntNormalPl(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","storage_order","out",0};
    int err;
    PyObject *in_ents,*ents;
    PyObject *in_verts,*verts;
    int storage_order = iBase_INTERLEAVED;
    PyObject *out = NULL;

    iBase_OutArray points = {0};
    iBase_OutArray normals = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|O&O!",kwlist,&in_ents,&in_verts,
                                    iBaseStorageOrder_Cvt,&storage_order,
                                    &PyTuple_Type,&out))
        return NULL;

    if(out && !PyArg_ParseTuple(out,"O&O&",iBaseBuffer_Cvt,&points,
                                           iBaseBuffer_Cvt,&normals))
        return NULL;

    iBase_EntityHandle *entities;
    int ent_size;

    if(!get_entity_data(in_ents,&ents,&entities,&ent_size))
        return NULL;

    verts = PyArray_FROMANY(in_verts,NPY_DOUBLE,1,2,NPY_C_CONTIGUOUS);
    if(verts == NULL)
        goto err;

    double *coords = PyArray_DATA(verts);
    int coord_size = PyArray_SIZE(verts);

    if(ents || PyArray_NDIM(verts) == 2)
    {
        if(PyArray_NDIM(verts) == 2 && !PyArray_CheckVectors(verts,2,3,
           storage_order==iBase_INTERLEAVED))
            goto err;
        if(PyArray_NDIM(verts) == 1 && !PyArray_CheckVectors(verts,1,3,0))
            goto err;

        iGeom_getArrNrmlPlXYZ(self->handle,entities,ent_size,storage_order,
                              coords,coord_size,PASS_OUTARR(double,points),
                              PASS_OUTARR(double,normals),&err);
        Py_XDECREF(ents);
        Py_DECREF(verts);

        if(checkError(self->handle,err))
            goto err;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = 3;
        dims[!vec_index] = normals.size/3;
        return NamedTuple_New(&NormalPl_Type,"(NN)",
            PyArray_NewFromOut(2,dims,NPY_DOUBLE,&points),
            PyArray_NewFromOut(2,dims,NPY_DOUBLE,&normals)
            );
    }
    else
    {
        if(!PyArray_CheckVectors(verts,1,3,0))
            goto err;

        double *point  = malloc(3*sizeof(double));
        double *normal = malloc(3*sizeof(double));

        iGeom_getEntNrmlPlXYZ(self->handle,entities[0],
                              coords[0],coords[1],coords[2],
                              point+0,point+1,point+2,
                              normal+0,normal+1,normal+2,&err);
        Py_DECREF(verts);

        if(checkError(self->handle,err))
        {
            free(point);
            free(normal);
            goto err;
        }

        npy_intp dims[] = {3};
        return NamedTuple_New(&NormalPl_Type,"(NN)",
            PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,point),
            PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,normal)
            );
    }

err:
    Py_XDECREF(ents);
    Py_XDECREF(verts);
    return NULL;
}

static PyObject *
iGeomObj_getEntTangent(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","basis","storage_order","out",
                             0};
    int err;
    PyObject *in_ents,*ents;
    PyObject *in_verts,*verts;
    enum iGeomExt_Basis basis = iGeomExt_XYZ;
    int storage_order = iBase_INTERLEAVED;

    iBase_OutArray tangents = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|O&O&O&",kwlist,&in_ents,
                                    &in_verts,iGeomBasis_Cvt,&basis,
                                    iBaseStorageOrder_Cvt,&storage_order,
                                    iBaseBuffer_Cvt,&tangents))
        return NULL;

    if(basis == iGeomExt_UV)
    {
        PyErr_SetString(PyExc_ValueError,ERR_INVALID_BASIS);
        return NULL;
    }

    iBase_EntityHandle *entities;
    int ent_size;

    if(!get_entity_data(in_ents,&ents,&entities,&ent_size))
        return NULL;

    verts = PyArray_FROMANY(in_verts,NPY_DOUBLE,1,2,NPY_C_CONTIGUOUS);
    if(verts == NULL)
        goto err;

    double *coords = PyArray_DATA(verts);
    int coord_size = PyArray_SIZE(verts);

    if(ents || PyArray_NDIM(verts) == 2)
    {
        if(PyArray_NDIM(verts) == 2 && !PyArray_CheckVectors(verts,2,
           get_dimension(basis),storage_order==iBase_INTERLEAVED))
            goto err;
        if(PyArray_NDIM(verts) == 1 && !PyArray_CheckVectors(verts,1,
           get_dimension(basis),0))
            goto err;

        if(basis == iGeomExt_XYZ)
            iGeom_getArrTgntXYZ(self->handle,entities,ent_size,storage_order,
                                coords,coord_size,PASS_OUTARR(double,tangents),
                                &err);
        else
            iGeom_getArrTgntU(self->handle,entities,ent_size,storage_order,
                              coords,coord_size,PASS_OUTARR(double,tangents),
                              &err);
        Py_XDECREF(ents);
        Py_DECREF(verts);

        if(checkError(self->handle,err))
            goto err;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = 3;
        dims[!vec_index] = tangents.size/3;
        return PyArray_NewFromOut(2,dims,NPY_DOUBLE,&tangents);
    }
    else
    {
        if(!PyArray_CheckVectors(verts,1,get_dimension(basis),0))
            goto err;

        double *tangent = malloc(3*sizeof(double));

        if(basis == iGeomExt_XYZ)
            iGeom_getEntTgntXYZ(self->handle,entities[0],
                                coords[0],coords[1],coords[2],
                                tangent+0,tangent+1,tangent+2,&err);
        else
            iGeom_getEntTgntU(self->handle,entities[0],coords[0],
                              tangent+0,tangent+1,tangent+2,&err);
        Py_DECREF(verts);

        if(checkError(self->handle,err))
        {
            free(tangent);
            goto err;
        }

        npy_intp dims[] = {3};
        return PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,tangent);
    }

err:
    Py_XDECREF(ents);
    Py_XDECREF(verts);
    return NULL;
}

static PyObject *
iGeomObj_getEntCurvature(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","basis","type",
                             "storage_order","out",0};
    int err;
    PyObject *in_ents,*ents;
    PyObject *in_verts,*verts;
    enum iGeomExt_Basis basis = iGeomExt_XYZ;
    int type = -1;
    int storage_order = iBase_INTERLEAVED;
    PyObject *out = NULL;

    iBase_OutArray curv1 = {0};
    iBase_OutArray curv2 = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|O&O&O&O!",kwlist,&in_ents,
                                    &in_verts,iGeomBasis_Cvt,&basis,
                                    iBaseType_Cvt,&type,iBaseStorageOrder_Cvt,
                                    &storage_order,&PyTuple_Type,&out))
        return NULL;

    if(out && !PyArg_ParseTuple(out,"O&O&",iBaseBuffer_Cvt,&curv1,
                                           iBaseBuffer_Cvt,&curv2))
        return NULL;

    if(basis == iGeomExt_U) /* Not currently supported */
    {
        PyErr_SetString(PyExc_ValueError,ERR_INVALID_BASIS);
        return NULL;
    }

    iBase_EntityHandle *entities;
    int ent_size;

    if(!get_entity_data(in_ents,&ents,&entities,&ent_size))
        return NULL;

    verts = PyArray_FROMANY(in_verts,NPY_DOUBLE,1,2,NPY_C_CONTIGUOUS);
    if(verts == NULL)
        goto err;

    double *coords = PyArray_DATA(verts);
    int coord_size = PyArray_SIZE(verts);

    if(type == -1) /* deduce entity type */
    {
        iGeom_getEntType(self->handle,entities[0],&type,&err);
        if(checkError(self->handle,err))
            goto err;
    }

    if(ents || PyArray_NDIM(verts) == 2)
    {
        if(PyArray_NDIM(verts) == 2 && !PyArray_CheckVectors(verts,2,
           get_dimension(basis),storage_order==iBase_INTERLEAVED))
            goto err;
        if(PyArray_NDIM(verts) == 1 && !PyArray_CheckVectors(verts,1,
           get_dimension(basis),0))
            goto err;

        if(basis == iGeomExt_XYZ)
            iGeom_getEntArrCvtrXYZ(self->handle,entities,ent_size,storage_order,
                                   coords,coord_size,PASS_OUTARR(double,curv1),
                                   PASS_OUTARR(double,curv2),&err);
        else if(type == iBase_FACE)
            iGeom_getFcArrCvtrUV(self->handle,entities,ent_size,storage_order,
                                 coords,coord_size,PASS_OUTARR(double,curv1),
                                 PASS_OUTARR(double,curv2),&err);
        else
        {
            PyErr_SetString(PyExc_ValueError,ERR_ENT_TYPE);
            goto err;
        }

        Py_XDECREF(ents);
        Py_DECREF(verts);

        if(checkError(self->handle,err))
            goto err;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = 3;
        dims[!vec_index] = curv1.size/3;
        if(curv2.size != 0)
            return Py_BuildValue("(NN)",
                PyArray_NewFromOut(2,dims,NPY_DOUBLE,&curv1),
                PyArray_NewFromOut(2,dims,NPY_DOUBLE,&curv2)
                );
        else
            return PyArray_NewFromOut(2,dims,NPY_DOUBLE,&curv1);
    }
    else
    {
        if(!PyArray_CheckVectors(verts,1,get_dimension(basis),0))
            goto err;

        if(type == iBase_FACE)
        {
            double *curv1 = malloc(3*sizeof(double));
            double *curv2 = malloc(3*sizeof(double));

            if(basis == iGeomExt_XYZ)
                iGeom_getFcCvtrXYZ(self->handle,entities[0],
                                   coords[0],coords[1],coords[2],
                                   curv1+0,curv1+1,curv1+2,
                                   curv2+0,curv2+1,curv2+2,&err);
            else
                iGeom_getFcCvtrUV(self->handle,entities[0],
                                  coords[0],coords[1],
                                  curv1+0,curv1+1,curv1+2,
                                  curv2+0,curv2+1,curv2+2,&err);
            Py_DECREF(verts);

            if(checkError(self->handle,err))
            {
                free(curv1);
                free(curv2);
                goto err;
            }

            npy_intp dims[] = {3};
            return Py_BuildValue("(NN)",
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,curv1),
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,curv2)
                );
        }
        else if(type == iBase_EDGE)
        {
            if(basis != iGeomExt_XYZ) /* not currently supported */
            {
                PyErr_SetString(PyExc_ValueError,ERR_INVALID_BASIS);
                goto err;
            }

            double *curv = malloc(3*sizeof(double));

            iGeom_getEgCvtrXYZ(self->handle,entities[0],
                               coords[0],coords[1],coords[2],
                               curv+0,curv+1,curv+2,&err);
            Py_DECREF(verts);

            if(checkError(self->handle,err))
            {
                free(curv);
                goto err;
            }

            npy_intp dims[] = {3};
            return PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,curv);
        }
        else
        {
            PyErr_SetString(PyExc_ValueError,ERR_ENT_TYPE);
            goto err;
        }
    }

err:
    Py_XDECREF(ents);
    Py_XDECREF(verts);
    return NULL;
}

static PyObject *
iGeomObj_getEntEval(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","type","storage_order","out",
                             0};
    int err;
    PyObject *in_ents,*ents;
    PyObject *in_verts,*verts;
    int type = -1;
    int storage_order = iBase_INTERLEAVED;
    PyObject *out = NULL;

    iBase_OutArray points = {0};
    iBase_OutArray tan_or_norm = {0};
    iBase_OutArray curv1 = {0};
    iBase_OutArray curv2 = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|O&O&O!",kwlist,&in_ents,
                                    &in_verts,iBaseType_Cvt,&type,
                                    iBaseStorageOrder_Cvt,&storage_order,
                                    &PyTuple_Type,&out))
        return NULL;

    if(out && !PyArg_ParseTuple(out,"O&O&O&O&",iBaseBuffer_Cvt,&points,
                                               iBaseBuffer_Cvt,&tan_or_norm,
                                               iBaseBuffer_Cvt,&curv1,
                                               iBaseBuffer_Cvt,&curv2))
        return NULL;

    iBase_EntityHandle *entities;
    int ent_size;

    if(!get_entity_data(in_ents,&ents,&entities,&ent_size))
        return NULL;

    verts = PyArray_FROMANY(in_verts,NPY_DOUBLE,1,2,NPY_C_CONTIGUOUS);
    if(verts == NULL)
        goto err;

    double *coords = PyArray_DATA(verts);
    int coord_size = PyArray_SIZE(verts);

    if(type == -1) /* deduce entity type */
    {
        iGeom_getEntType(self->handle,entities[0],&type,&err);
        if(checkError(self->handle,err))
            goto err;
    }

    if(ents || PyArray_NDIM(verts) == 2)
    {
        if(PyArray_NDIM(verts) == 2 && !PyArray_CheckVectors(verts,2,3,
           storage_order==iBase_INTERLEAVED))
            goto err;
        if(PyArray_NDIM(verts) == 1 && !PyArray_CheckVectors(verts,1,3,0))
            goto err;

        if(type == iBase_FACE)
        {
            iGeom_getArrFcEvalXYZ(self->handle,entities,ent_size,storage_order,
                                  coords,coord_size,PASS_OUTARR(double,points),
                                  PASS_OUTARR(double,tan_or_norm),
                                  PASS_OUTARR(double,curv1),
                                  PASS_OUTARR(double,curv2),&err);
            Py_XDECREF(ents);
            Py_DECREF(verts);

            if(checkError(self->handle,err))
                goto err;

            /* calculate the dimensions of the output array */
            npy_intp dims[2];
            int vec_index = storage_order != iBase_BLOCKED;
            dims[ vec_index] = 3;
            dims[!vec_index] = points.size/3;
            return NamedTuple_New(&FaceEval_Type,"(NNNN)",
                PyArray_NewFromOut(2,dims,NPY_DOUBLE,&points),
                PyArray_NewFromOut(2,dims,NPY_DOUBLE,&tan_or_norm),
                PyArray_NewFromOut(2,dims,NPY_DOUBLE,&curv1),
                PyArray_NewFromOut(2,dims,NPY_DOUBLE,&curv2)
                );
        }
        else if(type == iBase_EDGE)
        {
            iGeom_getArrEgEvalXYZ(self->handle,entities,ent_size,storage_order,
                                  coords,coord_size,PASS_OUTARR(double,points),
                                  PASS_OUTARR(double,tan_or_norm),
                                  PASS_OUTARR(double,curv1),&err);
            Py_XDECREF(ents);
            Py_DECREF(verts);

            if(checkError(self->handle,err))
                goto err;

            /* calculate the dimensions of the output array */
            npy_intp dims[2];
            int vec_index = storage_order != iBase_BLOCKED;
            dims[ vec_index] = 3;
            dims[!vec_index] = points.size/3;
            return NamedTuple_New(&EdgeEval_Type,"(NNN)",
                PyArray_NewFromOut(2,dims,NPY_DOUBLE,&points),
                PyArray_NewFromOut(2,dims,NPY_DOUBLE,&tan_or_norm),
                PyArray_NewFromOut(2,dims,NPY_DOUBLE,&curv1)
                );
        }
        else
        {
            PyErr_SetString(PyExc_ValueError,ERR_ENT_TYPE);
            goto err;
        }
    }
    else
    {
        if(!PyArray_CheckVectors(verts,1,3,0))
            goto err;

        if(type == iBase_FACE)
        {
            double *point  = malloc(3*sizeof(double));
            double *normal = malloc(3*sizeof(double));
            double *curv1  = malloc(3*sizeof(double));
            double *curv2  = malloc(3*sizeof(double));

            iGeom_getFcEvalXYZ(self->handle,entities[0],
                               coords[0],coords[1],coords[2],
                               point+0,  point+1,  point+2,
                               normal+0, normal+1, normal+2,
                               curv1+0,  curv1+1,  curv1+2,
                               curv2+0,  curv2+1,  curv2+2, &err);
            Py_DECREF(verts);

            if(checkError(self->handle,err))
            {
                free(point);
                free(normal);
                free(curv1);
                free(curv2);
                goto err;
            }

            npy_intp dims[] = {3};
            return NamedTuple_New(&FaceEval_Type,"(NNNN)",
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,point),
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,normal),
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,curv1),
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,curv2)
                );
        }
        else if(type == iBase_EDGE)
        {
            double *point   = malloc(3*sizeof(double));
            double *tangent = malloc(3*sizeof(double));
            double *curv    = malloc(3*sizeof(double));

            iGeom_getEgEvalXYZ(self->handle,entities[0],
                               coords[0],coords[1],coords[2],
                               point+0,  point+1,  point+2,
                               tangent+0,tangent+1,tangent+2,
                               curv+0,   curv+1,   curv+2, &err);
            Py_DECREF(verts);

            if(checkError(self->handle,err))
            {
                free(point);
                free(tangent);
                free(curv);
                goto err;
            }

            npy_intp dims[] = {3};
            return NamedTuple_New(&EdgeEval_Type,"(NNN)",
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,point),
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,tangent),
                PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,curv)
                );
        }
        else
        {
            PyErr_SetString(PyExc_ValueError,ERR_ENT_TYPE);
            goto err;
        }
    }

err:
    Py_XDECREF(ents);
    Py_XDECREF(verts);
    return NULL;
}

static PyObject *
iGeomObj_getEnt1stDerivative(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","storage_order","out",0};
    int err;
    PyObject *in_ents,*ents;
    PyObject *in_pts,*pts;
    int storage_order = iBase_INTERLEAVED;
    PyObject *out = NULL;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|O&O",kwlist,&in_ents,&in_pts,
                                    iBaseStorageOrder_Cvt,&storage_order,&out))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        pts = PyArray_ToVectors(in_pts,NPY_DOUBLE,2,2,
                                storage_order==iBase_INTERLEAVED);
        if(pts == NULL)
            goto err;

        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int ent_size = PyArray_SIZE(ents);
        double *uv = PyArray_DATA(pts);
        int uv_size = PyArray_SIZE(pts);

        iBase_OutArray u_deriv = {0};
        iBase_OutArray v_deriv = {0};
        iBase_OutArray offsets = {0};

        /* We don't use this */
        iBase_OutArray v_offsets = {0};

        if(out && !OffsetListBuffer_Cvt(out,&offsets,2,&u_deriv,&v_deriv))
        {
            PyErr_SetString(PyExc_ValueError,ERR_INVALID_OUT);
            return NULL;
        }

        iGeom_getArr1stDrvt(self->handle,entities,ent_size,storage_order,
                            uv,uv_size,PASS_OUTARR(double,u_deriv),
                            PASS_OUTARR(int,offsets),
                            PASS_OUTARR(double,v_deriv),
                            PASS_OUTARR(int,v_offsets),&err);
        Py_DECREF(ents);
        Py_DECREF(pts);

        if(checkError(self->handle,err))
            return NULL;
        free(v_offsets.data); /* Not needed */

        /* calculate the dimensions of the output array */
        npy_intp off_dims[] = {offsets.size};
        npy_intp uv_dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        uv_dims[ vec_index] = 3;
        uv_dims[!vec_index] = u_deriv.size/3;

        return OffsetList_New(
            PyArray_NewFromOut(1,off_dims,NPY_INT,&offsets),
            NamedTuple_New(&Deriv1st_Type,"(NN)",
                PyArray_NewFromOut(2,uv_dims,NPY_DOUBLE,&u_deriv),
                PyArray_NewFromOut(2,uv_dims,NPY_DOUBLE,&v_deriv)
                )
            );
    }
    else if(iBaseEntity_Check(in_ents))
    {
        pts = PyArray_ToVectors(in_pts,NPY_DOUBLE,1,2,0);
        if(pts == NULL)
            goto err;

        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        double *uv = PyArray_DATA(pts);

        iBase_OutArray u_deriv = {0};
        iBase_OutArray v_deriv = {0};

        if(out && !PyArg_ParseTuple(out,"O&O&",iBaseBuffer_Cvt,&u_deriv,
                                               iBaseBuffer_Cvt,&v_deriv))
        {
            PyErr_SetString(PyExc_ValueError,ERR_INVALID_OUT);
            return NULL;
        }

        iGeom_getEnt1stDrvt(self->handle,entity,uv[0],uv[1],
                            PASS_OUTARR(double,u_deriv),
                            PASS_OUTARR(double,v_deriv),&err);
        Py_DECREF(pts);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp uv_dims[] = {u_deriv.size};
        return NamedTuple_New(&Deriv1st_Type,"(NN)",
            PyArray_NewFromOut(1,uv_dims,NPY_DOUBLE,&u_deriv),
            PyArray_NewFromOut(1,uv_dims,NPY_DOUBLE,&v_deriv)
            );
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }

err:
    Py_XDECREF(ents);
    Py_XDECREF(pts);
    return NULL;
}

static PyObject *
iGeomObj_getEnt2ndDerivative(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","storage_order","out",0};
    int err;
    PyObject *in_ents,*ents;
    PyObject *in_pts,*pts;
    int storage_order = iBase_INTERLEAVED;
    PyObject *out = NULL;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|O&O",kwlist,&in_ents,&in_pts,
                                    iBaseStorageOrder_Cvt,&storage_order,&out))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        pts = PyArray_ToVectors(in_pts,NPY_DOUBLE,2,2,
                                storage_order==iBase_INTERLEAVED);
        if(pts == NULL)
            goto err;

        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int ent_size = PyArray_SIZE(ents);
        double *uv = PyArray_DATA(pts);
        int uv_size = PyArray_SIZE(pts);

        iBase_OutArray uu_deriv = {0};
        iBase_OutArray vv_deriv = {0};
        iBase_OutArray uv_deriv = {0};
        iBase_OutArray offsets = {0};

        /* We don't use these */
        iBase_OutArray vv_offsets = {0};
        iBase_OutArray uv_offsets = {0};

        if(out && !OffsetListBuffer_Cvt(out,&offsets,3,&uu_deriv,&vv_deriv,
                                        &uv_deriv))
        {
            PyErr_SetString(PyExc_ValueError,ERR_INVALID_OUT);
            return NULL;
        }

        iGeom_getArr2ndDrvt(self->handle,entities,ent_size,storage_order,
                            uv,uv_size,PASS_OUTARR(double,uu_deriv),
                            PASS_OUTARR(int,offsets),
                            PASS_OUTARR(double,vv_deriv),
                            PASS_OUTARR(int,vv_offsets),
                            PASS_OUTARR(double,uv_deriv),
                            PASS_OUTARR(int,uv_offsets),&err);
        Py_DECREF(ents);
        Py_DECREF(pts);

        if(checkError(self->handle,err))
            return NULL;
        free(vv_offsets.data); free(uv_offsets.data); /* Not needed */

        /* calculate the dimensions of the output array */
        npy_intp off_dims[] = {offsets.size};
        npy_intp uv_dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        uv_dims[ vec_index] = 3;
        uv_dims[!vec_index] = uu_deriv.size/3;

        return OffsetList_New(
            PyArray_NewFromOut(1,off_dims,NPY_INT,&offsets),
            NamedTuple_New(&Deriv2nd_Type,"(NNN)",
                PyArray_NewFromOut(2,uv_dims,NPY_DOUBLE,&uu_deriv),
                PyArray_NewFromOut(2,uv_dims,NPY_DOUBLE,&vv_deriv),
                PyArray_NewFromOut(2,uv_dims,NPY_DOUBLE,&uv_deriv)
                )
            );
    }
    else if(iBaseEntity_Check(in_ents))
    {
        pts = PyArray_ToVectors(in_pts,NPY_DOUBLE,1,2,0);
        if(pts == NULL)
            goto err;

        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        double *uv = PyArray_DATA(pts);

        iBase_OutArray uu_deriv = {0};
        iBase_OutArray vv_deriv = {0};
        iBase_OutArray uv_deriv = {0};

        if(out && !PyArg_ParseTuple(out,"O&O&O&",iBaseBuffer_Cvt,&uu_deriv,
                                                 iBaseBuffer_Cvt,&vv_deriv,
                                                 iBaseBuffer_Cvt,&uv_deriv))
        {
            PyErr_SetString(PyExc_ValueError,ERR_INVALID_OUT);
            return NULL;
        }

        iGeom_getEnt2ndDrvt(self->handle,entity,uv[0],uv[1],
                            PASS_OUTARR(double,uu_deriv),
                            PASS_OUTARR(double,vv_deriv),
                            PASS_OUTARR(double,uv_deriv),&err);
        Py_DECREF(pts);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp uv_dims[] = {uu_deriv.size};
        return NamedTuple_New(&Deriv2nd_Type,"(NNN)",
            PyArray_NewFromOut(1,uv_dims,NPY_DOUBLE,&uu_deriv),
            PyArray_NewFromOut(1,uv_dims,NPY_DOUBLE,&vv_deriv),
            PyArray_NewFromOut(1,uv_dims,NPY_DOUBLE,&uv_deriv)
            );
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }

err:
    Py_XDECREF(ents);
    Py_XDECREF(pts);
    return NULL;
}

static PyObject *
iGeomObj_getPtRayIntersect(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"points","vectors","storage_order","out",0};
    int err;
    PyObject *in_pts,*pts;
    PyObject *in_vecs,*vecs;
    int storage_order = iBase_INTERLEAVED;
    PyObject *out = NULL;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|O&O",kwlist,&in_pts,&in_vecs,
                                    iBaseStorageOrder_Cvt,&storage_order,&out))
        return NULL;

    pts = PyArray_ToVectors(in_pts,NPY_DOUBLE,2,3,
                            storage_order==iBase_INTERLEAVED);
    if(pts)
    {
        vecs = PyArray_ToVectors(in_vecs,NPY_DOUBLE,2,3,
                                 storage_order==iBase_INTERLEAVED);
        if(vecs == NULL)
            goto err;

        double *coords  = PyArray_DATA(pts);
        int coords_size = PyArray_SIZE(pts);
        double *dirs    = PyArray_DATA(vecs);
        int dirs_size   = PyArray_SIZE(vecs);

        iBase_OutArray entities = {0};
        iBase_OutArray offsets = {0};
        iBase_OutArray isect = {0};
        iBase_OutArray param = {0};

        if(out && !OffsetListBuffer_Cvt(out,&offsets,3,&entities,&isect,&param))
        {
            PyErr_SetString(PyExc_ValueError,ERR_INVALID_OUT);
            return NULL;
        }

        iGeom_getPntArrRayIntsct(self->handle,storage_order,
                                 coords,coords_size,dirs,dirs_size,
                                 PASS_OUTARR_ENT(entities),
                                 PASS_OUTARR(int,offsets),
                                 PASS_OUTARR(double,isect),
                                 PASS_OUTARR(double,param),&err);
        Py_DECREF(pts);
        Py_DECREF(vecs);

        if(checkError(self->handle,err))
            return NULL;

        /* calculate the dimensions of the output arrays */
        npy_intp off_dims[] = {offsets.size};
        npy_intp ent_dims[] = {entities.size};
        npy_intp coord_dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        coord_dims[ vec_index] = 3;
        coord_dims[!vec_index] = isect.size/3;
        npy_intp param_dims[] = {param.size};

        return OffsetList_New(
            PyArray_NewFromOut(1,off_dims,NPY_INT,&offsets),
            NamedTuple_New(&Intersect_Type,"(NNN)",
                PyArray_NewFromOut(1,ent_dims,NPY_IBASEENT,&entities),
                PyArray_NewFromOut(2,coord_dims,NPY_DOUBLE,&isect),
                PyArray_NewFromOut(1,param_dims,NPY_DOUBLE,&param)
                )
            );
    }

    pts = PyArray_ToVectors(in_pts,NPY_DOUBLE,1,3,0);
    if(pts)
    {
        vecs = PyArray_ToVectors(in_vecs,NPY_DOUBLE,1,3,0);
        if(vecs == NULL)
            goto err;

        double *coords = PyArray_DATA(pts);
        double *dirs   = PyArray_DATA(vecs);

        iBase_OutArray entities = {0};
        iBase_OutArray isect = {0};
        iBase_OutArray param = {0};

        if(out && !PyArg_ParseTuple(out,"O&O&O&",iBaseBuffer_Cvt,&entities,
                                                 iBaseBuffer_Cvt,&isect,
                                                 iBaseBuffer_Cvt,&param))
        {
            PyErr_SetString(PyExc_ValueError,ERR_INVALID_OUT);
            return NULL;
        }

        iGeom_getPntRayIntsct(self->handle,coords[0],coords[1],coords[2],
                              dirs[0],dirs[1],dirs[2],PASS_OUTARR_ENT(entities),
                              storage_order,PASS_OUTARR(double,isect),
                              PASS_OUTARR(double,param),&err);
        Py_DECREF(pts);
        Py_DECREF(vecs);
        if(checkError(self->handle,err))
            return NULL;

        /* calculate the dimensions of the output array */
        npy_intp ent_dims[] = {entities.size};
        npy_intp coord_dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        coord_dims[ vec_index] = 3;
        coord_dims[!vec_index] = isect.size/3;
        npy_intp param_dims[] = {param.size};

        return NamedTuple_New(&Intersect_Type,"(NNN)",
            PyArray_NewFromOut(1,ent_dims,NPY_IBASEENT,&entities),
            PyArray_NewFromOut(2,coord_dims,NPY_DOUBLE,&isect),
            PyArray_NewFromOut(2,param_dims,NPY_DOUBLE,&param)
            );
    }

    PyErr_SetString(PyExc_ValueError,ERR_ARR_DIMS);
    return NULL;
err:
    Py_XDECREF(pts);
    Py_XDECREF(vecs);
    return NULL;
}

static PyObject *
iGeomObj_getPtClass(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"points","storage_order","out",0};
    int err;
    PyObject *in_pts,*pts;
    int storage_order = iBase_INTERLEAVED;

    iBase_OutArray entities = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&O&",kwlist,&in_pts,
                                    iBaseStorageOrder_Cvt,&storage_order,
                                    iBaseBuffer_Cvt,&entities))
        return NULL;

    pts = PyArray_ToVectors(in_pts,NPY_DOUBLE,2,3,1);
    if(pts)
    {
        double *coords  = PyArray_DATA(pts);
        int coords_size = PyArray_SIZE(pts);

        iGeom_getPntArrClsf(self->handle,storage_order,coords,coords_size,
                            PASS_OUTARR_ENT(entities),&err);
        Py_DECREF(pts);

        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {entities.size};
        return PyArray_NewFromOut(1,dims,NPY_IBASEENT,&entities);
    }

    pts = PyArray_ToVectors(in_pts,NPY_DOUBLE,1,3,0);
    if(pts)
    {
        double *coords = PyArray_DATA(pts);

        iBase_EntityHandle handle;
        iGeom_getPntClsf(self->handle,coords[0],coords[1],coords[2],&handle,
                         &err);
        Py_DECREF(pts);
        if(checkError(self->handle,err))
            return NULL;
        return iBaseEntity_FromHandle(handle);
    }

    PyErr_SetString(PyExc_ValueError,ERR_ARR_DIMS);
    return NULL;
}

static PyObject *
iGeomObj_getEntNormalSense(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"faces","regions","out",0};
    int err;
    PyObject *in_ents1,*ents1 = NULL;
    PyObject *in_ents2,*ents2 = NULL;

    iBase_OutArray senses = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|O&",kwlist,&in_ents1,&in_ents2,
                                    iBaseBuffer_Cvt,&senses))
        return NULL;

    iBase_EntityHandle *faces;
    int face_size;
    iBase_EntityHandle *regions;
    int region_size;

    if(!get_entity_data(in_ents1,&ents1,&faces,&face_size))
        goto err;
    if(!get_entity_data(in_ents2,&ents2,&regions,&region_size))
        goto err;

    if(ents1 || ents2)
    {
        iGeom_getArrNrmlSense(self->handle,faces,face_size,regions,region_size,
                              PASS_OUTARR(int,senses),&err);
        Py_XDECREF(ents1);
        Py_XDECREF(ents2);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {senses.size};
        return PyArray_NewFromOut(1,dims,NPY_INT,&senses);
    }
    else
    {
        int sense;
        iGeom_getEntNrmlSense(self->handle,faces[0],regions[0],&sense,&err);
        if(checkError(self->handle,err))
            return NULL;
        return PyInt_FromLong(sense);
    }
err:
    Py_XDECREF(ents1);
    Py_XDECREF(ents2);
    return NULL;
}

static PyObject *
iGeomObj_getEgFcSense(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"edges","faces","out",0};
    int err;
    PyObject *in_ents1,*ents1 = NULL;
    PyObject *in_ents2,*ents2 = NULL;

    iBase_OutArray senses = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|O&",kwlist,&in_ents1,&in_ents2,
                                    iBaseBuffer_Cvt,&senses))
        return NULL;

    iBase_EntityHandle *edges;
    int edge_size;
    iBase_EntityHandle *faces;
    int face_size;

    if(!get_entity_data(in_ents1,&ents1,&edges,&edge_size))
        goto err;
    if(!get_entity_data(in_ents2,&ents2,&faces,&face_size))
        goto err;

    if(ents1 || ents2)
    {
        iGeom_getEgFcArrSense(self->handle,edges,edge_size,faces,face_size,
                              PASS_OUTARR(int,senses),&err);
        Py_XDECREF(ents1);
        Py_XDECREF(ents2);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {senses.size};
        return PyArray_NewFromOut(1,dims,NPY_INT,&senses);
    }
    else
    {
        int sense;
        iGeom_getEgFcSense(self->handle,edges[0],faces[0],&sense,&err);
        if(checkError(self->handle,err))
            return NULL;
        return PyInt_FromLong(sense);
    }
err:
    Py_XDECREF(ents1);
    Py_XDECREF(ents2);
    return NULL;
}

static PyObject *
iGeomObj_getEgVtxSense(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"edges","vertices1","vertices2","out",0};
    int err;
    PyObject *in_ents1,*ents1 = NULL;
    PyObject *in_ents2,*ents2 = NULL;
    PyObject *in_ents3,*ents3 = NULL;

    iBase_OutArray senses = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OOO|O&",kwlist,&in_ents1,&in_ents2,
                                    &in_ents3,iBaseBuffer_Cvt,&senses))
        return NULL;

    iBase_EntityHandle *edges;
    int edge_size;
    iBase_EntityHandle *verts1;
    int vert1_size;
    iBase_EntityHandle *verts2;
    int vert2_size;

    if(!get_entity_data(in_ents1,&ents1,&edges,&edge_size))
        goto err;
    if(!get_entity_data(in_ents2,&ents2,&verts1,&vert1_size))
        goto err;
    if(!get_entity_data(in_ents3,&ents3,&verts2,&vert2_size))
        goto err;

    if(ents1 || ents2 || ents3)
    {
        iGeom_getEgVtxArrSense(self->handle,edges,edge_size,verts1,vert1_size,
                               verts2,vert2_size,PASS_OUTARR(int,senses),&err);
        Py_XDECREF(ents1);
        Py_XDECREF(ents2);
        Py_XDECREF(ents3);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {senses.size};
        return PyArray_NewFromOut(1,dims,NPY_INT,&senses);
    }
    else
    {
        int sense;
        iGeom_getEgVtxSense(self->handle,edges[0],verts1[0],verts2[0],&sense,
                            &err);
        if(checkError(self->handle,err))
            return NULL;
        return PyInt_FromLong(sense);
    }
err:
    Py_XDECREF(ents1);
    Py_XDECREF(ents2);
    Py_XDECREF(ents3);
    return NULL;
}

static PyObject *
iGeomObj_copyEnt(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity",0};
    int err;
    iBaseEntity_Object *entity;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntity_Type,
                                    &entity))
        return NULL;

    iBaseEntity_Object *copy = iBaseEntity_New();
    iGeom_copyEnt(self->handle,entity->handle,&copy->handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF(copy);
        return NULL;
    }
    return (PyObject*)copy;
}

static PyObject *
iGeomObj_moveEnt(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity","direction",0};
    int err;
    iBaseEntity_Object *entity;
    PyObject *in_vec,*vec;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!O",kwlist,&iBaseEntity_Type,
                                    &entity,&in_vec))
        return NULL;

    vec = PyArray_ToVectors(in_vec,NPY_DOUBLE,1,3,0);
    if(vec == NULL)
        return NULL;

    double *coords = PyArray_DATA(vec);
    iGeom_moveEnt(self->handle,entity->handle,coords[0],coords[1],coords[2],
                  &err);
    Py_DECREF(vec);

    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_rotateEnt(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity","angle","axis",0};
    int err;
    iBaseEntity_Object *entity;
    double angle;
    PyObject *in_vec,*vec;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!dO",kwlist,&iBaseEntity_Type,
                                    &entity,&angle,&in_vec))
        return NULL;

    vec = PyArray_ToVectors(in_vec,NPY_DOUBLE,1,3,0);
    if(vec == NULL)
        return NULL;

    double *coords = PyArray_DATA(vec);
    iGeom_rotateEnt(self->handle,entity->handle,angle,coords[0],coords[1],
                    coords[2],&err);
    Py_DECREF(vec);

    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_reflectEnt(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity","axis",0};
    int err;
    iBaseEntity_Object *entity;
    PyObject *in_vec,*vec;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!O",kwlist,&iBaseEntity_Type,
                                    &entity,&in_vec))
        return NULL;

    vec = PyArray_ToVectors(in_vec,NPY_DOUBLE,1,3,0);
    if(vec == NULL)
        return NULL;

    double *coords = PyArray_DATA(vec);
    iGeom_reflectEnt(self->handle,entity->handle,coords[0],coords[1],coords[2],
                     &err);
    Py_DECREF(vec);

    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_scaleEnt(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity","scale",0};
    int err;
    iBaseEntity_Object *entity;
    PyObject *in_vec,*vec;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!O",kwlist,&iBaseEntity_Type,
                                    &entity,&in_vec))
        return NULL;

    vec = PyArray_ToVectors(in_vec,NPY_DOUBLE,1,3,0);
    if(vec == NULL)
        return NULL;

    double *coords = PyArray_DATA(vec);
    iGeom_scaleEnt(self->handle,entity->handle,coords[0],coords[1],coords[2],
                   &err);
    Py_DECREF(vec);

    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_sweepEntAboutAxis(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity","angle","axis",0};
    int err;
    iBaseEntity_Object *entity;
    double angle;
    PyObject *in_axis,*axis;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!dO",kwlist,&iBaseEntity_Type,
                                    &entity,&angle,&in_axis))
        return NULL;

    axis = PyArray_ToVectors(in_axis,NPY_DOUBLE,1,3,0);
    if(axis == NULL)
        return NULL;

    double *v = PyArray_DATA(axis);
    iBaseEntity_Object *result = iBaseEntity_New();
    iGeom_sweepEntAboutAxis(self->handle,entity->handle,angle,v[0],v[1],v[2],
                            &result->handle,&err);
    if(checkError(self->handle,err))
    {
        Py_DECREF(result);
        return NULL;
    }
    return (PyObject*)result;
}

static PyObject *
iGeomObj_uniteEnts(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    int err;
    PyObject *in_ents,*ents;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&in_ents))
        in_ents = args;

    ents = PyArray_FROMANY(in_ents,NPY_IBASEENT,1,1,NPY_C_CONTIGUOUS);
    if(ents == NULL)
        return NULL;

    iBase_EntityHandle *entities = PyArray_DATA(ents);
    int size = PyArray_SIZE(ents);

    iBaseEntity_Object *result = iBaseEntity_New();

    iGeom_uniteEnts(self->handle,entities,size,&result->handle,&err);
    Py_DECREF(ents);

    if(checkError(self->handle,err))
        return NULL;

    return (PyObject*)result;
}

static PyObject *
iGeomObj_subtractEnts(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity1","entity2",0};
    int err;
    iBaseEntity_Object *entity1;
    iBaseEntity_Object *entity2;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!O!",kwlist,&iBaseEntity_Type,
                                    &entity1,&iBaseEntity_Type,&entity2))
        return NULL;

    iBaseEntity_Object *result = iBaseEntity_New();
    iGeom_subtractEnts(self->handle,entity1->handle,entity2->handle,
                       &result->handle,&err);

    if(checkError(self->handle,err))
    {
        Py_DECREF(result);
        return NULL;
    }
    return (PyObject*)result;
}

static PyObject *
iGeomObj_intersectEnts(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity1","entity2",0};
    int err;
    iBaseEntity_Object *entity1;
    iBaseEntity_Object *entity2;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!O!",kwlist,&iBaseEntity_Type,
                                    &entity1,&iBaseEntity_Type,&entity2))
        return NULL;

    iBaseEntity_Object *result = iBaseEntity_New();
    iGeom_intersectEnts(self->handle,entity1->handle,entity2->handle,
                       &result->handle,&err);

    if(checkError(self->handle,err))
    {
        Py_DECREF(result);
        return NULL;
    }
    return (PyObject*)result;
}

static PyObject *
iGeomObj_sectionEnt(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entity","normal","offset","reverse",0};
    int err;
    iBaseEntity_Object *entity;
    PyObject *in_norm,*norm;
    double offset;
    PyObject* rev;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!OdO!",kwlist,&iBaseEntity_Type,
                                    &entity,&in_norm,&offset,&PyBool_Type,&rev))
        return NULL;


    norm = PyArray_ToVectors(in_norm,NPY_DOUBLE,1,3,0);
    if(norm == NULL)
        return NULL;

    double *coords = PyArray_DATA(norm);

    iBaseEntity_Object *result = iBaseEntity_New();

    iGeom_sectionEnt(self->handle,entity->handle,coords[0],coords[1],coords[2],
                     offset,(rev == Py_True),&result->handle,&err);
    Py_DECREF(norm);

    if(checkError(self->handle,err))
    {
        Py_DECREF(result);
        return NULL;
    }
    return (PyObject*)result;
}

static PyObject *
iGeomObj_imprintEnts(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    int err;
    PyObject *in_ents,*ents;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O",kwlist,&in_ents))
        in_ents = args;

    ents = PyArray_FROMANY(in_ents,NPY_IBASEENT,1,1,NPY_C_CONTIGUOUS);
    if(ents == NULL)
        return NULL;

    iBase_EntityHandle *entities = PyArray_DATA(ents);
    int size = PyArray_SIZE(ents);

    iGeom_imprintEnts(self->handle,entities,size,&err);
    Py_DECREF(ents);

    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_mergeEnts(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","tolerance",0};
    int err;
    PyObject *in_ents,*ents;
    double tolerance;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"Od",kwlist,&in_ents,&tolerance))
        return NULL;

    ents = PyArray_FROMANY(in_ents,NPY_IBASEENT,1,1,NPY_C_CONTIGUOUS);
    if(ents == NULL)
        return NULL;

    iBase_EntityHandle *entities = PyArray_DATA(ents);
    int size = PyArray_SIZE(ents);

    iGeom_mergeEnts(self->handle,entities,size,tolerance,&err);
    Py_DECREF(ents);

    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_createEntSet(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"ordered",0};
    int err;
    PyObject *ordered;

    iBase_EntitySetHandle handle;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&PyBool_Type,&ordered))
        return NULL;

    iGeom_createEntSet(self->handle,(ordered==Py_True),&handle,&err);
    if(checkError(self->handle,err))
        return NULL;

    return iGeomEntitySet_FromHandle(self,handle);
}

static PyObject *
iGeomObj_destroyEntSet(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    int err;
    iBaseEntitySet_Object *set;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntitySet_Type,
                                    &set))
        return NULL;

    iGeom_destroyEntSet(self->handle,set->handle,&err);
    if(checkError(self->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_createTag(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"name","size","type",0};
    int err;
    const char *name;
    int size;
    enum iBase_TagValueType type;

    iBase_TagHandle handle;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"siO&",kwlist,&name,&size,
                                    iBaseTagType_Cvt,&type))
        return NULL;

    iGeom_createTag(self->handle,name,size,type,&handle,&err,strlen(name));
    if(checkError(self->handle,err))
        return NULL;

    return iGeomTag_FromHandle(self,handle);
}

static PyObject *
iGeomObj_destroyTag(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"tag","force",0};
    int err;
    iBaseTag_Object *tag;
    PyObject *forced;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!O!",kwlist,&iBaseTag_Type,&tag,
                                    &PyBool_Type,&forced))
        return NULL;

    iGeom_destroyTag(self->handle,tag->handle,(forced==Py_True),&err);
    if(checkError(self->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iGeomObj_getTagHandle(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"name",0};
    int err;
    const char *name;

    iBase_TagHandle handle;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"s",kwlist,&name))
        return NULL;

    iGeom_getTagHandle(self->handle,name,&handle,&err,strlen(name));
    if(checkError(self->handle,err))
        return NULL;

    return iGeomTag_FromHandle(self,handle);
}

static PyObject *
iGeomObj_getAllTags(iGeom_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","out",0};
    int err;
    PyObject *ents;

    iBase_OutArray tags = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&",kwlist,&ents,
                                    iBaseBuffer_Cvt,&tags))
        return NULL;

    if(iBaseEntitySet_Check(ents))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GET_HANDLE(ents);

        iGeom_getAllEntSetTags(self->handle,set,PASS_OUTARR_TAG(tags),&err);
        if(checkError(self->handle,err))
            return NULL;
    }
    else if(iBaseEntity_Check(ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(ents);

        iGeom_getAllTags(self->handle,entity,PASS_OUTARR_TAG(tags),&err);
        if(checkError(self->handle,err))
            return NULL;
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTSET);
        return NULL;
    }

    npy_intp dims[] = {tags.size};
    return PyArray_NewFromOutBase(1,dims,NPY_IBASETAG,&tags,
                                  (iBase_Object*)self);
}

static PyObject *
iGeomObj_repr(iGeom_Object *self)
{
    return PyString_FromFormat("<%s %p>",self->ob_type->tp_name,self->handle);
}

static PyObject *
iGeomObj_richcompare(iGeom_Object *lhs,iGeom_Object *rhs,int op)
{
    if(!iGeom_Check(lhs) || !iGeom_Check(rhs))
    {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    switch(op)
    {
    case Py_EQ:
        return PyBool_FromLong(lhs->handle == rhs->handle);
    case Py_NE:
        return PyBool_FromLong(lhs->handle != rhs->handle);
    default:
        PyErr_SetNone(PyExc_TypeError);
        return NULL;
    }
}

static long
iGeomObj_hash(iGeom_Object *self)
{
    return (long)self->handle;
}

static PyMethodDef iGeomObj_methods[] = {
    IGEOM_METHOD(iGeom, load,                METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, save,                METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, createSphere,        METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, createBrick,         METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, createCylinder,      METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, createPrism,         METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, createCone,          METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, createTorus,         METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, deleteAll,           METH_NOARGS),
    IGEOM_METHOD(iGeom, deleteEnt,           METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getVtxCoords,        METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEntCoords,        METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, measure,             METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEntType,          METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getFaceType,         METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, isEntParametric,     METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, isEntPeriodic,       METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, isFcDegenerate,      METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEntBoundBox,      METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEntRange,         METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEntTolerance,     METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEntAdj,           METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEnt2ndAdj,        METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, isEntAdj,            METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEntClosestPt,     METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEntNormal,        METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEntNormalPl,      METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEntTangent,       METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEntCurvature,     METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEntEval,          METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEnt1stDerivative, METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEnt2ndDerivative, METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getPtRayIntersect,   METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getPtClass,          METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEntNormalSense,   METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEgFcSense,        METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getEgVtxSense,       METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, copyEnt,             METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, moveEnt,             METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, rotateEnt,           METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, reflectEnt,          METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, scaleEnt,            METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, sweepEntAboutAxis,   METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, uniteEnts,           METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, subtractEnts,        METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, intersectEnts,       METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, sectionEnt,          METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, imprintEnts,         METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, mergeEnts,           METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, createEntSet,        METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, destroyEntSet,       METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, createTag,           METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, destroyTag,          METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getTagHandle,        METH_VARARGS|METH_KEYWORDS),
    IGEOM_METHOD(iGeom, getAllTags,          METH_VARARGS|METH_KEYWORDS),
    {0}
};

static PyGetSetDef iGeomObj_getset[] = {
    IGEOM_GET(iGeom, rootSet),
    IGEOM_GET(iGeom, boundBox),
    IGEOM_GET(iGeom, topoLevel),
    IGEOM_GET(iGeom, parametric),
    IGEOM_GET(iGeom, tolerance),
    {0}
};

static PyObject * iGeomObj_getAttr(PyObject *self,PyObject *attr_name)
{
    PyObject *ret;

    ret = PyObject_GenericGetAttr(self,attr_name);
    if(ret)
        return ret;
    else if(!PyErr_ExceptionMatches(PyExc_AttributeError))
        return NULL;
    else
    {
        PyErr_Clear();
        PyObject *root = iGeomObj_getrootSet((iGeom_Object*)self,0);
        if(!root)
            return NULL;
        ret = PyObject_GetAttr(root,attr_name);
        Py_DECREF(root);
        return ret;
    }
}

static PyTypeObject iGeom_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iGeom.Geom",                       /* tp_name */
    sizeof(iGeom_Object),                     /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)iGeomObj_dealloc,             /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    (reprfunc)iGeomObj_repr,                  /* tp_repr */
    0,                                        /* tp_as_number */
    0,                                        /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    (hashfunc)iGeomObj_hash,                  /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str */
    iGeomObj_getAttr,                         /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    IGEOMDOC_iGeom,                           /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    (richcmpfunc)iGeomObj_richcompare,        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    iGeomObj_methods,                         /* tp_methods */
    0,                                        /* tp_members */
    iGeomObj_getset,                          /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)iGeomObj_init,                  /* tp_init */
    0,                                        /* tp_alloc */
    0,                                        /* tp_new */
};


static PyMethodDef module_methods[] = {
    {0}
};

ENUM_TYPE(iGeomBasis,"iGeom.Basis","");

PyMODINIT_FUNC initiGeom(void)
{
    PyObject *m;
    m = Py_InitModule("iGeom",module_methods);
    import_array();
    import_ufunc();
    import_iBase();
    import_helpers();

    /***** register C API *****/
    static void *IGeom_API[] = {
        &iGeom_Type,
        &iGeomIter_Type,
        &iGeomEntitySet_Type,
        &iGeomTag_Type,
        &iGeom_FromInstance,
        &iGeomEntitySet_FromHandle,
        &iGeomEntitySet_GetInstance,
        &iGeomTag_GetInstance,
        &iGeomTag_FromHandle,
        &NormalPl_Type_,
        &FaceEval_Type_,
        &EdgeEval_Type_,
        &Deriv1st_Type_,
        &Deriv2nd_Type_,
        &Intersect_Type_,
        &Tolerance_Type_,
        &iGeomBasis_Cvt,
    };
    PyObject *api_obj;

    /* Create a CObject containing the API pointer array's address */
    api_obj = PyCObject_FromVoidPtr(IGeom_API,NULL);

    if(api_obj != NULL)
        PyModule_AddObject(m, "_C_API", api_obj);

    REGISTER_CLASS_BASE(m,"Geom",     iGeom,         iBase);
    REGISTER_CLASS_BASE(m,"EntitySet",iGeomEntitySet,iBaseEntitySet);
    REGISTER_CLASS_BASE(m,"Tag",      iGeomTag,      iBaseTag);
    REGISTER_CLASS     (m,"Iterator", iGeomIter);

    /***** initialize topology enum *****/
    REGISTER_CLASS(m,"Basis",iGeomBasis);

    ADD_ENUM(iGeomBasis,"xyz", iGeomExt_XYZ);
    ADD_ENUM(iGeomBasis,"u",   iGeomExt_U);
    ADD_ENUM(iGeomBasis,"uv",  iGeomExt_UV);

    /***** initialize iGeom NumPy array *****/
    iBase_RegisterSubArray(NPY_IBASEENTSET,&iGeom_Type,&iGeomEntitySet_Type,
                           (arrgetfunc)iGeomEntitySet_GetInstance,
                           (arrcreatefunc)iGeomEntitySet_FromHandle);
    iBase_RegisterSubArray(NPY_IBASETAG,&iGeom_Type,&iGeomTag_Type,
                           (arrgetfunc)iGeomTag_GetInstance,
                           (arrcreatefunc)iGeomTag_FromHandle);

    /***** create named tuple types *****/
    NormalPl_Type_  = NamedTuple_CreateType(m,"normal_pl","points normals");
    FaceEval_Type_  = NamedTuple_CreateType(m,"face_eval","points normals "
                                           "curv1 curv2");
    EdgeEval_Type_  = NamedTuple_CreateType(m,"edge_eval","points tangents "
                                           "curv");
    Deriv1st_Type_  = NamedTuple_CreateType(m,"deriv_1st","u v");
    Deriv2nd_Type_  = NamedTuple_CreateType(m,"deriv_2nd","uu vv uv");
    Intersect_Type_ = NamedTuple_CreateType(m,"intersect","entities isect "
                                           "param");
    Tolerance_Type_ = NamedTuple_CreateType(m,"tolerance","type tolerance");
    MinMax_Type_    = NamedTuple_CreateType(m,"min_max","min max");
}

/* Include source files so that everything is in one translation unit */
#include "iGeom_entSet.inl"
#include "iGeom_iter.inl"
#include "iGeom_tag.inl"
