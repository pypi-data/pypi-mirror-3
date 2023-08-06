#include "errors.h"
#include "iMesh_Python.h"
#include "iBase_Python.h"
#include "structmember.h"

static PyObject *
iMeshEntSetObj_new(PyTypeObject *cls,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set","instance",0};
    iBaseEntitySet_Object *set;
    iMesh_Object *instance = NULL;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!|O!",kwlist,
                                    &iBaseEntitySet_Type,&set,&iMesh_Type,
                                    &instance))
        return NULL;

    if(instance)
    {
        if(iMeshEntitySet_Check(set))
        {
            PyErr_SetString(PyExc_ValueError,ERR_MESH_SET_CTOR);
            return NULL;
        }
    }
    else
    {
        if(!iMeshEntitySet_Check(set))
        {
            PyErr_SetString(PyExc_ValueError,ERR_EXP_INSTANCE);
            return NULL;
        }
        instance = iMeshEntitySet_GET_INSTANCE(set);
    }

    return iMeshEntitySet_FromHandle(instance,set->handle);
}

static void
iMeshEntSetObj_dealloc(iMeshEntitySet_Object *self)
{
    Py_XDECREF(self->instance);
    self->base.ob_type->tp_base->tp_dealloc((PyObject*)self);
}

static PyObject *
iMeshEntSetObj_getisList(iMeshEntitySet_Object *self,void *closure)
{
    int is_list,err;
    iMesh_isList(self->instance->handle,self->base.handle,&is_list,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyBool_FromLong(is_list);
}

static PyObject *
iMeshEntSetObj_load(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"filename","options",0};
    int err;
    const char *name = NULL;
    const char *options = "";

    if(!PyArg_ParseTupleAndKeywords(args,kw,"s|s",kwlist,&name,&options))
        return NULL;

    iMesh_load(self->instance->handle,self->base.handle,name,options,&err,
               strlen(name),strlen(options));
    if(checkError(self->instance->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iMeshEntSetObj_save(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"filename","options",0};
    int err;
    const char *name = NULL;
    const char *options = "";

    if(!PyArg_ParseTupleAndKeywords(args,kw,"s|s",kwlist,&name,&options))
        return NULL;

    iMesh_save(self->instance->handle,self->base.handle,name,options,&err,
               strlen(name),strlen(options));
    if(checkError(self->instance->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iMeshEntSetObj_getNumOfType(iMeshEntitySet_Object *self,PyObject *args,
                            PyObject *kw)
{
    static char *kwlist[] = {"type",0};
    int err;
    enum iBase_EntityType type;

    int num;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O&",kwlist,iBaseType_Cvt,&type))
        return NULL;

    iMesh_getNumOfType(self->instance->handle,self->base.handle,type,&num,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num);
}

static PyObject *
iMeshEntSetObj_getNumOfTopo(iMeshEntitySet_Object *self,PyObject *args,
                            PyObject *kw)
{
    static char *kwlist[] = {"topo",0};
    int err;
    enum iMesh_EntityTopology topo;

    int num;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O&",kwlist,iMeshTopology_Cvt,
                                    &topo))
        return NULL;

    iMesh_getNumOfTopo(self->instance->handle,self->base.handle,topo,&num,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num);
}

static Py_ssize_t
iMeshEntSetObj_len(iMeshEntitySet_Object *self)
{
    int num,err;

    iMesh_getNumOfType(self->instance->handle,self->base.handle,iBase_ALL_TYPES,
                       &num,&err);
    if(checkError(self->instance->handle,err))
        return -1;

    return num;
}

static PyObject *
iMeshEntSetObj_getEntities(iMeshEntitySet_Object *self,PyObject *args,
                           PyObject *kw)
{
    static char *kwlist[] = {"type","topo","out",0};
    int err;
    enum iBase_EntityType type = iBase_ALL_TYPES;
    enum iMesh_EntityTopology topo = iMesh_ALL_TOPOLOGIES;

    iBase_OutArray entities = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"|O&O&O&",kwlist,iBaseType_Cvt,
                                    &type,iMeshTopology_Cvt,&topo,
                                    iBaseBuffer_Cvt,&entities))
        return NULL;

    iMesh_getEntities(self->instance->handle,self->base.handle,type,topo,
                      PASS_OUTARR_ENT(entities),&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {entities.size};
    return PyArray_NewFromOut(1,dims,NPY_IBASEENT,&entities);
}

static PyObject *
iMeshEntSetObj_getAdjEntIndices(iMeshEntitySet_Object *self,PyObject *args,
                                PyObject *kw)
{
    static char *kwlist[] = {"type","topo","adj_type","out",0};
    int err;
    int type_requestor,topo_requestor,type_requested;
    PyObject *out = NULL;

    iBase_OutArray entities = {0};
    iBase_OutArray adj_ents = {0};
    iBase_OutArray indices  = {0};
    iBase_OutArray offsets  = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O&O&O&|O!",kwlist,
                                    iBaseType_Cvt,&type_requestor,
                                    iMeshTopology_Cvt,&topo_requestor,
                                    iBaseType_Cvt,&type_requested,
                                    &PyTuple_Type,&out))
        return NULL;

    if(out && (PyTuple_GET_SIZE(out) != 2 ||
               !iBaseBuffer_Cvt(PyTuple_GET_ITEM(out,0),&entities) ||
               !IndexedListBuffer_Cvt(PyTuple_GET_ITEM(out,1),&offsets,&indices,
                                      &adj_ents)))
    {
        PyErr_SetString(PyExc_ValueError,ERR_INVALID_OUT);
        return NULL;
    }

    iMesh_getAdjEntIndices(self->instance->handle,self->base.handle,
                           type_requestor,topo_requestor,type_requested,
                           PASS_OUTARR_ENT(entities),PASS_OUTARR_ENT(adj_ents),
                           PASS_OUTARR(int,indices),PASS_OUTARR(int,offsets),
                           &err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp ent_dims[] = {entities.size};
    npy_intp adj_dims[] = {adj_ents.size};
    npy_intp ind_dims[] = {indices.size};
    npy_intp off_dims[] = {offsets.size};

    return NamedTuple_New(&AdjEntIndices_Type,"NN",
        PyArray_NewFromOut(1,ent_dims,NPY_IBASEENT,&entities),
        IndexedList_New(
            PyArray_NewFromOut(1,off_dims,NPY_INT,&offsets),
            PyArray_NewFromOut(1,ind_dims,NPY_INT,&indices),
            PyArray_NewFromOut(1,adj_dims,NPY_IBASEENT,&adj_ents)
            )
        );
}

static PyObject *
iMeshEntSetObj_getNumEntSets(iMeshEntitySet_Object *self,PyObject *args,
                             PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int err;
    int hops=-1;

    int num_sets;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"|i",kwlist,&hops))
        return NULL;

    iMesh_getNumEntSets(self->instance->handle,self->base.handle,hops,
                        &num_sets,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num_sets);
}

