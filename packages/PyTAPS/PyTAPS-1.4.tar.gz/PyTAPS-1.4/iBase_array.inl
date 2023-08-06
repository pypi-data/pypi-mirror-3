#include "iBase_Python.h"
#include "structmember.h"
#include "numpy_extensions.h"

static PyObject *
PyArray_NewFromOutBase(int nd,npy_intp *dims,int typenum,iBase_OutArray *out,
                       iBase_Object *instance)
{
    iBaseArr_Object *arr = (iBaseArr_Object*)PyArray_NewFromOutSub(
        &iBaseArr_Type,nd,dims,typenum,out);
    Py_INCREF(instance);

    arr->instance = (PyObject*)instance;
    arr->funcs = get_sub_array(typenum,PyObject_Type((PyObject*)instance));
    return (PyObject*)arr;
}

static int
check_instance(iBaseArr_Object *arr,PyObject *o)
{
    PyObject *tmp = PyObject_GetAttrString(o,"instance");
    Py_XDECREF(tmp);
    PyErr_Clear();

    if(tmp == NULL)
        return 1;
    else if(arr->instance == NULL)
    {
        arr->instance = tmp;
        return 1;
    }
    else if(PyObject_RichCompare(arr->instance,tmp,Py_EQ))
        return 1;

    PyErr_SetString(PyExc_ValueError,ERR_ARR_INSTANCE);
    return 0;
}

static PyObject *
iBaseArrObj_new(PyTypeObject *cls,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"object","instance",0};

    PyObject *obj;
    PyObject *arr = NULL;
    PyObject *instance = NULL;
    iBaseArr_Object *self;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O|O!",kwlist,&obj,
                                    &iBase_Type,&instance))
        return NULL;

    arr = PyArray_FROM_O(obj);
    if(arr == NULL)
        return NULL;

    self = (iBaseArr_Object*)PyObject_CallMethod(arr,"view","O",cls);
    Py_DECREF(arr);
    if(self == NULL)
        return NULL;

    self->instance = instance;
    if(PySequence_Check(obj))
    {
        ssize_t i;
        for(i=0; i<PySequence_Size(obj); i++)
        {
            PyObject *o = PySequence_GetItem(obj,i);
            int good = check_instance(self,o);
            Py_DECREF(o);
            if(!good)
                goto err;
        }
    }
    else if(!check_instance(self,obj))
        goto err;

    if(self->instance == NULL)
    {
        PyErr_SetString(PyExc_ValueError,ERR_EXP_INSTANCE);
        goto err;
    }

    self->funcs = get_sub_array(PyArray_TYPE(self),
                                PyObject_Type(self->instance));
    Py_INCREF(self->instance);
    return (PyObject*)self;
err:
    Py_XDECREF((PyObject*)self);
    return NULL;
}

static void
iBaseArrObj_dealloc(iBaseArr_Object *self)
{
    Py_XDECREF(self->instance);
    self->array.ob_type->tp_free((PyObject*)self);
}

static PyObject*
iBaseArrObj_finalize(iBaseArr_Object *self,PyObject *args)
{
    iBaseArr_Object *context;
    if(PyArg_ParseTuple(args,"O!",&iBaseArr_Type,&context))
    {
        self->instance = context->instance;
        self->funcs = context->funcs;
        Py_XINCREF(self->instance);
    }
    PyErr_Clear();
    Py_RETURN_NONE;
}

static PyObject *
iBaseArr_TryNew(PyObject *list,iBase_Object *instance)
{
    PyObject *args = PyTuple_Pack((instance != NULL) ? 2:1,list,instance);
    PyObject *res = iBaseArrObj_new(&iBaseArr_Type,args,NULL);
    Py_DECREF(args);
    PyErr_Clear();
    return res;
}

static PyObject *
iBaseArrObj_richcompare(PyObject *lhs_in,PyObject *rhs_in,int op)
{
    PyObject *rhs_tmp = NULL;
    PyObject *lhs_tmp = NULL;
    PyObject *lhs;
    PyObject *rhs;
    PyObject *lhs_arr;
    PyObject *rhs_arr;

    PyObject *ret;

    if(op != Py_EQ && op != Py_NE)
    {
        PyErr_SetNone(PyExc_TypeError);
        return NULL;
    }

    if(!iBaseArr_Check(lhs_in) && (lhs_tmp = iBaseArr_TryNew(lhs_in,NULL)))
        lhs = lhs_tmp;
    else
        lhs = lhs_in;

    if(!iBaseArr_Check(rhs_in) && (rhs_tmp = iBaseArr_TryNew(rhs_in,NULL)))
        rhs = rhs_tmp;
    else
        rhs = rhs_in;

    if(iBaseArr_Check(lhs) && iBaseArr_Check(rhs))
    {
        int a = PyObject_RichCompareBool(iBaseArr_GET_INSTANCE(lhs),
                                         iBaseArr_GET_INSTANCE(rhs),op);
        if((op == Py_EQ && !a) || (op == Py_NE && a))
            return PyBool_FromLong(a);
    }

    lhs_arr = PyArray_FromAny(lhs,NULL,0,0,NPY_ENSUREARRAY,NULL);
    rhs_arr = PyArray_FromAny(rhs,NULL,0,0,NPY_ENSUREARRAY,NULL);
    ret = PyObject_RichCompare(lhs_arr,rhs_arr,op);

    Py_DECREF(lhs_arr);
    Py_DECREF(rhs_arr);
    Py_XDECREF(lhs_tmp);
    Py_XDECREF(rhs_tmp);

    return ret;
}

static int
iBaseArrObj_in(iBaseArr_Object *self,PyObject *el)
{
    if(self->funcs && PyObject_TypeCheck(el,self->funcs->el_type) && 
       !PyObject_RichCompare(self->instance,self->funcs->getter(el),Py_EQ))
       return 0;

    return PySequence_Contains(PyArray_EnsureArray((PyObject*)self),el);
}

static PyMethodDef iBaseArrObj_methods[] = {
    { "__array_finalize__", (PyCFunction)iBaseArrObj_finalize, METH_VARARGS,
      "" },
    {0}
};

static PyMemberDef iBaseArrObj_members[] = {
    { "instance", T_OBJECT_EX, offsetof(iBaseArr_Object, instance),
      READONLY, "base iBase instance" },
    {0}
};

static PySequenceMethods iBaseArrObj_seq = {
    0,                                        /* sq_length */
    0,                                        /* sq_concat */
    0,                                        /* sq_repeat */
    0,                                        /* sq_item */
    0,                                        /* sq_slice */
    0,                                        /* sq_ass_item */
    0,                                        /* sq_ass_slice */
    (objobjproc)iBaseArrObj_in,               /* sq_contains */
    0,                                        /* sq_inplace_concat */
    0,                                        /* sq_inplace_repeat */
};

static PyTypeObject iBaseArr_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iBase.Array",                      /* tp_name */
    sizeof(iBaseArr_Object),                  /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)iBaseArrObj_dealloc,          /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    0,                                        /* tp_repr */
    0,                                        /* tp_as_number */
    &iBaseArrObj_seq,                         /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    0,                                        /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str */
    0,                                        /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    "iBase array objects",                    /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    (richcmpfunc)iBaseArrObj_richcompare,     /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    iBaseArrObj_methods,                      /* tp_methods */
    iBaseArrObj_members,                      /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    0,                                        /* tp_init */
    0,                                        /* tp_alloc */
    iBaseArrObj_new,                          /* tp_new */
};
