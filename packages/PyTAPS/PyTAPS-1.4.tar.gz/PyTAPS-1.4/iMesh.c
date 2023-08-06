#define _IMESH_MODULE
#include "iMesh_Python.h"
#include "iMesh_doc.h"
#include "errors.h"
#include "common.h"
#include "helpers.h"
#include "numpy_extensions.h"

#include <numpy/ufuncobject.h>

static PyTypeObject *CreateEnt_Type_;
static PyTypeObject *AdjEntIndices_Type_;

#define CreateEnt_Type *CreateEnt_Type_
#define AdjEntIndices_Type *AdjEntIndices_Type_

static PyTypeObject iMesh_Type;
static PyTypeObject iMeshIter_Type;
static PyTypeObject iMeshEntitySet_Type;
static PyTypeObject iMeshTag_Type;

/* automatic method/property declarators */
#define IMESH_METHOD(cls, name, type)                    \
    { #name, (PyCFunction)(cls ## Obj_ ## name), (type), \
      IMESHDOC_ ## cls ## _ ## name }

#define IMESH_GET(cls, name)                      \
    { #name, (getter)(cls ## Obj_get ## name), 0, \
      IMESHDOC_ ## cls ## _ ## name, 0 }

#define IMESH_GETSET(cls, name)                \
    { #name, (getter)(cls ## Obj_get ## name), \
             (setter)(cls ## Obj_set ## name), \
      IMESHDOC_ ## cls ## _ ## name, 0 }

static int
checkError(iMesh_Instance mesh,int err)
{
    if(err)
    {
        char descr[120];
        iMesh_getDescription(mesh,descr,sizeof(descr)-1);
        PyErr_SetString(PyExc_Errors[err-1],descr);
        return 1;
    }
    else
        return 0;
}

static int
iMeshTopology_Cvt(PyObject *object,int *val)
{
    int tmp = PyInt_AsLong(object);
    if(PyErr_Occurred())
        return 0;
    if(tmp < iMesh_EntityTopology_MIN || tmp > iMesh_EntityTopology_MAX)
    {
        PyErr_SetString(PyExc_ValueError,ERR_INVALID_TOPO);
        return 0;
    }

    *val = tmp;
    return 1;
}

static PyObject *
iMesh_FromInstance(iMesh_Instance instance)
{
    iMesh_Object *o = PyObject_AllocNew(iMesh_Object,&iMesh_Type);
    if(o == NULL)
        return NULL;

    o->handle = instance;
    o->owned = 0;
    return (PyObject*)o;
}

static PyObject *
iMeshEntitySet_FromHandle(iMesh_Object *instance,iBase_EntitySetHandle handle)
{
    iMeshEntitySet_Object *o = iMeshEntitySet_New();
    if(o == NULL)
        return NULL;

    o->instance = instance;
    o->base.handle = handle;
    Py_INCREF(o->instance);
    return (PyObject*)o;
}

static iMesh_Object *
iMeshEntitySet_GetInstance(PyObject *o)
{
    if(iMeshEntitySet_Check(o))
        return iMeshEntitySet_GET_INSTANCE(o);

    if(o == NULL)
        PyErr_BadArgument();
    else
        PyErr_SetString(PyExc_TypeError,"iMesh.EntitySet is required");
    return NULL;
}

static PyObject *
iMeshTag_FromHandle(iMesh_Object *instance,iBase_TagHandle handle)
{
    iMeshTag_Object *o = iMeshTag_New();
    if(o == NULL)
        return NULL;

    o->instance = instance;
    o->base.handle = handle;
    Py_INCREF(o->instance);
    return (PyObject*)o;
}

static iMesh_Object *
iMeshTag_GetInstance(PyObject *o)
{
    if(iMeshTag_Check(o))
        return iMeshTag_GET_INSTANCE(o);

    if(o == NULL)
        PyErr_BadArgument();
    else
        PyErr_SetString(PyExc_TypeError,"iMesh.Tag is required");
    return NULL;
}

static int
iMeshObj_init(iMesh_Object *self,PyObject *args,PyObject *kw)
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
        iMesh_dtor(self->handle,&err);
        if(checkError(self->handle,err))
            return -1;
    }
    iMesh_newMesh(options,&self->handle,&err,strlen(options));
    if(checkError(self->handle,err))
        return -1;
    self->owned = 1;
    return 0;
}

static void
iMeshObj_dealloc(iMesh_Object *self)
{
    if(self->handle && self->owned)
    {
        int err;
        iMesh_dtor(self->handle,&err);
    }
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
iMeshObj_getrootSet(iMesh_Object *self,void *closure)
{
    int err;
    iBase_EntitySetHandle handle;

    iMesh_getRootSet(self->handle,&handle,&err);
    if(checkError(self->handle,err))
        return NULL;

    return iMeshEntitySet_FromHandle(self,handle);
}


static PyObject *
iMeshObj_getgeometricDimension(iMesh_Object *self,void *closure)
{
    int dim,err;
    iMesh_getGeometricDimension(self->handle,&dim,&err);
    if(checkError(self->handle,err))
        return NULL;

    return PyInt_FromLong(dim);
}

static int
iMeshObj_setgeometricDimension(iMesh_Object *self,PyObject *value,void *closure)
{
    int dim,err;

    if(value == NULL)
    {
        PyErr_SetString(PyExc_TypeError, 
                        "Cannot delete the geometricDimension attribute");
        return -1;
    }

    dim = PyInt_AsLong(value);
    if(PyErr_Occurred())
        return -1;

    iMesh_setGeometricDimension(self->handle,dim,&err);
    if(checkError(self->handle,err))
        return -1;

    return 0;
}

static PyObject *
iMeshObj_getdefaultStorage(iMesh_Object *self,void *closure)
{
    int order,err;

    iMesh_getDfltStorage(self->handle,&order,&err);
    if(checkError(self->handle,err))
        return NULL;

    return PyInt_FromLong(order);
}

static PyObject *
iMeshObj_getadjTable(iMesh_Object *self,void *closure)
{
    int err;

    iBase_OutArray adjtable = {0};

    iMesh_getAdjTable(self->handle,PASS_OUTARR(int,adjtable),&err);
    if(checkError(self->handle,err))
        return NULL;

    npy_intp dims[] = {4,4};
    return PyArray_NewFromOut(2,dims,NPY_INT,&adjtable);
}

static int
iMeshObj_setadjTable(iMesh_Object *self,PyObject *value,void *closure)
{
    PyObject *adj;
    int adjtable[16];
    int err;

    if(value == NULL)
    {
        PyErr_SetString(PyExc_TypeError, 
                        "Cannot delete the adjTable attribute");
        return -1;
    }

    adj = PyArray_FROMANY(value,NPY_INT,1,2,NPY_C_CONTIGUOUS);
    if ((PyArray_NDIM(adj) == 1 && PyArray_DIM(adj,0) != 16) ||
        (PyArray_NDIM(adj) == 2 && (PyArray_DIM(adj,0) != 4 ||
                                    PyArray_DIM(adj,1) != 4))) {
        PyErr_SetString(PyExc_ValueError, 
                        "expected 4x4 matrix of adjacency values");
        return -1;
    }
    /* copy the values since setAdjTable modifies them */
    memcpy(adjtable,PyArray_DATA(adj),sizeof(int)*16);
    Py_DECREF(adj);

    iMesh_setAdjTable(self->handle,adjtable,16,&err);
    if(checkError(self->handle,err))
        return -1;

    return 0;
}

static PyObject *
iMeshObj_optimize(iMesh_Object *self)
{
    int err;
    int invalidated;

    iMesh_optimize(self->handle,&invalidated,&err);
    if(checkError(self->handle,err))
        return NULL;

    return PyBool_FromLong(invalidated);
}

static PyObject *
iMeshObj_createVtx(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"coords","storage_order","out",0};
    int err;
    PyObject *in_verts,*verts;
    int storage_order = iBase_INTERLEAVED;

    iBase_OutArray entities = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&O&",kwlist,&in_verts,
                                    iBaseStorageOrder_Cvt,&storage_order,
                                    iBaseBuffer_Cvt,&entities))
        return NULL;

    verts = PyArray_ToVectors(in_verts,NPY_DOUBLE,2,3,
                              storage_order==iBase_INTERLEAVED);
    if(verts)
    {
        double *coords = PyArray_DATA(verts);
        int size = PyArray_SIZE(verts);

        iMesh_createVtxArr(self->handle,size/3,storage_order,coords,size,
                           PASS_OUTARR_ENT(entities),&err);
        Py_DECREF(verts);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {entities.size};
        return PyArray_NewFromOut(1,dims,NPY_IBASEENT,&entities);
    }

    verts = PyArray_ToVectors(in_verts,NPY_DOUBLE,1,3,0);
    if(verts)
    {
        double *v = PyArray_DATA(verts);
        iBase_EntityHandle handle;

        iMesh_createVtx(self->handle,v[0],v[1],v[2],&handle,&err);
        Py_DECREF(verts);
        if(checkError(self->handle,err))
            return NULL;
        return iBaseEntity_FromHandle(handle);
    }

    PyErr_SetString(PyExc_ValueError,ERR_ARR_DIMS);
    return NULL;
}

