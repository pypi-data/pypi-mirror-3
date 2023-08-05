#include <Python.h>
 
static PyObject *_aliyun_test(PyObject* self, PyObject* args)
{
    const char *name;

    if(!PyArg_ParseTuple(args, "s", &name))
        return NULL;

    printf("Greeting from _aliyun.test: [%s]!\n", name);

    Py_RETURN_NONE;
}

static char _aliyun_test__doc__[] =
"Nothing but to proove _aliyun has been called correctly.\n";
 
static PyMethodDef _aliyun_methods[] =
{
    {
        "test", 
        (PyCFunction)_aliyun_test, 
        METH_VARARGS, 
        _aliyun_test__doc__    
    },
    {NULL, NULL, 0, NULL} /* no clue */
};
 
PyMODINIT_FUNC init_aliyun(void)
{
     (void) Py_InitModule("_aliyun", _aliyun_methods);
}