static PyObject *
iMeshEntSetObj_getEntSets(iMeshEntitySet_Object *self,PyObject *args,
                          PyObject *kw)
{
    static char *kwlist[] = {"hops","out",0};
    int err;
    int hops=-1;

    iBase_OutArray sets = {0};
  
    if(!PyArg_ParseTupleAndKeywords(args,kw,"|iO&",kwlist,&hops,
                                    iBaseBuffer_Cvt,&sets))
        return NULL;

    iMesh_getEntSets(self->instance->handle,self->base.handle,hops,
                     PASS_OUTARR_SET(sets),&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {sets.size};
    return PyArray_NewFromOutBase(1,dims,NPY_IBASEENTSET,&sets,
                                  (iBase_Object*)self->instance);
}

static PyObject *
iMeshEntSetObj_add(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
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

        iMesh_addEntArrToSet(self->instance->handle,entities,size,
                             self->base.handle,&err);
        Py_DECREF(ents);
    }
    else if(iBaseEntitySet_Check(in_ents))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GET_HANDLE(in_ents);
        iMesh_addEntSet(self->instance->handle,set,self->base.handle,&err);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        iMesh_addEntToSet(self->instance->handle,entity,self->base.handle,&err);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return NULL;
    }

    if(checkError(self->instance->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iMeshEntSetObj_remove(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
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

        iMesh_rmvEntArrFromSet(self->instance->handle,entities,size,
                               self->base.handle,&err);
        Py_DECREF(ents);
    }
    else if(iBaseEntitySet_Check(in_ents))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GET_HANDLE(in_ents);
        iMesh_rmvEntSet(self->instance->handle,set,self->base.handle,&err);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        iMesh_rmvEntFromSet(self->instance->handle,entity,self->base.handle,
                            &err);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return NULL;
    }

    if(checkError(self->instance->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iMeshEntSetObj_contains(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","out",0};
    int err;
    PyObject *in_ents,*ents;

    iBase_OutArray contains = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&",kwlist,&in_ents,
                                    iBaseBuffer_Cvt,&contains))
        return NULL;

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int size = PyArray_SIZE(ents);

        iMesh_isEntArrContained(self->instance->handle,self->base.handle,
                                entities,size,PASS_OUTARR(int,contains),&err);
        Py_DECREF(ents);
        if(checkError(self->instance->handle,err))
            return NULL;

        npy_intp dims[] = {contains.size};
        npy_intp strides[] = {sizeof(int)/sizeof(npy_bool)};
        return PyArray_NewFromOutStrided(1,dims,strides,NPY_BOOL,&contains);
    }
    else if(iBaseEntitySet_Check(in_ents))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GET_HANDLE(in_ents);
        int contains;

        iMesh_isEntSetContained(self->instance->handle,self->base.handle,set,
                                &contains,&err);
        if(checkError(self->instance->handle,err))
            return NULL;

        return PyBool_FromLong(contains);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        int contains;

        iMesh_isEntContained(self->instance->handle,self->base.handle,entity,
                             &contains,&err);
        if(checkError(self->instance->handle,err))
            return NULL;

        return PyBool_FromLong(contains);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return NULL;
    }
}

