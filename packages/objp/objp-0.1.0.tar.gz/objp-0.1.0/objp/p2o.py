import re
import os.path as op
from .base import tmpl_replace, TYPE_SPECS_REVERSED, copy_objp_unit

TEMPLATE_UNIT = """
#define PY_SSIZE_T_CLEAN
#import <Python.h>
#import "structmember.h"
#import "ObjP.h"

%%objcinterface%%

typedef struct {
    PyObject_HEAD
    %%clsname%% *objc_ref;
} %%clsname%%_Struct;

static PyTypeObject %%clsname%%_Type; /* Forward declaration */

/* Methods */

static void
%%clsname%%_dealloc(%%clsname%%_Struct *self)
{
    [self->objc_ref release];
    Py_TYPE(self)->tp_free((PyObject *)self);
}

%%initfunc%%

%%methods%%

static PyMethodDef %%clsname%%_methods[] = {
 %%methodsdef%%
{NULL}  /* Sentinel */
};

static PyTypeObject %%clsname%%_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "%%modulename%%.%%clsname%%", /*tp_name*/
    sizeof(%%clsname%%_Struct), /*tp_basicsize*/
    0, /*tp_itemsize*/
    (destructor)%%clsname%%_dealloc, /*tp_dealloc*/
    0, /*tp_print*/
    0, /*tp_getattr*/
    0, /*tp_setattr*/
    0, /*tp_reserved*/
    0, /*tp_repr*/
    0, /*tp_as_number*/
    0, /*tp_as_sequence*/
    0, /*tp_as_mapping*/
    0, /*tp_hash */
    0, /*tp_call*/
    0, /*tp_str*/
    0, /*tp_getattro*/
    0, /*tp_setattro*/
    0, /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "%%clsname%% object", /* tp_doc */
    0, /* tp_traverse */
    0, /* tp_clear */
    0, /* tp_richcompare */
    0, /* tp_weaklistoffset */
    0, /* tp_iter */
    0, /* tp_iternext */
    %%clsname%%_methods,/* tp_methods */
    0, /* tp_members */
    0, /* tp_getset */
    0, /* tp_base */
    0, /* tp_dict */
    0, /* tp_descr_get */
    0, /* tp_descr_set */
    0, /* tp_dictoffset */
    (initproc)%%clsname%%_init,      /* tp_init */
    0, /* tp_alloc */
    0, /* tp_new */
    0, /* tp_free */
    0, /* tp_is_gcc */
    0, /* tp_bases */
    0, /* tp_mro */
    0, /* tp_cache */
    0, /* tp_subclasses */
    0  /* tp_weaklist */
};

static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

static struct PyModuleDef %%modulename%%Def = {
    PyModuleDef_HEAD_INIT,
    "%%modulename%%",
    NULL,
    -1,
    module_methods,
    NULL,
    NULL,
    NULL,
    NULL
};

PyObject *
PyInit_%%modulename%%(void)
{
    PyObject *m;
    
    %%clsname%%_Type.tp_new = PyType_GenericNew;
    if (PyType_Ready(&%%clsname%%_Type) < 0) {
        return NULL;
    }
    
    m = PyModule_Create(&%%modulename%%Def);
    if (m == NULL) {
        return NULL;
    }
    
    Py_INCREF(&%%clsname%%_Type);
    PyModule_AddObject(m, "%%clsname%%", (PyObject *)&%%clsname%%_Type);
    return m;
}

"""

TEMPLATE_INITFUNC_CREATE = """
static int
%%clsname%%_init(%%clsname%%_Struct *self, PyObject *args, PyObject *kwds)
{
    if (!PyArg_ParseTuple(args, "")) {
        return -1;
    }
    
    self->objc_ref = [[%%clsname%% alloc] init];
    
    return 0;
}
"""

TEMPLATE_METHOD_NOARGS = """
static PyObject *
%%clsname%%_%%methname%%(%%clsname%%_Struct *self)
{
    %%retvalassign%%[self->objc_ref %%methname%%];
    %%retvalreturn%%
}
"""

TEMPLATE_METHOD_VARARGS = """
static PyObject *
%%clsname%%_%%methname%%(%%clsname%%_Struct *self, PyObject *args)
{
    PyObject %%argliststar%%;
    if (!PyArg_ParseTuple(args, "%%argfmt%%", %%arglistamp%%)) {
        return NULL;
    }
    %%conversion%%
    
    %%retvalassign%%[self->objc_ref %%methcall%%];
    %%retvalreturn%%
}
"""

