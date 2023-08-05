import os.path as op
import inspect

from .base import TYPE_SPECS, tmpl_replace, copy_objp_unit

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
    self = [super initwithClassName:@"Simple"];
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

def get_objc_signature(name, argspec):
    args = argspec.args[1:] # remove self
    name_elems = name.split('_')
    assert len(name_elems) == len(args) + 1
    ann = argspec.annotations
    assert all(arg in ann for arg in args)
    assert all(argtype in TYPE_SPECS for argtype in ann.values())
    if 'return' in ann:
        return_type = TYPE_SPECS[ann['return']].objctype
    else:
        return_type = 'void'
    result_elems = ['(%s)' % return_type, name_elems[0]]
    for name_elem, arg in zip(name_elems[1:], args):
        argtype = TYPE_SPECS[ann[arg]].objctype
        result_elems.append(':(%s)%s %s' % (argtype, arg, name_elem))
    return ''.join(result_elems).strip()

def get_objc_method_code(name, argspec):
    signature = get_objc_signature(name, argspec)
    args = argspec.args[1:] # remove self
    ann = argspec.annotations
    tmpl_args = []
    for arg in args:
        ts = TYPE_SPECS[ann[arg]]
        tmpl_args.append(ts.o2p_code % arg)
    tmpl_args = ', '.join(tmpl_args)
    if 'return' in ann:
        ts = TYPE_SPECS[ann['return']]
        tmpl_pyconversion = ts.p2o_code % 'pResult'
        returncode = tmpl_replace(TEMPLATE_RETURN, type=ts.objctype, pyconversion=tmpl_pyconversion)
    else:
        returncode = TEMPLATE_RETURN_VOID
    code = tmpl_replace(TEMPLATE_METHOD, signature=signature, pyname=name, args=tmpl_args,
        returncode=returncode)
    sig = '- %s;' % signature
    return (code, sig)

def generate_objc_code(class_, destfolder):
    # returns (header, implementation)
    methods = inspect.getmembers(class_, inspect.isfunction)
    method_code = []
    method_sigs = []
    for name, meth in methods:
        argspec = inspect.getfullargspec(meth)
        try:
            code, sig = get_objc_method_code(name, argspec)
            method_code.append(code)
            method_sigs.append(sig)
        except AssertionError:
            print("Warning: Couldn't generate signature for %s" % name)
            continue
    header = tmpl_replace(TEMPLATE_HEADER, classname=class_.__name__, methods='\n'.join(method_sigs))
    implementation = tmpl_replace(TEMPLATE_UNIT, classname=class_.__name__, methods=''.join(method_code))
    copy_objp_unit(destfolder)
    with open(op.join(destfolder, '%s.h' % class_.__name__), 'wt') as fp:
        fp.write(header)
    with open(op.join(destfolder, '%s.m' % class_.__name__), 'wt') as fp:
        fp.write(implementation)