static int
iMeshEntSetObj_in(iMeshEntitySet_Object *self,PyObject *value)
{
    int err;
    int contains;

    if(iBaseEntitySet_Check(value))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GET_HANDLE(value);
        iMesh_isEntSetContained(self->instance->handle,self->base.handle,set,
                                &contains,&err);
        if(checkError(self->instance->handle,err))
            return -1;

        return contains;
    }
    else if(iBaseEntity_Check(value))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(value);
        iMesh_isEntContained(self->instance->handle,self->base.handle,entity,
                             &contains,&err);
        if(checkError(self->instance->handle,err))
            return -1;

        return contains;
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ENT_OR_ENTSET);
        return -1;
    }
}

static PyObject *
iMeshEntSetObj_isChild(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    int err;
    iBaseEntitySet_Object *set;

    int is_child;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntitySet_Type,
                                    &set))
        return NULL;

    iMesh_isChildOf(self->instance->handle,self->base.handle,set->handle,
                    &is_child,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyBool_FromLong(is_child);
}

static PyObject *
iMeshEntSetObj_getNumChildren(iMeshEntitySet_Object *self,PyObject *args,
                              PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int err;
    int hops=-1;

    int num_children;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"|i",kwlist,&hops))
        return NULL;

    iMesh_getNumChld(self->instance->handle,self->base.handle,hops,
                     &num_children,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num_children);
}

static PyObject *
iMeshEntSetObj_getNumParents(iMeshEntitySet_Object *self,PyObject *args,
                             PyObject *kw)
{
    static char *kwlist[] = {"hops",0};
    int err;
    int hops=-1;

    int num_parents;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"|i",kwlist,&hops))
        return NULL;

    iMesh_getNumPrnt(self->instance->handle,self->base.handle,hops,
                     &num_parents,&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    return PyInt_FromLong(num_parents);
}

static PyObject *
iMeshEntSetObj_getChildren(iMeshEntitySet_Object *self,PyObject *args,
                           PyObject *kw)
{
    static char *kwlist[] = {"hops","out",0};
    int err;
    int hops=-1;

    iBase_OutArray sets = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"|iO&",kwlist,&hops,
                                    iBaseBuffer_Cvt,&sets))
        return NULL;

    iMesh_getChldn(self->instance->handle,self->base.handle,hops,
                   PASS_OUTARR_SET(sets),&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {sets.size};
    return PyArray_NewFromOutBase(1,dims,NPY_IBASEENTSET,&sets,
                                  (iBase_Object*)self->instance);
}

static PyObject *
iMeshEntSetObj_getParents(iMeshEntitySet_Object *self,PyObject *args,
                          PyObject *kw)
{
    static char *kwlist[] = {"hops","out",0};
    int err;
    int hops=-1;

    iBase_OutArray sets = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"|iO&",kwlist,&hops,
                                    iBaseBuffer_Cvt,&sets))
        return NULL;

    iMesh_getPrnts(self->instance->handle,self->base.handle,hops,
                   PASS_OUTARR_SET(sets),&err);
    if(checkError(self->instance->handle,err))
        return NULL;

    npy_intp dims[] = {sets.size};
    return PyArray_NewFromOutBase(1,dims,NPY_IBASEENTSET,&sets,
                                  (iBase_Object*)self->instance);
}

