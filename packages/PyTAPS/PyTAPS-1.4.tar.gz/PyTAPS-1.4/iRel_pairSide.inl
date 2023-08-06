#include "errors.h"
#include "iRel_Python.h"
#include "iBase_Python.h"
#include "structmember.h"

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
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return 0;
    }
    return 1;
}

static int
get_entityset_data(PyObject *obj,PyObject **array,iBase_EntitySetHandle **sets,
                   int *size)
{
    if((*array = PyArray_TryFromObject(obj,NPY_IBASEENTSET,1,1)) != NULL)
    {
        *sets = PyArray_DATA(*array);
        *size = PyArray_SIZE(*array);
    }
    else if(iBaseEntitySet_Check(obj))
    {
        *sets = &iBaseEntitySet_GET_HANDLE(obj);
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
iAnyEntitySet_FromHandle(iBase_Object *instance,iBase_EntitySetHandle handle)
{
    if(iMesh_Check(instance))
        return iMeshEntitySet_FromHandle((iMesh_Object*)instance,handle);
    if(iGeom_Check(instance))
        return iGeomEntitySet_FromHandle((iGeom_Object*)instance,handle);

    return NULL;
}

static void
iRelPairSideObj_dealloc(iRelPairSide_Object *self)
{
    Py_XDECREF(self->parent);

    ((PyObject*)self)->ob_type->tp_free((PyObject*)self);
}

static PyObject *
iRelPairSideObj_getinstance(iRelPairSide_Object *self,void *closure)
{
    return (PyObject*)self->parent->related[self->side];
}

static PyObject *
iRelPairSideObj_gettype(iRelPairSide_Object *self,void *closure)
{
    int err;
    iBase_Instance iface[2];
    int ent_or_set[2];
    int type[2];
    int status[2];

    iRel_getPairInfo(self->parent->instance->handle,self->parent->handle,
                     iface+0,ent_or_set+0,type+0,status+0,
                     iface+1,ent_or_set+1,type+1,status+1,&err);
    if(checkError(self->parent->instance->handle,err))
        return NULL;

    return PyInt_FromLong(ent_or_set[self->side]);
}

static PyObject *
iRelPairSideObj_getstatus(iRelPairSide_Object *self,void *closure)
{
    int err;
    iBase_Instance iface[2];
    int ent_or_set[2];
    int type[2];
    int status[2];

    iRel_getPairInfo(self->parent->instance->handle,self->parent->handle,
                     iface+0,ent_or_set+0,type+0,status+0,
                     iface+1,ent_or_set+1,type+1,status+1,&err);
    if(checkError(self->parent->instance->handle,err))
        return NULL;

    return PyInt_FromLong(status[self->side]);
}

static PyObject *
iRelPairSideObj_retrieve(iRelPairSide_Object *self,PyObject *in_ents,
                         iBase_OutArray *data)
{
    int err;
    PyObject *ents;

    iBase_Instance iface[2];
    int ent_or_set[2];
    int type[2];
    int status[2];

    iRel_getPairInfo(self->parent->instance->handle,self->parent->handle,
                     iface+0,ent_or_set+0,type+0,status+0,
                     iface+1,ent_or_set+1,type+1,status+1,&err);
    if(checkError(self->parent->instance->handle,err))
        return NULL;

    int return_type = ent_or_set[!self->side];
    iBase_Object *related = self->parent->related[!self->side];

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1);
    if(ents)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int ent_size = PyArray_SIZE(ents);

        if(return_type == iRel_ENTITY)
        {
            iRel_getEntArrEntArrRelation(self->parent->instance->handle,
                                         self->parent->handle,
                                         entities,ent_size,self->side,
                                         PASS_OUTARR(iBase_EntityHandle,*data),
                                         &err);
            Py_DECREF(ents);
            if(checkError(self->parent->instance->handle,err))
                return NULL;

            npy_intp dims[] = {ent_size};
            return PyArray_NewFromOut(1,dims,NPY_IBASEENT,data);
        }
        else
        {
            iRel_getEntArrSetArrRelation(self->parent->instance->handle,
                                         self->parent->handle,
                                         entities,ent_size,self->side,
                                         PASS_OUTARR(iBase_EntitySetHandle,
                                                     *data),&err);
            Py_DECREF(ents);
            if(checkError(self->parent->instance->handle,err))
                return NULL;

            npy_intp dims[] = {ent_size};
            return PyArray_NewFromOutBase(1,dims,NPY_IBASEENTSET,data,related);
        }
    }

    ents = PyArray_TryFromObject(in_ents,NPY_IBASEENTSET,1,1);
    if(ents)
    {
        iBase_EntitySetHandle *sets = PyArray_DATA(ents);
        int set_size = PyArray_SIZE(ents);

        if(return_type == iRel_ENTITY)
        {
            iRel_getSetArrEntArrRelation(self->parent->instance->handle,
                                         self->parent->handle,
                                         sets,set_size,self->side,
                                         PASS_OUTARR(iBase_EntityHandle,*data),
                                         &err);
            Py_DECREF(ents);
            if(checkError(self->parent->instance->handle,err))
                return NULL;

            npy_intp dims[] = {set_size};
            return PyArray_NewFromOut(1,dims,NPY_IBASEENT,data);
        }
        else
        {
            iRel_getSetArrSetArrRelation(self->parent->instance->handle,
                                         self->parent->handle,
                                         sets,set_size,self->side,
                                         PASS_OUTARR(iBase_EntitySetHandle,
                                                     *data),&err);
            Py_DECREF(ents);
            if(checkError(self->parent->instance->handle,err))
                return NULL;

            npy_intp dims[] = {set_size};
            return PyArray_NewFromOutBase(1,dims,NPY_IBASEENTSET,data,related);
        }
    }

    /* TODO: use iBase_OutArray here? */
    if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);

        if(return_type == iRel_ENTITY)
        {
            iBase_EntityHandle result;

            iRel_getEntEntRelation(self->parent->instance->handle,
                                   self->parent->handle,entity,self->side,
                                   &result,&err);
            if(checkError(self->parent->instance->handle,err))
                return NULL;
            return iBaseEntity_FromHandle(result);
        }
        else
        {
            iBase_EntitySetHandle result;

            iRel_getEntSetRelation(self->parent->instance->handle,
                                   self->parent->handle,entity,self->side,
                                   &result,&err);
            if(checkError(self->parent->instance->handle,err))
                return NULL;
            return iAnyEntitySet_FromHandle(related,result);
        }
    }

    if(iBaseEntitySet_Check(in_ents))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GET_HANDLE(in_ents);

        if(return_type == iRel_ENTITY)
        {
            iBase_EntityHandle result;

            iRel_getSetEntRelation(self->parent->instance->handle,
                                   self->parent->handle,set,self->side,
                                   &result,&err);
            if(checkError(self->parent->instance->handle,err))
                return NULL;
            return iBaseEntity_FromHandle(result);
        }
        else
        {
            iBase_EntitySetHandle result;

            iRel_getSetSetRelation(self->parent->instance->handle,
                                   self->parent->handle,set,self->side,
                                   &result,&err);
            if(checkError(self->parent->instance->handle,err))
                return NULL;
            return iAnyEntitySet_FromHandle(related,result);
        }
    }

    PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
    return NULL;
}

