#define _IREL_MODULE
#include "iRel_Python.h"
#include "iRel_doc.h"
#include "errors.h"
#include "common.h"
#include "helpers.h"
#include "numpy_extensions.h"

#include "iMesh_Python.h"
#include "iGeom_Python.h"

static PyTypeObject iRel_Type;
static PyTypeObject iRelPair_Type;
static PyTypeObject iRelPairSide_Type;

/* automatic method/property declarators */
#define IREL_METHOD(cls, name, type)                     \
    { #name, (PyCFunction)(cls ## Obj_ ## name), (type), \
      IRELDOC_ ## cls ## _ ## name }

#define IREL_GET(cls, name)                       \
    { #name, (getter)(cls ## Obj_get ## name), 0, \
      IRELDOC_ ## cls ## _ ## name, 0 }

#define IREL_GETSET(cls, name)                 \
    { #name, (getter)(cls ## Obj_get ## name), \
             (setter)(cls ## Obj_set ## name), \
      IRELDOC_ ## cls ## _ ## name, 0 }


static int
checkError(iRel_Instance rel,int err)
{
    if(err)
    {
        char descr[120];
        iRel_getDescription(rel,descr,sizeof(descr)-1);
        PyErr_SetString(PyExc_Errors[err-1],descr);
        return 1;
    }
    else
        return 0;
}

static int
iRelType_Cvt(PyObject *object,int *val)
{
    int tmp = PyInt_AsLong(object);
    if(PyErr_Occurred())
        return 0;
    if(tmp < iRel_RelationType_MIN || tmp > iRel_RelationType_MAX)
    {
        PyErr_SetString(PyExc_ValueError,ERR_INVALID_RELTYPE);
        return 0;
    }

    *val = tmp;
    return 1;
}

static int
iRelStatus_Cvt(PyObject *object,int *val)
{
    int tmp = PyInt_AsLong(object);
    if(PyErr_Occurred())
        return 0;
    if(tmp < iRel_RelationStatus_MIN || tmp > iRel_RelationStatus_MAX)
    {
        PyErr_SetString(PyExc_ValueError,ERR_INVALID_RELSTATUS);
        return 0;
    }

    *val = tmp;
    return 1;
}

static int
get_iface_type(iBase_Object *o)
{
    if(iMesh_Check(o))
        return iRel_IMESH_IFACE;
    if(iGeom_Check(o))
        return iRel_IGEOM_IFACE;
    if(iRel_Check(o))
        return iRel_IREL_IFACE;

    return -1;
}

static PyObject *
iBase_FromInstance(iBase_Instance instance,int type)
{
    switch(type)
    {
    case iRel_IMESH_IFACE:
        return iMesh_FromInstance(instance);
    case iRel_IGEOM_IFACE:
        return iGeom_FromInstance(instance);
    case iRel_IREL_IFACE:
    default:
        return 0;
    }
}

static iRelPair_Object *
iRelPair_FromInstance(iRel_Object *instance)
{
    iRelPair_Object *o = iRelPair_New();
    if(o == NULL)
        return NULL;

    o->instance = instance;
    o->handle = NULL;
    Py_INCREF(o->instance);

    o->sides[0] = NULL;
    o->sides[1] = NULL;

    int i;
    for(i=0; i<2; i++)
    {
        o->sides[i] = iRelPairSide_New();
        if(o == NULL)
            goto err;
        o->sides[i]->parent = o;
        o->sides[i]->side = i;
        Py_INCREF(o);
    }

    return o;
err:
    Py_XDECREF(o->sides[0]);
    Py_XDECREF(o->sides[1]);
    Py_DECREF(o);
    return NULL;
}

static PyObject *
iRel_FromInstance(iRel_Instance instance)
{
    iRel_Object *o = PyObject_AllocNew(iRel_Object,&iRel_Type);
    if(o == NULL)
        return NULL;

    o->handle = instance;
    o->owned = 0;
    return (PyObject*)o;
}

static int
iRelObj_init(iRel_Object *self,PyObject *args,PyObject *kw)
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
        iRel_destroy(self->handle,&err);
        if(checkError(self->handle,err))
            return -1;
    }
    iRel_create(options,&self->handle,&err,strlen(options));
    if(checkError(self->handle,err))
        return -1;
    self->owned = 1;
    return 0;
}

static void
iRelObj_dealloc(iRel_Object *self)
{
    if(self->handle && self->owned)
    {
        int err;
        iRel_destroy(self->handle,&err);
    }
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
iRelObj_createPair(iRel_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist1[] = {"left", "left_type",
                              "right","right_type",0};
    static char *kwlist2[] = {"left", "left_type", "left_status",
                              "right","right_type","right_status",0};

    int err;
    iBase_Object *iface1;
    int ent_or_set1;
    int status1 = iRel_ACTIVE;
    iBase_Object *iface2;
    int ent_or_set2;
    int status2 = iRel_ACTIVE;

    int type1,type2;

    /* first, try the brief signature (no status args) */
    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!O&O!O&",kwlist1,
                                    &iBase_Type, &iface1,
                                    iRelType_Cvt,&ent_or_set1,
                                    &iBase_Type, &iface2,
                                    iRelType_Cvt,&ent_or_set2)) {
        PyErr_Clear();
        /* now, try the full signature (with status args) */
        if(!PyArg_ParseTupleAndKeywords(args,kw,"O!O&O&O!O&O&",kwlist2,
                                        &iBase_Type, &iface1,
                                        iRelType_Cvt,&ent_or_set1,
                                        iRelStatus_Cvt,&status1,
                                        &iBase_Type, &iface2,
                                        iRelType_Cvt,&ent_or_set2,
                                        iRelStatus_Cvt,&status2))
            return NULL;
    }

    type1 = get_iface_type(iface1);
    type2 = get_iface_type(iface2);
    if(type1 == -1 || type2 == -1)
    {
        PyErr_SetString(PyExc_ValueError,ERR_UNKNOWN_INST);
        return NULL;
    }

    iRelPair_Object *pair = iRelPair_FromInstance(self);

    iRel_createPair(self->handle,
                    iface1->handle,ent_or_set1,type1,status1,
                    iface2->handle,ent_or_set2,type2,status2,
                    &pair->handle,&err);
    if(checkError(self->handle,err))
        return NULL;

    pair->related[0] = iface1;
    pair->related[1] = iface2;
    Py_INCREF(iface1);
    Py_INCREF(iface2);

    return (PyObject*)pair;
}

static PyObject *
iRelObj_destroyPair(iRel_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"pair",0};
    int err;
    iRelPair_Object *pair;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iRelPair_Type,
                                    &pair))
        return NULL;

    iRel_destroyPair(self->handle,pair->handle,&err);
    if(checkError(self->handle,err))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *
iRelObj_findPairs(iRel_Object *self,PyObject *args,PyObject *kw)
{
    static char *kwlist[] = {"interface",0};
    int err;
    iBase_Object *iface;

    if(!PyArg_ParseTupleAndKeywords(args,kw,"O!",kwlist,&iBase_Type,&iface))
        return NULL;

    iRel_PairHandle *pairs=NULL;
    int pairs_alloc=0,pairs_size;

    iRel_findPairs(self->handle,iface->handle,&pairs,&pairs_alloc,&pairs_size,
                   &err);
    if(checkError(self->handle,err))
        return NULL;

    PyObject *result = PyList_New(pairs_size);
    if(!result)
        goto err;

    int i;
    for(i=0; i<pairs_size; i++)
    {
        iRelPair_Object *pair = iRelPair_FromInstance(self);
        iBase_Instance iface[2];
        int ent_or_set[2];
        int type[2];
        int status[2];

        pair->handle = pairs[i];
        iRel_getPairInfo(self->handle,pairs[i],
                         iface+0,ent_or_set+0,type+0,status+0,
                         iface+1,ent_or_set+1,type+1,status+1,&err);

        pair->related[0] = (iBase_Object*)iBase_FromInstance(iface[0],type[0]);
        pair->related[1] = (iBase_Object*)iBase_FromInstance(iface[0],type[1]);

        if(pair->related[0] && pair->related[1])
          PyList_SET_ITEM(result,i,(PyObject*)pair);
        else
            goto err;
    }

    free(pairs);
    return result;
err:
    free(pairs);
    Py_XDECREF(result);
    return NULL;
}

