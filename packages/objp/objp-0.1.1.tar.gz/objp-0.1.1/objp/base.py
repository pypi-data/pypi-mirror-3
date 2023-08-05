import os
import os.path as op
import shutil
from collections import namedtuple

TypeSpec = namedtuple('TypeSpec', 'pytype objctype o2p_code p2o_code')
ArgSpec = namedtuple('ArgSpec', 'argname typespec')
MethodSpec = namedtuple('MethodSpec', 'methodname argspecs returntype')
ClassSpec = namedtuple('ClassSpec', 'clsname methodspecs')

TYPE_SPECS = [
    TypeSpec(str, 'NSString *', 'ObjP_str_o2p(%s)', 'ObjP_str_p2o(%s)'),
    TypeSpec(int, 'NSInteger', 'ObjP_int_o2p(%s)', 'ObjP_int_p2o(%s)'),
    TypeSpec(bool, 'BOOL', 'ObjP_bool_o2p(%s)', 'ObjP_bool_p2o(%s)'),
    TypeSpec(object, 'id', 'ObjP_obj_o2p(%s)', 'ObjP_obj_p2o(%s)'),
    TypeSpec(list, 'NSArray *', 'ObjP_list_o2p(%s)', 'ObjP_list_p2o(%s)'),
    TypeSpec(dict, 'NSDictionary *', 'ObjP_dict_o2p(%s)', 'ObjP_dict_p2o(%s)'),
]

PYTYPE2SPEC = {ts.pytype: ts for ts in TYPE_SPECS}
OBJCTYPE2SPEC = {ts.objctype: ts for ts in TYPE_SPECS}

DATA_PATH = op.join(op.dirname(__file__), 'data')

def tmpl_replace(tmpl, **replacments):
    # Because we generate code and that code is likely to contain "{}" braces, it's better if we
    # use more explicit placeholders than the typecal format() method. These placeholders are
    # %%name%%.
    result = tmpl
    for placeholder, replacement in replacments.items():
        result = result.replace('%%{}%%'.format(placeholder), replacement)
    return result

def copy_objp_unit(destfolder):
    if not op.exists(destfolder):
        os.makedirs(destfolder)
    shutil.copy(op.join(DATA_PATH, 'ObjP.h'), destfolder)
    shutil.copy(op.join(DATA_PATH, 'ObjP.m'), destfolder)
