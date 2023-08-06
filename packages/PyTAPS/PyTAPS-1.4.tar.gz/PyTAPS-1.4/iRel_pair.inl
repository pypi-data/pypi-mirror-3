#include "errors.h"
#include "iRel_Python.h"
#include "iBase_Python.h"
#include "structmember.h"

static void
iRelPairObj_dealloc(iRelPair_Object *self)
{
    Py_XDECREF(self->instance);
    Py_XDECREF(self->related[0]);
    Py_XDECREF(self->related[1]);
    Py_XDECREF(self->sides[0]);
    Py_XDECREF(self->sides[1]);

    ((PyObject*)self)->ob_type->tp_free((PyObject*)self);
}

static PyObject *
iRelPairObj_repr(iRelPair_Object *self)
{
    return PyString_FromFormat("<%s '%s<->%s' %p>",
                               self->ob_type->tp_name,
                               self->related[0]->ob_type->tp_name,
                               self->related[1]->ob_type->tp_name,
                               self->handle);
}

static PyObject *
iRelPairObj_changeType(iRelPair_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"left","right",0};
    int err;
    int ent_or_set1;
    int ent_or_set2;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO",kwlist,
                                    iRelType_Cvt,&ent_or_set1,
                                    iRelType_Cvt,&ent_or_set2))
        return NULL;

    iRel_changePairType(self->instance->handle,self->handle,ent_or_set1,
                        ent_or_set2,&err);
    if(checkError(self->instance->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iRelPairObj_changeStatus(iRelPair_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"left","right",0};
    int err;
    int status1;
    int status2;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO",kwlist,
                                    iRelStatus_Cvt,&status1,
                                    iRelStatus_Cvt,&status2))
        return NULL;

    iRel_changePairStatus(self->instance->handle,self->handle,status1,status2,
                          &err);
    if(checkError(self->instance->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iRelPairObj_relate(iRelPair_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"left","right",0};
    PyObject *in_ents1;
    PyObject *in_ents2;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"OO",kwlist,&in_ents1,&in_ents2))
        return NULL;

    if(iRelPairSideObj_assign(self->sides[0],in_ents1,in_ents2) == 0)
        Py_RETURN_NONE;
    else
        return NULL;
}

static PyObject *
iRelPairObj_inferAllRelations(iRelPair_Object *self)
{
    int err;
    iRel_inferAllRelations(self->instance->handle,self->handle,&err);
    if(checkError(self->instance->handle,err))
        return NULL;
    Py_RETURN_NONE;
}

static PyObject *
iRelPairObj_richcompare(iRelPair_Object *lhs,iRelPair_Object *rhs,int op)
{
    if(!iRelPair_Check(lhs) || !iRelPair_Check(rhs))
    {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    switch(op)
    {
    case Py_EQ:
        return PyBool_FromLong(lhs->handle == rhs->handle &&
                               lhs->instance->handle == rhs->instance->handle);
    case Py_NE:
        return PyBool_FromLong(lhs->handle != rhs->handle ||
                               lhs->instance->handle != rhs->instance->handle);
    default:
        PyErr_SetNone(PyExc_TypeError);
        return NULL;
    }
}


static PyMethodDef iRelPairObj_methods[] = {
    IREL_METHOD(iRelPair, changeType,        METH_VARARGS|METH_KEYWORDS),
    IREL_METHOD(iRelPair, changeStatus,      METH_VARARGS|METH_KEYWORDS),
    IREL_METHOD(iRelPair, relate,            METH_VARARGS|METH_KEYWORDS),
    IREL_METHOD(iRelPair, inferAllRelations, METH_NOARGS),
    {0}
};

static PyMemberDef iRelPairObj_members[] = {
    {"instance", T_OBJECT_EX, offsetof(iRelPair_Object, instance),
     READONLY, IRELDOC_iRelPair_instance},
    {"left", T_OBJECT_EX, offsetof(iRelPair_Object, sides[0]),
     READONLY, IRELDOC_iRelPair_left},
    {"right", T_OBJECT_EX, offsetof(iRelPair_Object, sides[1]),
     READONLY, IRELDOC_iRelPair_right},
    {0}
};

static PyTypeObject iRelPair_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iRel.Pair",                        /* tp_name */
    sizeof(iRelPair_Object),                  /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)iRelPairObj_dealloc,          /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    (reprfunc)iRelPairObj_repr,               /* tp_repr */
    0,                                        /* tp_as_number */
    0,                                        /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    0,                                        /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str */
    0,                                        /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    IRELDOC_iRelPair,                         /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    (richcmpfunc)iRelPairObj_richcompare,     /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    iRelPairObj_methods,                      /* tp_methods */
    iRelPairObj_members,                      /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    0,                                        /* tp_new */
};