static PyObject *
iMeshObj_createEnt(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"topo","entities",0};
    int err;
    int topo;
    PyObject *in_ents,*ents;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O&O",kwlist,iMeshTopology_Cvt,
                                    &topo,&in_ents))
        return NULL;

    ents = PyArray_FROMANY(in_ents,NPY_IBASEENT,1,1,NPY_C_CONTIGUOUS);
    if(ents == NULL)
        return NULL;

    iBase_EntityHandle *lower = PyArray_DATA(ents);
    int size = PyArray_SIZE(ents);

    iBase_EntityHandle handle;
    int status;

    iMesh_createEnt(self->handle,topo,lower,size,&handle,&status,&err);
    Py_DECREF(ents);
    if(checkError(self->handle,err))
        return NULL;

    return NamedTuple_New(&CreateEnt_Type,"(Ni)",iBaseEntity_FromHandle(handle),
                          status);
}

static PyObject *
iMeshObj_createEntArr(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"topo","entities","out",0};
    int err;
    int topo;
    PyObject *in_ents,*ents;
    PyObject *out = NULL;

    iBase_OutArray entities = {0};
    iBase_OutArray status = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O&O|O!",kwlist,iMeshTopology_Cvt,
                                    &topo,&in_ents,&PyTuple_Type,&out))
        return NULL;

    if(out && !PyArg_ParseTuple(out,"O&O&",iBaseBuffer_Cvt,&entities,
                                           iBaseBuffer_Cvt,&status))
        return NULL;

    ents = PyArray_FROMANY(in_ents,NPY_IBASEENT,1,1,NPY_C_CONTIGUOUS);
    if(ents == NULL)
        return NULL;

    iBase_EntityHandle *lower = PyArray_DATA(ents);
    int size = PyArray_SIZE(ents);

    iMesh_createEntArr(self->handle,topo,lower,size,PASS_OUTARR_ENT(entities),
                       PASS_OUTARR(int,status),&err);
    Py_DECREF(ents);
    if(checkError(self->handle,err))
        return NULL;

    npy_intp ent_dims[] = {entities.size};
    npy_intp stat_dims[] = {status.size};
    return NamedTuple_New(&CreateEnt_Type,"(NN)",
        PyArray_NewFromOut(1,ent_dims,NPY_IBASEENT,&entities),
        PyArray_NewFromOut(1,stat_dims,NPY_INT,&status)
        );
}

