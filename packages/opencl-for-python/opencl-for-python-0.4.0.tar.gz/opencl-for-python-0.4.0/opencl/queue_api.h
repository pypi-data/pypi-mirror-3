#ifndef __PYX_HAVE_API__opencl__queue
#define __PYX_HAVE_API__opencl__queue
#include "Python.h"

static cl_command_queue (*__pyx_f_6opencl_5queue_CyQueue_GetID)(PyObject *) = 0;
#define CyQueue_GetID __pyx_f_6opencl_5queue_CyQueue_GetID
static int (*__pyx_f_6opencl_5queue_CyQueue_Check)(PyObject *) = 0;
#define CyQueue_Check __pyx_f_6opencl_5queue_CyQueue_Check
static PyObject *(*__pyx_f_6opencl_5queue_CyQueue_Create)(cl_command_queue) = 0;
#define CyQueue_Create __pyx_f_6opencl_5queue_CyQueue_Create
static cl_uint (*__pyx_f_6opencl_5queue__make_wait_list)(PyObject *, cl_event **) = 0;
#define _make_wait_list __pyx_f_6opencl_5queue__make_wait_list

#ifndef __PYX_HAVE_RT_ImportModule
#define __PYX_HAVE_RT_ImportModule
static PyObject *__Pyx_ImportModule(const char *name) {
    PyObject *py_name = 0;
    PyObject *py_module = 0;

    #if PY_MAJOR_VERSION < 3
    py_name = PyString_FromString(name);
    #else
    py_name = PyUnicode_FromString(name);
    #endif
    if (!py_name)
        goto bad;
    py_module = PyImport_Import(py_name);
    Py_DECREF(py_name);
    return py_module;
bad:
    Py_XDECREF(py_name);
    return 0;
}
#endif

#ifndef __PYX_HAVE_RT_ImportFunction
#define __PYX_HAVE_RT_ImportFunction
static int __Pyx_ImportFunction(PyObject *module, const char *funcname, void (**f)(void), const char *sig) {
    PyObject *d = 0;
    PyObject *cobj = 0;
    union {
        void (*fp)(void);
        void *p;
    } tmp;

    d = PyObject_GetAttrString(module, (char *)"__pyx_capi__");
    if (!d)
        goto bad;
    cobj = PyDict_GetItemString(d, funcname);
    if (!cobj) {
        PyErr_Format(PyExc_ImportError,
            "%s does not export expected C function %s",
                PyModule_GetName(module), funcname);
        goto bad;
    }
#if PY_VERSION_HEX >= 0x02070000 && !(PY_MAJOR_VERSION==3&&PY_MINOR_VERSION==0)
    if (!PyCapsule_IsValid(cobj, sig)) {
        PyErr_Format(PyExc_TypeError,
            "C function %s.%s has wrong signature (expected %s, got %s)",
             PyModule_GetName(module), funcname, sig, PyCapsule_GetName(cobj));
        goto bad;
    }
    tmp.p = PyCapsule_GetPointer(cobj, sig);
#else
    {const char *desc, *s1, *s2;
    desc = (const char *)PyCObject_GetDesc(cobj);
    if (!desc)
        goto bad;
    s1 = desc; s2 = sig;
    while (*s1 != '\0' && *s1 == *s2) { s1++; s2++; }
    if (*s1 != *s2) {
        PyErr_Format(PyExc_TypeError,
            "C function %s.%s has wrong signature (expected %s, got %s)",
             PyModule_GetName(module), funcname, sig, desc);
        goto bad;
    }
    tmp.p = PyCObject_AsVoidPtr(cobj);}
#endif
    *f = tmp.fp;
    if (!(*f))
        goto bad;
    Py_DECREF(d);
    return 0;
bad:
    Py_XDECREF(d);
    return -1;
}
#endif

static int import_opencl__queue(void) {
  PyObject *module = 0;
  module = __Pyx_ImportModule("opencl.queue");
  if (!module) goto bad;
  if (__Pyx_ImportFunction(module, "CyQueue_GetID", (void (**)(void))&__pyx_f_6opencl_5queue_CyQueue_GetID, "cl_command_queue (PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "CyQueue_Check", (void (**)(void))&__pyx_f_6opencl_5queue_CyQueue_Check, "int (PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "CyQueue_Create", (void (**)(void))&__pyx_f_6opencl_5queue_CyQueue_Create, "PyObject *(cl_command_queue)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "_make_wait_list", (void (**)(void))&__pyx_f_6opencl_5queue__make_wait_list, "cl_uint (PyObject *, cl_event **)") < 0) goto bad;
  Py_DECREF(module); module = 0;
  return 0;
  bad:
  Py_XDECREF(module);
  return -1;
}

#endif /* !__PYX_HAVE_API__opencl__queue */