TEMPLATE_METHODDEF = """
{"%%methname%%", (PyCFunction)%%clsname%%_%%methname%%, %%methtype%%, ""},
"""

def parse_objc_header(header):
    # returns (clsname, [(methodname, resulttype, [(argname, argtype)])])
    re_class = re.compile(r"@interface\s+(\w*?)\s*:\s*\w*?.*?{.*?}(.*?)@end", re.MULTILINE | re.DOTALL)
    match = re_class.search(header)
    assert match is not None
    clsname, methods = match.groups()
    re_method = re.compile(r"-\s*\(\s*([\w *]+?)\s*\)(.+?);")
    methods = re_method.findall(methods)
    method_specs = []
    re_method_elems = re.compile(r"(\w+)\s*:\s*\(\s*(\w+?\s*\*?)\s*\)\s*(\w+)")
    for resulttype, rest in methods:
        elems = re_method_elems.findall(rest)
        if not elems: # no arguments
            name = rest
            args = []
        else:
            name = ':'.join(elem[0] for elem in elems)
            if not name.endswith(':'):
                name += ':'
            args = [(elem[2], elem[1]) for elem in elems]
        method_specs.append((name, resulttype, args))
    return (clsname, method_specs)

def generate_python_proxy_code(header_path, destpath):
    # The name of the file in destpath will determine the name of the module. For example,
    # "foo/bar.m" will result in a module name "bar".
    with open(header_path, 'rt') as fp:
        header = fp.read()
    clsname, method_specs = parse_objc_header(header)
    tmpl_initfunc = tmpl_replace(TEMPLATE_INITFUNC_CREATE, clsname=clsname)
    tmpl_methods = []
    tmpl_methodsdef = []
    for methodname, resulttype, args in method_specs:
        tmplval = {}
        tmplval['methname'] = methodname.replace(':', '_')
        if resulttype == 'void':
            tmplval['retvalassign'] = ''
            tmplval['retvalreturn'] = 'Py_RETURN_NONE;'
        else:
            ts = TYPE_SPECS_REVERSED[resulttype]
            tmplval['retvalassign'] = '%s retval = ' % ts.objctype
            fmt = 'PyObject *pResult = %s; return pResult;'
            tmplval['retvalreturn'] = fmt % (ts.o2p_code % 'retval')
        if args:
            tmplval['methtype'] = 'METH_VARARGS'
            tmplval['argliststar'] = ', '.join('*p'+name for name, _ in args)
            tmplval['arglistamp'] = ', '.join('&p'+name for name, _ in args)
            tmplval['argfmt'] = 'O' * len(args)
            conversion = []
            for name, type in args:
                ts = TYPE_SPECS_REVERSED[type]
                conversion.append('%s %s = %s;' % (type, name, ts.p2o_code % ('p'+name)))
            tmplval['conversion'] = '\n'.join(conversion)
            elems = methodname.split(':')
            elems_and_args = [elem + ':' + argname for elem, (argname, _) in zip(elems, args)]
            tmplval['methcall'] = ' '.join(elems_and_args)
            tmpl_methods.append(tmpl_replace(TEMPLATE_METHOD_VARARGS, clsname=clsname, **tmplval))
        else:
            tmplval['methtype'] = 'METH_NOARGS'
            tmpl_methods.append(tmpl_replace(TEMPLATE_METHOD_NOARGS, clsname=clsname, **tmplval))
        tmpl_methodsdef.append(tmpl_replace(TEMPLATE_METHODDEF, clsname=clsname, **tmplval))
    tmpl_methods = ''.join(tmpl_methods)
    tmpl_methodsdef = ''.join(tmpl_methodsdef)
    modulename = op.splitext(op.basename(destpath))[0]
    result = tmpl_replace(TEMPLATE_UNIT, clsname=clsname, modulename=modulename,
        objcinterface=header, initfunc=tmpl_initfunc, methods=tmpl_methods,
        methodsdef=tmpl_methodsdef)
    copy_objp_unit(op.dirname(destpath))
    with open(destpath, 'wt') as fp:
        fp.write(result)
    