static PyObject *
iMeshObj_deleteEnt(iMesh_Object *self,PyObject *args,PyObject *kw)
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

        iMesh_deleteEntArr(self->handle,entities,size,&err);
        Py_DECREF(ents);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        iMesh_deleteEnt(self->handle,entity,&err);
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
iMeshObj_getVtxCoords(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","storage_order","out",0};
    int err;
    PyObject *in_ents,*ents;
    int storage_order = iBase_INTERLEAVED;

    iBase_OutArray coords = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&O&",kwlist,&in_ents,
                                    iBaseStorageOrder_Cvt,&storage_order,
                                    iBaseBuffer_Cvt,&coords))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int size = PyArray_SIZE(ents);

        iMesh_getVtxArrCoords(self->handle,entities,size,storage_order,
                              PASS_OUTARR(double,coords),&err);
        Py_DECREF(ents);

        if(checkError(self->handle,err))
            return NULL;

        /* calculate the dimensions of the output array */
        npy_intp dims[2];
        int vec_index = storage_order != iBase_BLOCKED;
        dims[ vec_index] = 3;
        dims[!vec_index] = coords.size/3;
        return PyArray_NewFromOut(2,dims,NPY_DOUBLE,&coords);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        double *v = malloc(3*sizeof(double));

        iMesh_getVtxCoord(self->handle,entity,v+0,v+1,v+2,&err);
        if(checkError(self->handle,err))
        {
            free(v);
            return NULL;
        }

        npy_intp dims[] = {3};
        return PyArray_NewFromMalloc(1,dims,NPY_DOUBLE,v);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iMeshObj_setVtxCoords(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","coords","storage_order",0};
    int err;
    PyObject *in_ents,*ents;
    PyObject *in_verts,*verts;
    int storage_order = iBase_INTERLEAVED;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO|O&",kwlist,&in_ents,&in_verts,
                                    iBaseStorageOrder_Cvt,&storage_order))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        verts = PyArray_ToVectors(in_verts,NPY_DOUBLE,2,3,
                                  storage_order==iBase_INTERLEAVED);
        if(!verts)
            goto err;

        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int ent_size = PyArray_SIZE(ents);
        double *coords = PyArray_DATA(verts);
        int coord_size = PyArray_SIZE(verts);

        iMesh_setVtxArrCoords(self->handle,entities,ent_size,storage_order,
                              coords,coord_size,&err);
        Py_DECREF(ents);
        Py_DECREF(verts);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        verts = PyArray_ToVectors(in_verts,NPY_DOUBLE,1,3,0);
        if(!verts)
            goto err;

        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        double *v = PyArray_DATA(verts);

        iMesh_setVtxCoord(self->handle,entity, v[0],v[1],v[2], &err);
        Py_DECREF(verts);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }

    if(checkError(self->handle,err))
        return NULL;
    Py_RETURN_NONE;

