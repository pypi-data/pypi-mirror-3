import os.path as op
import inspect

from .base import PYTYPE2SPEC, tmpl_replace, copy_objp_unit, ArgSpec, MethodSpec, ClassSpec

TEMPLATE_HEADER = """
#import "ObjP.h"

@interface %%classname%%:OPProxy {}
%%methods%%
@end
"""

TEMPLATE_UNIT = """
#import "%%classname%%.h"

@implementation %%classname%%
- (id)init
{
    self = [super initwithClassName:@"%%classname%%"];
    return self;
}

%%methods%%
@end
"""

TEMPLATE_METHOD = """
- %%signature%%
{
    PyObject *pResult, *pMethodName;
    pMethodName = PyUnicode_FromString("%%pyname%%");
    pResult = PyObject_CallMethodObjArgs(py, pMethodName, %%args%%, NULL);
    Py_DECREF(pMethodName);
    %%returncode%%
}
"""

TEMPLATE_RETURN_VOID = "Py_DECREF(pResult);"

TEMPLATE_RETURN = """%%type%% result = %%pyconversion%%;
    Py_DECREF(pResult);
    return result;"""

def internalize_argspec(name, argspec):
    # take argspec from the inspect module and returns MethodSpec
    args = argspec.args[1:] # remove self
    ann = argspec.annotations
    assert all(arg in ann for arg in args)
    assert all(argtype in PYTYPE2SPEC for argtype in ann.values())
    argspecs = []
    for arg in args:
        ts = PYTYPE2SPEC[ann[arg]]
        argspecs.append(ArgSpec(arg, ts))
    if 'return' in ann:
        returntype = PYTYPE2SPEC[ann['return']]
    else:
        returntype = None
    return MethodSpec(name, argspecs, returntype)

def get_objc_signature(methodspec):
    name_elems = methodspec.methodname.split('_')
    assert len(name_elems) == len(methodspec.argspecs) + 1
    returntype = methodspec.returntype
    returntype = returntype.objctype if returntype is not None else 'void'
    result_elems = ['(%s)' % returntype, name_elems[0]]
    for name_elem, arg in zip(name_elems[1:], methodspec.argspecs):
        result_elems.append(':(%s)%s %s' % (arg.typespec.objctype, arg.argname, name_elem))
    return ''.join(result_elems).strip()

def get_objc_method_code(methodspec):
    signature = get_objc_signature(methodspec)
    tmpl_args = []
    for arg in methodspec.argspecs:
        tmpl_args.append(arg.typespec.o2p_code % arg.argname)
    tmpl_args = ', '.join(tmpl_args)
    if methodspec.returntype is not None:
        ts = methodspec.returntype
        tmpl_pyconversion = ts.p2o_code % 'pResult'
        returncode = tmpl_replace(TEMPLATE_RETURN, type=ts.objctype, pyconversion=tmpl_pyconversion)
    else:
        returncode = TEMPLATE_RETURN_VOID
    code = tmpl_replace(TEMPLATE_METHOD, signature=signature, pyname=methodspec.methodname,
        args=tmpl_args, returncode=returncode)
    sig = '- %s;' % signature
    return (code, sig)

def spec_from_python_class(class_):
    methods = inspect.getmembers(class_, inspect.isfunction)
    methodspecs = []
    for name, meth in methods:
        argspec = inspect.getfullargspec(meth)
        try:
            methodspec = internalize_argspec(name, argspec)
            methodspecs.append(methodspec)
        except AssertionError:
            print("Warning: Couldn't generate spec for %s" % name)
            continue
    return ClassSpec(class_.__name__, methodspecs)

def generate_objc_code(class_, destfolder):
    # returns (header, implementation)
    clsspec = spec_from_python_class(class_)
    method_code = []
    method_sigs = []
    for methodspec in clsspec.methodspecs:
        code, sig = get_objc_method_code(methodspec)
        method_code.append(code)
        method_sigs.append(sig)
    clsname = clsspec.clsname
    header = tmpl_replace(TEMPLATE_HEADER, classname=clsname, methods='\n'.join(method_sigs))
    implementation = tmpl_replace(TEMPLATE_UNIT, classname=clsname, methods=''.join(method_code))
    copy_objp_unit(destfolder)
    with open(op.join(destfolder, '%s.h' % clsname), 'wt') as fp:
        fp.write(header)
    with open(op.join(destfolder, '%s.m' % clsname), 'wt') as fp:
        fp.write(implementation)