/* TODO: add/removeParent? */

static PyObject *
iMeshEntSetObj_addChild(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    int err;
    iBaseEntitySet_Object *set;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntitySet_Type,
                                    &set))
        return NULL;

    iMesh_addPrntChld(self->instance->handle,self->base.handle,set->handle,
                      &err);
    if(checkError(self->instance->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iMeshEntSetObj_removeChild(iMeshEntitySet_Object *self,PyObject *args,
                           PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    int err;
    iBaseEntitySet_Object *set;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBaseEntitySet_Type,
                                    &set))
        return NULL;

    iMesh_rmvPrntChld(self->instance->handle,self->base.handle,set->handle,
                      &err);
    if(checkError(self->instance->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iMeshEntSetObj_iterate(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    PyObject *first = PyTuple_Pack(1,self);
    PyObject *tuple = PyNumber_Add(first,args);
    PyObject *ret;

    Py_DECREF(first);
    ret = PyObject_Call((PyObject*)&iMeshIter_Type,tuple,kw);
    Py_DECREF(tuple);

    return ret;
}

static PyObject *
iMeshEntSetObj_iter(iMeshEntitySet_Object *self)
{
    PyObject *args;
    PyObject *ret;

    args = PyTuple_Pack(1,self);
    ret = PyObject_CallObject((PyObject*)&iMeshIter_Type,args);
    Py_DECREF(args);

    return ret;
}

static PyObject *
iMeshEntSetObj_sub(iMeshEntitySet_Object *lhs,iMeshEntitySet_Object *rhs)
{
    int err;
    iBase_EntitySetHandle result;

    if(lhs->instance->handle != rhs->instance->handle)
        return NULL;

    iMesh_subtract(lhs->instance->handle,lhs->base.handle,rhs->base.handle,
                   &result,&err);
    if(checkError(lhs->instance->handle,err))
        return NULL;

    return iMeshEntitySet_FromHandle(lhs->instance,result);
}

static PyObject *
iMeshEntSetObj_bitand(iMeshEntitySet_Object *lhs,iMeshEntitySet_Object *rhs)
{
    int err;
    iBase_EntitySetHandle result;

    if(lhs->instance->handle != rhs->instance->handle)
        return NULL;

    iMesh_intersect(lhs->instance->handle,lhs->base.handle,rhs->base.handle,
                    &result,&err);
    if(checkError(lhs->instance->handle,err))
        return NULL;

    return iMeshEntitySet_FromHandle(lhs->instance,result);
}

static PyObject *
iMeshEntSetObj_bitor(iMeshEntitySet_Object *lhs,iMeshEntitySet_Object *rhs)
{
    int err;
    iBase_EntitySetHandle result;

    if(lhs->instance->handle != rhs->instance->handle)
        return NULL;

    iMesh_unite(lhs->instance->handle,lhs->base.handle,rhs->base.handle,
                &result,&err);
    if(checkError(lhs->instance->handle,err))
    {
        Py_DECREF((PyObject*)result);
        return NULL;
    }

    return iMeshEntitySet_FromHandle(lhs->instance,result);
}


static PyObject *
iMeshEntSetObj_difference(iMeshEntitySet_Object *self,PyObject *args,
                          PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    iMeshEntitySet_Object *rhs;
    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iMeshEntitySet_Type,
                                    &rhs))
        return NULL;

    return iMeshEntSetObj_sub(self,rhs);
}

static PyObject *
iMeshEntSetObj_intersection(iMeshEntitySet_Object *self,PyObject *args,
                            PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    iMeshEntitySet_Object *rhs;
    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iMeshEntitySet_Type,
                                    &rhs))
        return NULL;

    return iMeshEntSetObj_bitand(self,rhs);
}

static PyObject *
iMeshEntSetObj_union(iMeshEntitySet_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"set",0};
    iMeshEntitySet_Object *rhs;
    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iMeshEntitySet_Type,
                                    &rhs))
        return NULL;

    return iMeshEntSetObj_bitor(self,rhs);
}