err:
    Py_XDECREF(ents);
    Py_XDECREF(verts);
    return NULL;
}

static PyObject *
iMeshObj_getEntType(iMesh_Object *self,PyObject *args,PyObject *kw)
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

        iMesh_getEntArrType(self->handle,entities,size,PASS_OUTARR(int,types),
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

        iMesh_getEntType(self->handle,entity,&type,&err);
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
iMeshObj_getEntTopo(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","out",0};
    int err;
    PyObject *in_ents,*ents;

    iBase_OutArray topos = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&",kwlist,&in_ents,
                                    iBaseBuffer_Cvt,&topos))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int size = PyArray_SIZE(ents);

        iMesh_getEntArrTopo(self->handle,entities,size,PASS_OUTARR(int,topos),
                            &err);
        Py_DECREF(ents);
        if(checkError(self->handle,err))
            return NULL;

        npy_intp dims[] = {topos.size};
        return PyArray_NewFromOut(1,dims,NPY_INT,&topos);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        int topo;

        iMesh_getEntTopo(self->handle,entity,&topo,&err);
        if(checkError(self->handle,err))
            return NULL;

        return PyInt_FromLong(topo);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTARR);
        return NULL;
    }
}

static PyObject *
iMeshObj_getEntAdj(iMesh_Object *self,PyObject *args,PyObject *kw)
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

        iMesh_getEntArrAdj(self->handle,entities,size,type_req,
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

        iMesh_getEntAdj(self->handle,entity,type_req,PASS_OUTARR_ENT(adj),&err);
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
iMeshObj_getEnt2ndAdj(iMesh_Object *self,PyObject *args,PyObject *kw)
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

        iMesh_getEntArr2ndAdj(self->handle,entities,size,bridge_type,type_req,
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

        iMesh_getEnt2ndAdj(self->handle,entity,bridge_type,type_req,
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
iMeshObj_createEntSet(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"ordered",0};
    int err;
    PyObject *ordered;

    iBase_EntitySetHandle handle;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&PyBool_Type,&ordered))
        return NULL;

    iMesh_createEntSet(self->handle,(ordered==Py_True),&handle,&err);
    if(checkError(self->handle,err))
        return NULL;

    return iMeshEntitySet_FromHandle(self,handle);
}

