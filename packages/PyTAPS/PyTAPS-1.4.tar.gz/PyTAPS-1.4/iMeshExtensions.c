#include "iMesh_Python.h"

#include <Python.h>
#include <iMesh.h>
#include <iMesh_extensions.h>
#include "numpy_extensions.h"
#include "errors.h"

/* automatic method/property declarators */
#define IMESH_METHOD(cls, name, type)                    \
    { #name, (PyCFunction)(cls ## Obj_ ## name), (type), \
      "" }

/* This function is taken directly from Python/Objects/typeobject.c. */
static int
add_methods(PyTypeObject *type, PyMethodDef *meth)
{
    PyObject *dict = type->tp_dict;

    for (; meth->ml_name != NULL; meth++) {
        PyObject *descr;
        if (PyDict_GetItemString(dict, meth->ml_name) &&
            !(meth->ml_flags & METH_COEXIST))
                continue;
        if (meth->ml_flags & METH_CLASS) {
            if (meth->ml_flags & METH_STATIC) {
                PyErr_SetString(PyExc_ValueError,
                     "method cannot be both class and static");
                return -1;
            }
            descr = PyDescr_NewClassMethod(type, meth);
        }
        else if (meth->ml_flags & METH_STATIC) {
            PyObject *cfunc = PyCFunction_New(meth, NULL);
            if (cfunc == NULL)
                return -1;
            descr = PyStaticMethod_New(cfunc);
            Py_DECREF(cfunc);
        }
        else {
            descr = PyDescr_NewMethod(type, meth);
        }
        if (descr == NULL)
            return -1;
        if (PyDict_SetItemString(dict, meth->ml_name, descr) < 0)
            return -1;
        Py_DECREF(descr);
    }
    return 0;
}

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

static PyObject *
iMeshObj_getAllTags(iMesh_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","out",0};
    int err;
    PyObject *ents = NULL;

    iBase_OutArray tags = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"|OO&",kwlist,&ents,
                                    iBaseBuffer_Cvt,&tags))
        return NULL;

    if(ents == NULL)
    {
        iMesh_getAllIfaceTags(self->handle,PASS_OUTARR_TAG(tags),&err);
    }
    else if(iBaseEntitySet_Check(ents))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GET_HANDLE(ents);
        iMesh_getAllEntSetTags(self->handle,set,PASS_OUTARR_TAG(tags),&err);
    }
    else if(iBaseEntity_Check(ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(ents);
        iMesh_getAllTags(self->handle,entity,PASS_OUTARR_TAG(tags),&err);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTSET);
        return NULL;
    }

    if(checkError(self->handle,err))
        return NULL;

    npy_intp dims[] = {tags.size};
    return PyArray_NewFromOutBase(1,dims,NPY_IBASETAG,&tags,
                                  (iBase_Object*)self);
}

static PyObject *
iMeshEntSetObj_getEntitiesRec(iMeshEntitySet_Object *self,PyObject *args,
                              PyObject *kw)
{
    static char *kwlist[] = {"type","topo","recursive","out",0};
    int err;
    enum iBase_EntityType type = iBase_ALL_TYPES;
    enum iMesh_EntityTopology topo = iMesh_ALL_TOPOLOGIES;
    PyObject *recursive = Py_True;

    iBase_OutArray entities = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"|O&O&O!O&",kwlist,iBaseType_Cvt,
                                    &type,iMeshTopology_Cvt,&topo,&PyBool_Type,
                                    &recursive,iBaseBuffer_Cvt,&entities))
        return NULL;

    iMesh_getEntitiesRec(self->instance->handle,self->base.handle,type,topo,
                         (recursive == Py_True),PASS_OUTARR_ENT(entities),&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {entities.size};
    return PyArray_NewFromOut(1,dims,NPY_IBASEENT,&entities);
}

static PyObject *
iMeshEntSetObj_getNumOfTypeRec(iMeshEntitySet_Object *self,PyObject *args,
                               PyObject *kw)
{
    static char *kwlist[] = {"type","recursive",0};
    int err;
    enum iBase_EntityType type;
    PyObject *recursive = NULL;

    int num;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O&|O!",kwlist,iBaseType_Cvt,&type,
                                    &PyBool_Type,&recursive))
        return NULL;

    iMesh_getNumOfTypeRec(self->instance->handle,self->base.handle,type,
                          (recursive == NULL || recursive == Py_True),&num,
                          &err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num);
}