static int
iRelPairSideObj_assign(iRelPairSide_Object *self,PyObject *in_ents1,
                       PyObject *in_ents2)
{
    int err;
    PyObject *ents1 = NULL;
    PyObject *ents2 = NULL;

    iBase_EntityHandle *entities1 = NULL;
    iBase_EntityHandle *entities2 = NULL;
    iBase_EntitySetHandle *sets1  = NULL;
    iBase_EntitySetHandle *sets2  = NULL;
    int size1;
    int size2;

    /* If we're using the right side, swap the so in_ents1 is always the left
       side's entities. */
    if(self->side == 1)
    {
        PyObject *tmp;
        tmp = in_ents1; in_ents1 = in_ents2; in_ents2 = tmp;
    }

    if(!get_entity_data   (in_ents1,&ents1,&entities1,&size1) &&
       !get_entityset_data(in_ents1,&ents1,&sets1,    &size1))
        goto err;
    if(!get_entity_data   (in_ents2,&ents2,&entities2,&size2) &&
       !get_entityset_data(in_ents2,&ents2,&sets2,    &size2))
        goto err;

    if(ents1 || ents2)
    {
        if(entities1)
        {
            if(entities2)
                iRel_setEntArrEntArrRelation(self->parent->instance->handle,
                                             self->parent->handle,
                                             entities1,size1,
                                             entities2,size2,&err);
            else
                iRel_setEntArrSetArrRelation(self->parent->instance->handle,
                                             self->parent->handle,
                                             entities1,size1,
                                             sets2,size2,&err);
        }
        else
        {
            if(entities2)
                iRel_setSetArrEntArrRelation(self->parent->instance->handle,
                                             self->parent->handle,
                                             sets1,size1,
                                             entities2,size2,&err);
            else
                iRel_setSetArrSetArrRelation(self->parent->instance->handle,
                                             self->parent->handle,
                                             sets1,size1,
                                             sets2,size2,&err);
        }
    }
    else
    {
        if(entities1)
        {
            if(entities2)
                iRel_setEntEntRelation(self->parent->instance->handle,
                                       self->parent->handle,
                                       entities1[0],entities2[0],&err);
            else
                iRel_setEntSetRelation(self->parent->instance->handle,
                                       self->parent->handle,
                                       entities1[0],sets2[0],&err);
        }
        else
        {
            if(entities2)
                iRel_setSetEntRelation(self->parent->instance->handle,
                                       self->parent->handle,
                                       sets1[0],entities2[0],&err);
            else
                iRel_setSetSetRelation(self->parent->instance->handle,
                                       self->parent->handle,
                                       sets1[0],sets2[0],&err);
        }
    }

    Py_XDECREF(ents1);
    Py_XDECREF(ents2);
    if(checkError(self->parent->instance->handle,err))
        return -1;
    return 0;
err:
    Py_XDECREF(ents1);
    Py_XDECREF(ents2);
    return -1;
}