static PyObject *
iMeshObj_destroyEntSet(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    int err;
    iBaseEntitySet_Object *set;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntitySet_Type,
                                    &set))
        return NULL;

    iMesh_destroyEntSet(self->handle,set->handle,&err);
    if(checkError(self->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iMeshObj_createTag(iMesh_Object *self,PyObject *args,PyObject *kw)
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

    iMesh_createTag(self->handle,name,size,type,&handle,&err,strlen(name));
    if(checkError(self->handle,err))
        return NULL;

    return iMeshTag_FromHandle(self,handle);
}

static PyObject *
iMeshObj_destroyTag(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"tag","force",0};
    int err;
    iBaseTag_Object *tag;
    PyObject *forced;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!O!",kwlist,&iBaseTag_Type,&tag,
                                    &PyBool_Type,&forced))
        return NULL;

    iMesh_destroyTag(self->handle,tag->handle,(forced==Py_True),&err);
    if(checkError(self->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iMeshObj_getTagHandle(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"name",0};
    int err;
    const char *name;

    iBase_TagHandle handle;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"s",kwlist,&name))
        return NULL;

    iMesh_getTagHandle(self->handle,name,&handle,&err,strlen(name));
    if(checkError(self->handle,err))
        return NULL;

    return iMeshTag_FromHandle(self,handle);
}

static PyObject *
iMeshObj_getAllTags(iMesh_Object *self,PyObject *args,PyObject *kw)
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

        iMesh_getAllEntSetTags(self->handle,set,PASS_OUTARR_TAG(tags),&err);
        if(checkError(self->handle,err))
            return NULL;
    }
    else if(iBaseEntity_Check(ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(ents);

        iMesh_getAllTags(self->handle,entity,PASS_OUTARR_TAG(tags),&err);
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
iMeshObj_repr(iMesh_Object *self)
{
    return PyString_FromFormat("<%s %p>",self->ob_type->tp_name,self->handle);
}

static PyObject *
iMeshObj_richcompare(iMesh_Object *lhs,iMesh_Object *rhs,int op)
{
    if(!iMesh_Check(lhs) || !iMesh_Check(rhs))
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
iMeshObj_hash(iMesh_Object *self)
{
    return (long)self->handle;
}

static PyMethodDef iMeshObj_methods[] = {
    IMESH_METHOD(iMesh, optimize,      METH_NOARGS),
    IMESH_METHOD(iMesh, createVtx,     METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMesh, createEnt,     METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMesh, createEntArr,  METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMesh, deleteEnt,     METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMesh, getVtxCoords,  METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMesh, setVtxCoords,  METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMesh, getEntType,    METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMesh, getEntTopo,    METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMesh, getEntAdj,     METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMesh, getEnt2ndAdj,  METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMesh, createEntSet,  METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMesh, destroyEntSet, METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMesh, createTag,     METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMesh, destroyTag,    METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMesh, getTagHandle,  METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMesh, getAllTags,    METH_VARARGS|METH_KEYWORDS),
    {0}
};

static PyGetSetDef iMeshObj_getset[] = {
    IMESH_GET   (iMesh, rootSet),
    IMESH_GETSET(iMesh, geometricDimension),
    IMESH_GET   (iMesh, defaultStorage),
    IMESH_GETSET(iMesh, adjTable),
    {0}
};

static PyObject * iMeshObj_getAttr(PyObject *self,PyObject *attr_name)
{
    PyObject *ret;

    ret = PyObject_GenericGetAttr(self,attr_name);
    if(ret)
        return ret;
    else
    {
        PyErr_Clear();
        PyObject *root = iMeshObj_getrootSet((iMesh_Object*)self,0);
        if(!root)
            return NULL;
        ret = PyObject_GetAttr(root,attr_name);
        Py_DECREF(root);
        return ret;
    }
}

static PyTypeObject iMesh_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iMesh.Mesh",                       /* tp_name */
    sizeof(iMesh_Object),                     /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)iMeshObj_dealloc,             /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    (reprfunc)iMeshObj_repr,                  /* tp_repr */
    0,                                        /* tp_as_number */
    0,                                        /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    (hashfunc)iMeshObj_hash,                  /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str */
    iMeshObj_getAttr,                         /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    IMESHDOC_iMesh,                           /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    (richcmpfunc)iMeshObj_richcompare,        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    iMeshObj_methods,                         /* tp_methods */
    0,                                        /* tp_members */
    iMeshObj_getset,                          /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)iMeshObj_init,                  /* tp_init */
    0,                                        /* tp_alloc */
    0,                                        /* tp_new */
};