static PyObject *
iMeshEntSetObj_getNumOfTopoRec(iMeshEntitySet_Object *self,PyObject *args,
                               PyObject *kw)
{
    static char *kwlist[] = {"topology","recursive",0};
    int err;
    enum iMesh_EntityTopology topo;
    PyObject *recursive = Py_True;

    int num;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O&|O!",kwlist,iMeshTopology_Cvt,
                                    &topo,&PyBool_Type,&recursive))
        return NULL;

    iMesh_getNumOfTopoRec(self->instance->handle,self->base.handle,topo,
                          (recursive == Py_True),&num,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num);
}

static PyObject *
iMeshEntSetObj_getEntsByTagsRec(iMeshEntitySet_Object *self,PyObject *args,
                                PyObject *kw)
{
    static char *kwlist[] = {"type","topology","tags","tag_values","recursive",
                             "out",0};
    int err;
    enum iBase_EntityType type = iBase_ALL_TYPES;
    enum iMesh_EntityTopology topo = iMesh_ALL_TOPOLOGIES;
    PyObject *in_tags = NULL,*tags = NULL;
    PyObject *in_tag_values = NULL; /*,*tag_values = NULL;*/
    PyObject *recursive = Py_True;

    iBase_OutArray entities = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"|O&O&OOO!O&",kwlist,iBaseType_Cvt,
                                    &type,iMeshTopology_Cvt,&topo,
                                    &in_tags,&in_tag_values,
                                    &PyBool_Type,&recursive,
                                    iBaseBuffer_Cvt,&entities))
        return NULL;

    if(in_tags)
        tags = PyArray_FROM_OT(in_tags,NPY_IBASETAG);
    if(!tags)
        return NULL;
    if(PyArray_NDIM(tags) > 1)
    {
        PyErr_SetString(PyExc_ValueError,
                        "object of too large depth for desired array");
        return NULL;
    }

    /* TODO: tag value stuff */

    iMesh_getEntsByTagsRec(self->instance->handle,self->base.handle,type,topo,
                           PyArray_DATA(tags),0,PyArray_SIZE(tags),
                           (recursive == Py_True),PASS_OUTARR_ENT(entities),
                           &err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {entities.size};
    return PyArray_NewFromOut(1,dims,NPY_IBASEENT,&entities);
}

static PyObject *
iMeshEntSetObj_getEntSetsByTagsRec(iMeshEntitySet_Object *self,PyObject *args,
                                   PyObject *kw)
{
    static char *kwlist[] = {"tags","tag_values","recursive","out",0};
    int err;
    PyObject *in_tags = NULL,*tags = NULL;
    PyObject *in_tag_values = NULL; /*,*tag_values = NULL;*/
    PyObject *recursive = Py_True;

    iBase_OutArray sets = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|OO!O&",kwlist,&in_tags,
                                    &in_tag_values,&PyBool_Type,&recursive,
                                    iBaseBuffer_Cvt,&sets))
        return NULL;

    tags = PyArray_FROM_OT(in_tags,NPY_IBASETAG);
    if(!tags)
        return NULL;
    if(PyArray_NDIM(tags) > 1)
    {
        PyErr_SetString(PyExc_ValueError,
                        "object of too large depth for desired array");
        return NULL;
    }

    /* TODO: tag value stuff */

    iMesh_getEntSetsByTagsRec(self->instance->handle,self->base.handle,
                              PyArray_DATA(tags),0,PyArray_SIZE(tags),
                              (recursive == Py_True),PASS_OUTARR_SET(sets),
                              &err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {sets.size};
    return PyArray_NewFromOut(1,dims,NPY_IBASEENTSET,&sets);
}