static int
iRelPairSideObj_del(iRelPairSide_Object *self,PyObject *in_ents)
{
    int err;
    PyObject *ents;

    if((ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1)))
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int ent_size = PyArray_SIZE(ents);

        iRel_rmvEntArrRelation(self->parent->instance->handle,
                               self->parent->handle,entities,ent_size,
                               self->side,&err);
        Py_DECREF(ents);
    }
    else if((ents = PyArray_TryFromObject(in_ents,NPY_IBASEENTSET,1,1)))
    {
        iBase_EntitySetHandle *sets = PyArray_DATA(ents);
        int set_size = PyArray_SIZE(ents);

        iRel_rmvSetArrRelation(self->parent->instance->handle,
                               self->parent->handle,sets,set_size,
                               self->side,&err);
        Py_DECREF(ents);
    }
    else if(iBaseEntitySet_Check(in_ents))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GET_HANDLE(in_ents);
        iRel_rmvSetRelation(self->parent->instance->handle,
                            self->parent->handle,set,self->side,&err);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);
        iRel_rmvEntRelation(self->parent->instance->handle,
                            self->parent->handle,entity,self->side,&err);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return -1;
    }

    if(checkError(self->parent->instance->handle,err))
        return -1;
    return 0;
}

static PyObject *
iRelPairSideObj_subscript(iRelPairSide_Object *self,PyObject *in_ents)
{
    iBase_OutArray data = {0};
    return iRelPairSideObj_retrieve(self,in_ents,&data);
}

static int
iRelPairSideObj_ass_subscript(iRelPairSide_Object *self,PyObject *in_ents1,
                              PyObject *in_ents2)
{
    if(in_ents2)
        return iRelPairSideObj_assign(self,in_ents1,in_ents2);
    else
        return iRelPairSideObj_del(self,in_ents1);
}

static PyObject *
iRelPairSideObj_get(iRelPairSide_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"entities","out",0};
    PyObject *in_ents;

    iBase_OutArray data = {0};

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O&",kwlist,&in_ents,
                                    iBaseBuffer_Cvt,&data))
        return NULL;

    return iRelPairSideObj_retrieve(self,in_ents,&data);
}