static PyObject *
iMeshEntSetObj_repr(iMeshEntitySet_Object *self)
{
    return PyString_FromFormat("<%s %p>",self->base.ob_type->tp_name,
                               self->base.handle);
}

static PyObject *
iMeshEntSetObj_richcompare(iMeshEntitySet_Object *lhs,
                           iMeshEntitySet_Object *rhs,int op)
{
    if(!iMeshEntitySet_Check(lhs) || !iMeshEntitySet_Check(rhs))
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
iMeshEntSetObj_hash(iMeshEntitySet_Object *self)
{
    return (long)self->base.handle;
}


static PyMethodDef iMeshEntSetObj_methods[] = {
    IMESH_METHOD(iMeshEntSet, load,             METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, save,             METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, getNumOfType,     METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, getNumOfTopo,     METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, getEntities,      METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, getAdjEntIndices, METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, getNumEntSets,    METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, getEntSets,       METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, add,              METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, remove,           METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, contains,         METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, isChild,          METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, getNumChildren,   METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, getNumParents,    METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, getChildren,      METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, getParents,       METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, addChild,         METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, removeChild,      METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, iterate,          METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, difference,       METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, intersection,     METH_VARARGS|METH_KEYWORDS),
    IMESH_METHOD(iMeshEntSet, union,            METH_VARARGS|METH_KEYWORDS),
    {0}
};

static PyMemberDef iMeshEntSetObj_members[] = {
    { "instance", T_OBJECT_EX, offsetof(iMeshEntitySet_Object, instance),
      READONLY, IMESHDOC_iMeshEntSet_instance },
    {0}
};

static PyGetSetDef iMeshEntSetObj_getset[] = {
    IMESH_GET(iMeshEntSet, isList),
    {0}
};

static PyNumberMethods iMeshEntSetObj_num = {
    0,                                        /* nb_add */
    (binaryfunc)iMeshEntSetObj_sub,           /* nb_subtract */
    0,                                        /* nb_multiply */
    0,                                        /* nb_divide */
    0,                                        /* nb_remainder */
    0,                                        /* nb_divmod */
    0,                                        /* nb_power */
    0,                                        /* nb_negative */
    0,                                        /* nb_positive */
    0,                                        /* nb_absolute */
    0,                                        /* nb_nonzero */
    0,                                        /* nb_invert */
    0,                                        /* nb_lshift */
    0,                                        /* nb_rshift */
    (binaryfunc)iMeshEntSetObj_bitand,        /* nb_and */
    0,                                        /* nb_xor */
    (binaryfunc)iMeshEntSetObj_bitor,         /* nb_or */
    0,                                        /* nb_coerce */
    0,                                        /* nb_int */
    0,                                        /* nb_long */
    0,                                        /* nb_float */
    0,                                        /* nb_oct */
    0,                                        /* nb_hex */
};

static PySequenceMethods iMeshEntSetObj_seq = {
    (lenfunc)iMeshEntSetObj_len,              /* sq_length */
    0,                                        /* sq_concat */
    0,                                        /* sq_repeat */
    0,                                        /* sq_item */
    0,                                        /* sq_slice */
    0,                                        /* sq_ass_item */
    0,                                        /* sq_ass_slice */
    (objobjproc)iMeshEntSetObj_in,            /* sq_contains */
    0,                                        /* sq_inplace_concat */
    0,                                        /* sq_inplace_repeat */
};

static PyTypeObject iMeshEntitySet_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iMesh.EntitySet",                  /* tp_name */
    sizeof(iMeshEntitySet_Object),            /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)iMeshEntSetObj_dealloc,       /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    (reprfunc)iMeshEntSetObj_repr,            /* tp_repr */
    &iMeshEntSetObj_num,                      /* tp_as_number */
    &iMeshEntSetObj_seq,                      /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    (hashfunc)iMeshEntSetObj_hash,            /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str */
    0,                                        /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    IMESHDOC_iMeshEntSet,                     /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    (richcmpfunc)iMeshEntSetObj_richcompare,  /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    (getiterfunc)iMeshEntSetObj_iter,         /* tp_iter */
    0,                                        /* tp_iternext */
    iMeshEntSetObj_methods,                   /* tp_methods */
    iMeshEntSetObj_members,                   /* tp_members */
    iMeshEntSetObj_getset,                    /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    iMeshEntSetObj_new,                       /* tp_new */
};