static PyObject *
iMeshEntSetObj_createStructuredMesh(iMeshEntitySet_Object *self,PyObject *args,
                                    PyObject *kw)
{
    static char *kwlist[] = {"local_dims","global_dims","i","j","k",
                             "resolve_shared","ghost_dim","bridge_dim",
                             "num_layers","addl_ents","vert_gids","elem_gids",
                             "create_set",0};
    int err;
    PyObject *in_local_dims,*local_dims;
    PyObject *in_global_dims = NULL,*global_dims = NULL;
    PyObject *in_vals[3] = {NULL,NULL,NULL};
    PyObject *vals[3] = {NULL,NULL,NULL};
    PyObject *resolve_shared = Py_False;
    int ghost_dim = -1;
    int bridge_dim = -1;
    int num_layers = -1;
    int addl_ents = 0; /* ??? */
    PyObject *vert_gids = Py_False;
    PyObject *elem_gids = Py_False;
    PyObject *create_set = Py_False;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|OOOOO!iiiiO!O!O!",kwlist,
                                    &in_local_dims,&in_global_dims,in_vals+0,
                                    in_vals+1,in_vals+2,&PyBool_Type,
                                    &resolve_shared,&ghost_dim,&bridge_dim,
                                    &num_layers,&addl_ents,&PyBool_Type,
                                    &vert_gids,&PyBool_Type,&elem_gids,
                                    &PyBool_Type,&create_set))
        return NULL;

    local_dims = PyArray_ToVectors(in_local_dims,NPY_INT,1,6,0);
    if(!local_dims)
        return NULL;

    int *gdims = NULL;
    if(in_global_dims) {
        global_dims = PyArray_ToVectors(in_global_dims,NPY_INT,1,6,0);
        if(!global_dims)
            return NULL;
        gdims = PyArray_DATA(global_dims);
    }

    double *data[3] = {NULL,NULL,NULL};
    int i;
    for(i=0; i<3; i++) {
        if(in_vals[i]) {
            vals[i] = PyArray_FROMANY(in_vals[i],NPY_DOUBLE,1,1,
                                      NPY_C_CONTIGUOUS);
            if(!vals[i])
                return NULL;
            data[i] = PyArray_DATA(vals[i]);
        }
    }

    iBase_EntitySetHandle out_set = 0;
    iBase_EntitySetHandle *set_ptr = NULL;
    if(create_set==Py_True)
        set_ptr = &out_set;
    else if(self->base.handle)
        set_ptr = &self->base.handle;

    iMesh_createStructuredMesh(self->instance->handle,PyArray_DATA(local_dims),
                               gdims,data[0],data[1],data[2],
                               (resolve_shared==Py_True),ghost_dim,bridge_dim,
                               num_layers,addl_ents,(vert_gids==Py_True),
                               (elem_gids==Py_True),set_ptr,&err);
    Py_DECREF(local_dims);
    Py_XDECREF(global_dims);
    Py_XDECREF(vals[0]);
    Py_XDECREF(vals[1]);
    Py_XDECREF(vals[2]);
    if(checkError(self->instance->handle,err))
        return NULL;

    if(create_set==Py_True)
        return iMeshEntitySet_FromHandle(self->instance,out_set);
    else
        Py_RETURN_NONE;
}

static PyObject *
iMeshIterObj_step(iMeshIter_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"n",0};
    int err;
    int n;
    int at_end;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"i",kwlist,&n))
        return NULL;

    if(self->is_arr)
      iMesh_stepEntArrIter(self->instance->handle,self->iter.arr,n,&at_end,
                           &err);
    else
      iMesh_stepEntIter(self->instance->handle,self->iter.one,n,&at_end,&err);

    if(checkError(self->instance->handle,err))
        return NULL;

    return PyBool_FromLong(at_end);
}


static PyMethodDef iMesh_methods[] = {
    IMESH_METHOD(iMesh, getAllTags, METH_VARARGS|METH_KEYWORDS),
    {0}
};

static PyMethodDef iMeshEntSet_methods[] = {
    IMESH_METHOD(iMeshEntSet, getEntitiesRec,       METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, getNumOfTypeRec,      METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, getNumOfTopoRec,      METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, getEntsByTagsRec,     METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, getEntSetsByTagsRec,  METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, createStructuredMesh, METH_VARARGS|METH_KEYWORDS),
    {0}
};

static PyMethodDef iMeshIter_methods[] = {
    IMESH_METHOD(iMeshIter, step, METH_VARARGS|METH_KEYWORDS),
    {0}
};

static PyMethodDef module_methods[] = {
    {0}
};

PyMODINIT_FUNC initiMeshExtensions(void)
{
    PyObject *m;
    m = Py_InitModule("iMeshExtensions",module_methods);

    import_array();
    import_iBase();
    import_iMesh();

    add_methods(&iMesh_Type, iMesh_methods);
    add_methods(&iMeshEntitySet_Type, iMeshEntSet_methods);
    add_methods(&iMeshIter_Type, iMeshIter_methods);
}