static PyMethodDef module_methods[] = {
    {0}
};

ENUM_TYPE(iMeshTopology,"iMesh.Topology","");

PyMODINIT_FUNC initiMesh(void)
{
    PyObject *m;
    m = Py_InitModule("iMesh",module_methods);
    import_array();
    import_ufunc();
    import_iBase();
    import_helpers();

    /***** register C API *****/
    static void *IMesh_API[] = {
        &iMesh_Type,
        &iMeshIter_Type,
        &iMeshEntitySet_Type,
        &iMeshTag_Type,
        &iMesh_FromInstance,
        &iMeshEntitySet_FromHandle,
        &iMeshEntitySet_GetInstance,
        &iMeshTag_FromHandle,
        &iMeshTag_GetInstance,
        &CreateEnt_Type_,
        &AdjEntIndices_Type_,
        &iMeshTopology_Cvt,
    };
    PyObject *api_obj;

    /* Create a CObject containing the API pointer array's address */
    api_obj = PyCObject_FromVoidPtr(IMesh_API,NULL);

    if(api_obj != NULL)
        PyModule_AddObject(m, "_C_API", api_obj);

    REGISTER_CLASS_BASE(m,"Mesh",     iMesh,         iBase);
    REGISTER_CLASS_BASE(m,"EntitySet",iMeshEntitySet,iBaseEntitySet);
    REGISTER_CLASS_BASE(m,"Tag",      iMeshTag,      iBaseTag);
    REGISTER_CLASS     (m,"Iterator", iMeshIter);

    /***** initialize topology enum *****/
    REGISTER_CLASS(m,"Topology",iMeshTopology);

    ADD_ENUM(iMeshTopology,"point",         iMesh_POINT);
    ADD_ENUM(iMeshTopology,"line_segment",  iMesh_LINE_SEGMENT);
    ADD_ENUM(iMeshTopology,"polygon",       iMesh_POLYGON);
    ADD_ENUM(iMeshTopology,"triangle",      iMesh_TRIANGLE);
    ADD_ENUM(iMeshTopology,"quadrilateral", iMesh_QUADRILATERAL);
    ADD_ENUM(iMeshTopology,"polyhedron",    iMesh_POLYHEDRON);
    ADD_ENUM(iMeshTopology,"tetrahedron",   iMesh_TETRAHEDRON);
    ADD_ENUM(iMeshTopology,"hexahedron",    iMesh_HEXAHEDRON);
    ADD_ENUM(iMeshTopology,"prism",         iMesh_PRISM);
    ADD_ENUM(iMeshTopology,"pyramid",       iMesh_PYRAMID);
    ADD_ENUM(iMeshTopology,"septahedron",   iMesh_SEPTAHEDRON);
    ADD_ENUM(iMeshTopology,"all",           iMesh_ALL_TOPOLOGIES);

    /***** initialize iMesh NumPy array *****/
    iBase_RegisterSubArray(NPY_IBASEENTSET,&iMesh_Type,&iMeshEntitySet_Type,
                           (arrgetfunc)iMeshEntitySet_GetInstance,
                           (arrcreatefunc)iMeshEntitySet_FromHandle);
    iBase_RegisterSubArray(NPY_IBASETAG,&iMesh_Type,&iMeshTag_Type,
                           (arrgetfunc)iMeshTag_GetInstance,
                           (arrcreatefunc)iMeshTag_FromHandle);

    /***** create named tuple types *****/
    CreateEnt_Type_     = NamedTuple_CreateType(m,"create_ent","entity status");
    AdjEntIndices_Type_ = NamedTuple_CreateType(m,"adj_ent",   "entities adj");
}

/* Include source files so that everything is in one translation unit */
#include "iMesh_entSet.inl"
#include "iMesh_iter.inl"
#include "iMesh_tag.inl"