static PyObject *
iRelObj_repr(iRel_Object *self)
{
    return PyString_FromFormat("<%s %p>",self->ob_type->tp_name,self->handle);
}

static PyObject *
iRelObj_richcompare(iRel_Object *lhs,iRel_Object *rhs,int op)
{
    if(!iRel_Check(lhs) || !iRel_Check(rhs))
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

static PyMethodDef iRelObj_methods[] = {
    IREL_METHOD(iRel, createPair,  METH_VARARGS|METH_KEYWORDS),
    IREL_METHOD(iRel, destroyPair, METH_VARARGS|METH_KEYWORDS),
    IREL_METHOD(iRel, findPairs,   METH_VARARGS|METH_KEYWORDS),
    {0}
};

static PyTypeObject iRel_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "itaps.iRel.Rel",                         /* tp_name */
    sizeof(iRel_Object),                      /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)iRelObj_dealloc,              /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    (reprfunc)iRelObj_repr,                   /* tp_repr */
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
    IRELDOC_iRel,                             /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    (richcmpfunc)iRelObj_richcompare,         /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    iRelObj_methods,                          /* tp_methods */
    0,                                        /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)iRelObj_init,                   /* tp_init */
    0,                                        /* tp_alloc */
    0,                                        /* tp_new */
};


static PyMethodDef module_methods[] = {
    {0}
};

ENUM_TYPE(iRelType,"iRel.Type","");
ENUM_TYPE(iRelStatus,"iRel.Status","");

PyMODINIT_FUNC initiRel(void)
{
    PyObject *m;

    m = Py_InitModule("iRel",module_methods);
    import_array();
    import_iBase();
    import_iMesh();
    import_iGeom();
    import_helpers();

    /***** register C API *****/
    static void *IRel_API[] = {
         &iRel_Type,
         &iRelPair_Type,
         &iRelPairSide_Type,
         &iRel_FromInstance,
    };
    PyObject *api_obj;

    /* Create a CObject containing the API pointer array's address */
    api_obj = PyCObject_FromVoidPtr(IRel_API,NULL);

    if(api_obj != NULL)
        PyModule_AddObject(m, "_C_API", api_obj);

    REGISTER_CLASS(m,"Rel",      iRel);
    REGISTER_CLASS(m,"Pair",     iRelPair);
    REGISTER_CLASS(m,"PairSide", iRelPairSide);

    /***** initialize relation type enum *****/
    REGISTER_CLASS(m,"Type",iRelType);

    ADD_ENUM(iRelType,"entity", iRel_ENTITY);
    ADD_ENUM(iRelType,"set",    iRel_SET);
    ADD_ENUM(iRelType,"both",   iRel_BOTH);

    /***** initialize relation status enum *****/
    REGISTER_CLASS(m,"Status",iRelStatus);

    ADD_ENUM(iRelStatus,"active",    iRel_ACTIVE);
    ADD_ENUM(iRelStatus,"inactive",  iRel_INACTIVE);
    ADD_ENUM(iRelStatus,"not_exist", iRel_NOTEXIST);
}

/* Include source files so that everything is in one translation unit */
#include "iRel_pairSide.inl"
#include "iRel_pair.inl"
