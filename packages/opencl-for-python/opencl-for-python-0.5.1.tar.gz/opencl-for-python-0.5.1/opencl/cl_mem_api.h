#ifndef __PYX_HAVE_API__opencl__cl_mem
#define __PYX_HAVE_API__opencl__cl_mem
#include "Python.h"

static PyObject *(*__pyx_f_6opencl_6cl_mem_CyMemoryObject_Create)(cl_mem) = 0;
#define CyMemoryObject_Create __pyx_f_6opencl_6cl_mem_CyMemoryObject_Create
static int (*__pyx_f_6opencl_6cl_mem_CyView_GetBuffer)(PyObject *, Py_buffer *) = 0;
#define CyView_GetBuffer __pyx_f_6opencl_6cl_mem_CyView_GetBuffer
static PyObject *(*__pyx_f_6opencl_6cl_mem_CyView_Create)(cl_mem, Py_buffer *, PyObject *, int) = 0;
#define CyView_Create __pyx_f_6opencl_6cl_mem_CyView_Create
static int (*__pyx_f_6opencl_6cl_mem_CyMemoryObject_Check)(PyObject *) = 0;
#define CyMemoryObject_Check __pyx_f_6opencl_6cl_mem_CyMemoryObject_Check
static cl_mem (*__pyx_f_6opencl_6cl_mem_CyMemoryObject_GetID)(PyObject *) = 0;
#define CyMemoryObject_GetID __pyx_f_6opencl_6cl_mem_CyMemoryObject_GetID
static PyObject *(*__pyx_f_6opencl_6cl_mem_CyImageFormat_New)(cl_image_format) = 0;
#define CyImageFormat_New __pyx_f_6opencl_6cl_mem_CyImageFormat_New
static PyObject *(*__pyx_f_6opencl_6cl_mem_CyImage_New)(cl_mem) = 0;
#define CyImage_New __pyx_f_6opencl_6cl_mem_CyImage_New
static Py_buffer *(*__pyx_f_6opencl_6cl_mem_CyView_GetPyBuffer)(PyObject *) = 0;
#define CyView_GetPyBuffer __pyx_f_6opencl_6cl_mem_CyView_GetPyBuffer
static int (*__pyx_f_6opencl_6cl_mem_CyImage_GetBuffer)(PyObject *, Py_buffer *) = 0;
#define CyImage_GetBuffer __pyx_f_6opencl_6cl_mem_CyImage_GetBuffer
static PyObject *(*__pyx_f_6opencl_6cl_mem_CyView_CreateSubclass)(PyObject *, cl_mem, Py_buffer *, PyObject *, int) = 0;
#define CyView_CreateSubclass __pyx_f_6opencl_6cl_mem_CyView_CreateSubclass
static PyObject *(*__pyx_f_6opencl_6cl_mem_CyImage_Create)(cl_mem, Py_buffer *, int) = 0;
#define CyImage_Create __pyx_f_6opencl_6cl_mem_CyImage_Create
static int (*__pyx_f_6opencl_6cl_mem_ImageFormat_Check)(PyObject *) = 0;
#define ImageFormat_Check __pyx_f_6opencl_6cl_mem_ImageFormat_Check
static cl_image_format (*__pyx_f_6opencl_6cl_mem_ImageFormat_Get)(PyObject *) = 0;
#define ImageFormat_Get __pyx_f_6opencl_6cl_mem_ImageFormat_Get

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

static int import_opencl__cl_mem(void) {
  PyObject *module = 0;
  module = __Pyx_ImportModule("opencl.cl_mem");
  if (!module) goto bad;
  if (__Pyx_ImportFunction(module, "CyMemoryObject_Create", (void (**)(void))&__pyx_f_6opencl_6cl_mem_CyMemoryObject_Create, "PyObject *(cl_mem)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "CyView_GetBuffer", (void (**)(void))&__pyx_f_6opencl_6cl_mem_CyView_GetBuffer, "int (PyObject *, Py_buffer *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "CyView_Create", (void (**)(void))&__pyx_f_6opencl_6cl_mem_CyView_Create, "PyObject *(cl_mem, Py_buffer *, PyObject *, int)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "CyMemoryObject_Check", (void (**)(void))&__pyx_f_6opencl_6cl_mem_CyMemoryObject_Check, "int (PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "CyMemoryObject_GetID", (void (**)(void))&__pyx_f_6opencl_6cl_mem_CyMemoryObject_GetID, "cl_mem (PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "CyImageFormat_New", (void (**)(void))&__pyx_f_6opencl_6cl_mem_CyImageFormat_New, "PyObject *(cl_image_format)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "CyImage_New", (void (**)(void))&__pyx_f_6opencl_6cl_mem_CyImage_New, "PyObject *(cl_mem)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "CyView_GetPyBuffer", (void (**)(void))&__pyx_f_6opencl_6cl_mem_CyView_GetPyBuffer, "Py_buffer *(PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "CyImage_GetBuffer", (void (**)(void))&__pyx_f_6opencl_6cl_mem_CyImage_GetBuffer, "int (PyObject *, Py_buffer *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "CyView_CreateSubclass", (void (**)(void))&__pyx_f_6opencl_6cl_mem_CyView_CreateSubclass, "PyObject *(PyObject *, cl_mem, Py_buffer *, PyObject *, int)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "CyImage_Create", (void (**)(void))&__pyx_f_6opencl_6cl_mem_CyImage_Create, "PyObject *(cl_mem, Py_buffer *, int)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "ImageFormat_Check", (void (**)(void))&__pyx_f_6opencl_6cl_mem_ImageFormat_Check, "int (PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "ImageFormat_Get", (void (**)(void))&__pyx_f_6opencl_6cl_mem_ImageFormat_Get, "cl_image_format (PyObject *)") < 0) goto bad;
  Py_DECREF(module); module = 0;
  return 0;
  bad:
  Py_XDECREF(module);
  return -1;
}

#endif /* !__PYX_HAVE_API__opencl__cl_mem */
