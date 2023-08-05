#import "ObjP.h"

@implementation OPProxy
- (id)initwithClassName:(NSString *)name
{
    PyObject *pClass;
    self = [super init];
    pClass = ObjP_findPythonClass(name);
    py = PyObject_CallObject(pClass, NULL);
    Py_DECREF(pClass);
    return self;
}

- (void)dealloc
{
    Py_DECREF(py);
    [super dealloc];
}
@end

PyObject* ObjP_findPythonClass(NSString *name)
{
    PyObject *pMainModule, *pClass;
    pMainModule = PyImport_AddModule("__main__");
    pClass = PyObject_GetAttrString(pMainModule, [name UTF8String]);
    if (pClass == NULL) {
        PyErr_Print();
        PyErr_Clear();
    }
    return pClass;
}

NSString* ObjP_str_p2o(PyObject *pStr)
{
    PyObject *pBytes = PyUnicode_AsUTF8String(pStr);
    char *utf8Bytes = PyBytes_AS_STRING(pBytes);
    NSString *result = [NSString stringWithUTF8String:utf8Bytes];
    Py_DECREF(pBytes);
    return result;
}

PyObject* ObjP_str_o2p(NSString *str)
{
    return PyUnicode_FromString([str UTF8String]);
}

NSInteger ObjP_int_p2o(PyObject *pInt)
{
    return PyLong_AsLong(pInt);
}

PyObject* ObjP_int_o2p(NSInteger i)
{
    return PyLong_FromLong(i);
}

BOOL ObjP_bool_p2o(PyObject *pBool)
{
    return PyObject_IsTrue(pBool);
}

PyObject* ObjP_bool_o2p(BOOL b)
{
    if (b) {
        Py_RETURN_TRUE;
    }
    else {
        Py_RETURN_FALSE;
    }
}

NSObject* ObjP_obj_p2o(PyObject *pObj)
{
    if (pObj == Py_None) {
        return nil;
    }
    else if (PyUnicode_Check(pObj)) {
        return ObjP_str_p2o(pObj);
    }
    else if (PyLong_Check(pObj)) {
        return [NSNumber numberWithInt:ObjP_int_p2o(pObj)];
    }
    else if (PyList_Check(pObj)) {
        return ObjP_list_p2o(pObj);
    }
    else if (PyDict_Check(pObj)) {
        return ObjP_dict_p2o(pObj);
    }
    else {
        return nil;
    }
}

PyObject* ObjP_obj_o2p(NSObject *obj)
{
    if (obj == nil) {
        Py_RETURN_NONE;
    }
    else if ([obj isKindOfClass:[NSString class]]) {
        return ObjP_str_o2p((NSString *)obj);
    }
    else if ([obj isKindOfClass:[NSNumber class]]) {
        return ObjP_int_o2p([(NSNumber *)obj intValue]);
    }
    else if ([obj isKindOfClass:[NSArray class]]) {
        return ObjP_list_o2p((NSArray *)obj);
    }
    else if ([obj isKindOfClass:[NSDictionary class]]) {
        return ObjP_dict_o2p((NSDictionary *)obj);
    }
    else {
        return NULL;
    }
}

NSArray* ObjP_list_p2o(PyObject *pList)
{
    PyObject *iterator = PyObject_GetIter(pList);
    PyObject *item;
    NSMutableArray *result = [NSMutableArray array];
    while ( (item = PyIter_Next(iterator)) ) {
        [result addObject:ObjP_obj_p2o(item)];
        Py_DECREF(item);
    }
    Py_DECREF(iterator);
    return result;
}

PyObject* ObjP_list_o2p(NSArray *list)
{
    PyObject *pResult = PyList_New([list count]);
    NSInteger i;
    for (i=0; i<[list count]; i++) {
        NSObject *obj = [list objectAtIndex:i];
        PyObject *pItem = ObjP_obj_o2p(obj);
        PyList_SET_ITEM(pResult, i, pItem);
    }
    return pResult;
}

NSDictionary* ObjP_dict_p2o(PyObject *pDict)
{
    PyObject *pKey, *pValue;
    Py_ssize_t pos = 0;
    NSMutableDictionary *result = [NSMutableDictionary dictionary];
    while (PyDict_Next(pDict, &pos, &pKey, &pValue)) {
        NSString *key = ObjP_str_p2o(pKey);
        NSObject *value = ObjP_obj_p2o(pValue);
        [result setObject:value forKey:key];
    }
    return result;
}

PyObject* ObjP_dict_o2p(NSDictionary *dict)
{
    PyObject *pResult = PyDict_New();
    for (NSString *key in dict) {
        NSObject *value = [dict objectForKey:key];
        PyObject *pValue = ObjP_obj_o2p(value);
        PyDict_SetItemString(pResult, [key UTF8String], pValue);
        Py_DECREF(pValue);
    }
    return pResult;
}