static PyObject *
iRelPairSideObj_inferRelations(iRelPairSide_Object *self,PyObject *args,
                               PyObject *kw)
{
    static char *kwlist[] = {"entities",0};
    int err;
    PyObject *in_ents,*ents;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO!",kwlist,&in_ents))
        return NULL;

    if((ents = PyArray_TryFromObject(in_ents,NPY_IBASEENT,1,1)) != NULL)
    {
        iBase_EntityHandle *entities = PyArray_DATA(ents);
        int ent_size = PyArray_SIZE(ents);

        iRel_inferEntArrRelations(self->parent->instance->handle,
                                  self->parent->handle,entities,ent_size,
                                  self->side,&err);
        Py_DECREF(ents);
    }
    else if((ents = PyArray_TryFromObject(in_ents,NPY_IBASEENTSET,1,1)) != NULL)
    {
        iBase_EntitySetHandle *sets = PyArray_DATA(ents);
        int set_size = PyArray_SIZE(ents);

        iRel_inferSetArrRelations(self->parent->instance->handle,
                                  self->parent->handle,sets,set_size,
                                  self->side,&err);
        Py_DECREF(ents);
    }
    else if(iBaseEntity_Check(in_ents))
    {
        iBase_EntityHandle entity = iBaseEntity_GET_HANDLE(in_ents);

        iRel_inferEntRelations(self->parent->instance->handle,
                               self->parent->handle,entity,self->side,&err);
    }
    else if(iBaseEntitySet_Check(in_ents))
    {
        iBase_EntitySetHandle set = iBaseEntitySet_GET_HANDLE(in_ents);

        iRel_inferSetRelations(self->parent->instance->handle,
                               self->parent->handle,set,self->side,&err);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError,ERR_ANY_ENT);
        return NULL;
    }

    if(checkError(self->parent->instance->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iRelPairSideObj_richcompare(iRelPairSide_Object *lhs,iRelPairSide_Object *rhs,
                            int op)
{
    if(!iRelPairSide_Check(lhs) || !iRelPairSide_Check(rhs))
    {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    switch(op)
    {
    case Py_EQ:
        return PyBool_FromLong(lhs->parent->handle == rhs->parent->handle &&
                               lhs->parent->instance->handle ==
                               rhs->parent->instance->handle &&
                               lhs->side == rhs->side);
    case Py_NE:
        return PyBool_FromLong(lhs->parent->handle != rhs->parent->handle ||
                               lhs->parent->instance->handle !=
                               rhs->parent->instance->handle ||
                               lhs->side != rhs->side);
    default:
        PyErr_SetNone(PyExc_TypeError);
        return NULL;
    }
}


static PyMethodDef iRelPairSideObj_methods[] = {
    IREL_METHOD(iRelPairSide, get,            METH_VARARGS|METH_KEYWORDS),
    IREL_METHOD(iRelPairSide, inferRelations, METH_VARARGS|METH_KEYWORDS),
    {0}
};

static PyGetSetDef iRelPairSideObj_getset[] = {
    IREL_GET(iRelPairSide, instance),
    IREL_GET(iRelPairSide, type),
    IREL_GET(iRelPairSide, status),
    {0}
};

static PyMappingMethods iRelPairSideObj_map = {
    0,                                            /* mp_length */
    (binaryfunc)iRelPairSideObj_subscript,        /* mp_subscript */
    (objobjargproc)iRelPairSideObj_ass_subscript, /* mp_ass_subscript */
};

static PyTypeObject iRelPairSide_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iRel.PairSide",                    /* tp_name */
    sizeof(iRelPairSide_Object),              /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)iRelPairSideObj_dealloc,      /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    0,                                        /* tp_repr */
    0,                                        /* tp_as_number */
    0,                                        /* tp_as_sequence */
    &iRelPairSideObj_map,                     /* tp_as_mapping */
    0,                                        /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str */
    0,                                        /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    IRELDOC_iRelPairSide,                     /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    (richcmpfunc)iRelPairSideObj_richcompare, /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    iRelPairSideObj_methods,                  /* tp_methods */
    0,                                        /* tp_members */
    iRelPairSideObj_getset,                   /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    0,                                        /* tp_new */
};
