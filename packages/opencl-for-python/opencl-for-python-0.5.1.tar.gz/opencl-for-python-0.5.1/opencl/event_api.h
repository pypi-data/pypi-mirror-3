#ifndef __PYX_HAVE_API__opencl__event
#define __PYX_HAVE_API__opencl__event
#include "Python.h"

static PyObject *(*__pyx_f_6opencl_5event_cl_eventAs_PyEvent)(cl_event) = 0;
#define cl_eventAs_PyEvent __pyx_f_6opencl_5event_cl_eventAs_PyEvent
static cl_event (*__pyx_f_6opencl_5event_cl_eventFrom_PyEvent)(PyObject *) = 0;
#define cl_eventFrom_PyEvent __pyx_f_6opencl_5event_cl_eventFrom_PyEvent
static PyObject *(*__pyx_f_6opencl_5event_PyEvent_New)(cl_event) = 0;
#define PyEvent_New __pyx_f_6opencl_5event_PyEvent_New
static int (*__pyx_f_6opencl_5event_PyEvent_Check)(PyObject *) = 0;
#define PyEvent_Check __pyx_f_6opencl_5event_PyEvent_Check

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

static int import_opencl__event(void) {
  PyObject *module = 0;
  module = __Pyx_ImportModule("opencl.event");
  if (!module) goto bad;
  if (__Pyx_ImportFunction(module, "cl_eventAs_PyEvent", (void (**)(void))&__pyx_f_6opencl_5event_cl_eventAs_PyEvent, "PyObject *(cl_event)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "cl_eventFrom_PyEvent", (void (**)(void))&__pyx_f_6opencl_5event_cl_eventFrom_PyEvent, "cl_event (PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "PyEvent_New", (void (**)(void))&__pyx_f_6opencl_5event_PyEvent_New, "PyObject *(cl_event)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "PyEvent_Check", (void (**)(void))&__pyx_f_6opencl_5event_PyEvent_Check, "int (PyObject *)") < 0) goto bad;
  Py_DECREF(module); module = 0;
  return 0;
  bad:
  Py_XDECREF(module);
  return -1;
}

#endif /* !__PYX_HAVE_API__opencl__event */
