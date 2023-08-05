import weakref
import struct
import ctypes

from opencl.type_formats import type_format, size_from_format, ctype_from_format
from opencl.errors import OpenCLException
from opencl import cl_types

from libc.stdlib cimport malloc, free 
from libc.string cimport strcpy, memcpy
 
from cpython cimport PyObject, Py_DECREF, Py_INCREF, PyBuffer_IsContiguous, PyBuffer_FillContiguousStrides
from cpython cimport Py_buffer, PyBUF_SIMPLE, PyBUF_STRIDES, PyBUF_ND, PyBUF_FORMAT, PyBUF_INDIRECT, PyBUF_WRITABLE

from _cl cimport * 
from opencl.context cimport CyContext_GetID, CyContext_Create, CyContext_Check
import sys

mem_layout = cl_types.cl_uint8
    
cdef extern from "Python.h":

    object PyByteArray_FromStringAndSize(char * , Py_ssize_t)
    object PyMemoryView_FromBuffer(Py_buffer * info)
    int PyObject_GetBuffer(object obj, Py_buffer * view, int flags)
    int PyObject_CheckBuffer(object obj)
    void PyBuffer_Release(Py_buffer * view)
    
    void PyEval_InitThreads()

PyEval_InitThreads()


cdef class UserData:
    cdef object function
    cdef object args
    cdef object kwargs

cdef void pfn_notify_destroy_mem_object(cl_mem memobj, UserData user_data) with gil:
    '''
    Callback for memory destructor.
    '''
    
    mem = CyMemoryObject_Create(memobj)

    function = user_data.function
    args = user_data.args
    kwargs = user_data.kwargs
    
    function(mem, *args, **kwargs)
    
    user_data.function = None
    user_data.args = None
    user_data.kwargs = None
    
    Py_DECREF(user_data)
    
    return

cdef class MemoryObject:
    '''
    Memory objects are categorized into two types: buffer objects, and image objects.  A buffer
    object stores a one-dimensional collection of elements whereas an image object is used to store a 
    two- or three- dimensional texture, frame-buffer or image.
    '''
    BUFFER = CL_MEM_OBJECT_BUFFER
    IMAGE2D = CL_MEM_OBJECT_IMAGE2D
    IMAGE3D = CL_MEM_OBJECT_IMAGE3D    

    cdef cl_mem buffer_id
    
    def get_buffer_id(self):
        '''
        Return the pointer to the opencl memory object. 
        '''
        return ctypes.c_void_p(< size_t > self.buffer_id)
        
    def __cinit__(self):
        self.buffer_id = NULL
        
    def __dealloc__(self):
        if self.buffer_id != NULL:
            clReleaseMemObject(self.buffer_id)
        self.buffer_id = NULL
    
    
    def add_destructor_callback(self, callback, *args, **kwargs):
        '''
        memobj.add_destructor_callback(callback, *args, **kwargs)
        
        Registers a user callback function with a memory object.  Each call to 
        `add_destructor_callback` registers the specified user callback function on a 
        callback stack associated with memobj.  
        
        The registered user callback functions are called in the 
        reverse order in which they were registered.  The user callback functions are called and then the 
        memory object's resources are freed and the memory object is deleted.  This provides a 
        mechanism for the application (and libraries) using memobj to be notified when the memory 
        referenced by host_ptr, specified when the memory object is created and used as the storage bits 
        for the memory object, can be reused or freed.
        
        :param callback: function with the signature callback(memobj, *args, **kwargs) 
        '''
        Py_INCREF(callback)
        
#        cdef void * user_data = < void *> callback
        
        cdef cl_int err_code
        
        cdef UserData user_data = UserData()
        user_data.function = callback
        user_data.args = args
        user_data.kwargs = kwargs

        Py_INCREF(user_data)
        
        err_code = clSetMemObjectDestructorCallback(self.buffer_id, < void *> & pfn_notify_destroy_mem_object, < void *> user_data)
    
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)

    property context:
        '''
        Return the context that this object was created with. 
        '''
        def __get__(self):
            cdef cl_context param_value
            cdef cl_int err_code
            
            err_code = clGetMemObjectInfo(self.buffer_id, CL_MEM_CONTEXT, sizeof(size_t),
                                          < void *> & param_value, NULL)
            
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
    
            return CyContext_Create(param_value)

            
    property type:
        '''
        return the enumed type of this object. 
        One of MemoryObject.BUFFER, MemoryObject.IMAGE2D or MemoryObject.IMAGE3D
        '''
        def __get__(self):
    
            cdef cl_mem_object_type param_value
            cdef cl_int err_code
            
            err_code = clGetMemObjectInfo(self.buffer_id, CL_MEM_TYPE, sizeof(cl_mem_object_type),
                                          < void *> & param_value, NULL)
            
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
    
            return param_value
            
    property mem_size:
        '''
        Return the size in bytes of this memory object.
        '''
        def __get__(self):
    
            cdef size_t param_value
            cdef cl_int err_code
            
            err_code = clGetMemObjectInfo(self.buffer_id, CL_MEM_SIZE, sizeof(size_t),
                                          < void *> & param_value, NULL)
            
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
    
            return param_value

    property _refcount:
        '''
        Return the OpenCL internal refrence count of this object. 
        '''
        def __get__(self):
            cdef cl_uint param_value
            cdef cl_int err_code
            err_code = clGetMemObjectInfo(self.buffer_id, CL_MEM_REFERENCE_COUNT, sizeof(cl_uint),
                                           < void *>& param_value, NULL)
    
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)

            return param_value

    property _mapcount:
        def __get__(self):
            
            cdef cl_uint param_value
            cdef cl_int err_code
            err_code = clGetMemObjectInfo(self.buffer_id, CL_MEM_MAP_COUNT, sizeof(cl_uint),
                                          < void *>& param_value, NULL)
    
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)

            return param_value
        
#    property base_offset:
#        '''
#        Return the offset from `base` of this is a subbuffer. 
#        '''
#        def __get__(self):
#            
#            cdef size_t param_value
#            cdef cl_int err_code
#            
#            err_code = clGetMemObjectInfo(self.buffer_id, CL_MEM_OFFSET, sizeof(size_t),
#                                          < void *>& param_value, NULL)
#    
#            if err_code != CL_SUCCESS:
#                raise OpenCLException(err_code)
#
#            return param_value
    
    cdef cl_mem _get_base(self):
    
        cdef cl_mem param_value
        clGetMemObjectInfo(self.buffer_id, CL_MEM_ASSOCIATED_MEMOBJECT, sizeof(cl_mem), < void *>& param_value, NULL)
        return param_value
    
    property base:
        '''
        Return the original memobject if this is a sub-buffer. 
        '''
        def __get__(self):
            cdef cl_mem param_value
            cdef cl_int err_code
            
            err_code = clGetMemObjectInfo(self.buffer_id, CL_MEM_ASSOCIATED_MEMOBJECT, sizeof(cl_mem), < void *>& param_value, NULL)
    
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            if param_value == NULL:
                return None
            else:
                return CyMemoryObject_Create(param_value)
    

def mock_callback(mem, array):
    pass

cdef class DeviceMemoryView(MemoryObject):
    '''
    A buffer object stores a one-dimensional collection of elements.  Elements of a buffer object can 
    be a scalar data type (such as an int, float), vector data type, or a user-defined structure
    '''
    cdef Py_buffer * buffer    
    cdef object __weakref__
    cdef public object _host_pointer
    cdef object _ctype
    
    def __cinit__(self):
        self.buffer = NULL
        
    def __dealloc__(self):
        if self.buffer == NULL:
            return 
        
#        if self.buffer.format != NULL: free(self.buffer.format)
        if self.buffer.shape != NULL: free(self.buffer.shape)
        if self.buffer.strides != NULL: free(self.buffer.strides)

        free(self.buffer)
        
        self.buffer = NULL
        
    def __init__(self):
        raise TypeError("Can not initialize 'DeviceMemoryView' directly use 'opencl.empty'")
    
    property array_info:
        def __get__(self):
            layout = mem_layout(0, 0, 0, self.size, 0, 0, 0, 0)
            cdef int i 
            for i in range(self.buffer.ndim):
                layout[i] = self.buffer.shape[i]
                layout[4 + i] = self.buffer.strides[i] // self.itemsize
            
#            if self.context.devices[0].driver_version == '1.0': #FIXME this should be better
            layout[7] = self.offset_ // self.itemsize
                
            return layout
        
    property offset_:
        'offset from base buffer'
        def __get__(self):
            return < size_t > self.buffer.buf
        
    property ndim:
        'number of dimensions'
        def __get__(self):
            return self.buffer.ndim

    property readonly:
        'Is this memory writable'
        def __get__(self):
            return self.buffer.readonly
        
    property itemsize:
        'size of each element'
        def __get__(self):
            return self.buffer.itemsize
        
    property format:
        'ctype format of the elements'
        def __get__(self):
            if self.buffer.format != NULL:
                return self.buffer.format.decode('UTF-8')
            else:
                return "B"
        
    property shape:
        'Shape of the array'
        def __get__(self):
            shape = []
            for i in range(self.buffer.ndim):
                shape.append(self.buffer.shape[i])
            return tuple(shape)
        
    property strides:
        'Strides of the array'
        def __get__(self):
            strides = []
            for i in range(self.buffer.ndim):
                strides.append(self.buffer.strides[i])
            return tuple(strides)
        
    def reshape(self, shape):
        
        size = 1
        for d in shape: size *= d
            
        if size != self.size:
            raise ValueError("total size of new array must be unchanged")
        
        if not self.is_contiguous:
            raise Exception("array must be contiguous to reshape")
        
        cdef cl_mem buffer_id = self.buffer_id
         
        cdef Py_buffer * result_buffer = < Py_buffer *> malloc(sizeof(Py_buffer))
        
        result_buffer.buf = NULL
        cdef size_t ndim = len(shape)
        
        result_buffer.ndim = ndim
        result_buffer.itemsize = self.itemsize
        
        result_buffer.format = < char *> malloc(len(self.format) + 1)
        cdef char * fmt = self.format
        strcpy(result_buffer.format, fmt)
        
        result_buffer.shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * ndim)
        result_buffer.strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * ndim)
        
        for i, item in enumerate(shape):
            result_buffer.shape[i] = item
            
        PyBuffer_FillContiguousStrides(result_buffer.ndim, result_buffer.shape, result_buffer.strides, result_buffer.itemsize, 'C')
        
        result_buffer.internal = NULL
        result_buffer.suboffsets = NULL
        
        return CyView_Create(buffer_id, result_buffer, self.ctype, 1)
        
        
    def map(self, queue, blocking=True, readable=True, writeable=True):
        '''
        DeviceMemoryView.map(queue, blocking=True, readable=True, writeable=True)
        
        enqueues a command to map a region of the buffer object given by buffer into the host address 
        space and returns a pointer to this mapped region.
        '''
        
        from opencl.queue import MemoryViewMap
        
        cdef cl_map_flags flags = 0
        
        if readable: 
            flags |= CL_MAP_READ
        if writeable: 
            flags |= CL_MAP_WRITE
        
        cdef cl_bool blocking_map = 1 if blocking else 0
            
        return MemoryViewMap(queue, self, blocking_map, flags)

    @classmethod
    def from_host(cls, context, host, copy=True, readable=True, writeable=True):
        '''
        DeviceMemoryView.from_host(context, host, copy=True, readable=True, writeable=True)
        
        Create an OpenCL buffer from a Python memoryview object.
        '''
        if not CyContext_Check(context):
            raise TypeError("argument 'context' must be a valid opencl.Context object")
        
        if isinstance(host, int):
            host = ctypes.c_int(host)
        elif isinstance(host, float):
            host = ctypes.c_float(host)
            
        cdef cl_context ctx = CyContext_GetID(context)
         
        cdef Py_buffer view
        cdef Py_buffer * buffer = < Py_buffer *> malloc(sizeof(Py_buffer))
        cdef cl_mem buffer_id = NULL
        
        cdef int py_flags = PyBUF_SIMPLE | PyBUF_STRIDES | PyBUF_ND | PyBUF_FORMAT
        
        cdef cl_mem_flags mem_flags = 0
        if copy:
            mem_flags |= CL_MEM_COPY_HOST_PTR
        else:
            mem_flags |= CL_MEM_USE_HOST_PTR
            
        if readable and writeable:
            mem_flags |= CL_MEM_READ_WRITE
        elif readable:
            mem_flags |= CL_MEM_READ_ONLY
        elif writeable:
            mem_flags |= CL_MEM_WRITE_ONLY
        else:
            raise Exception("at least one of arguments 'readable' or 'writable' must be true")
        
        cdef cl_int err_code
        cdef char * tmp
        if not PyObject_CheckBuffer(host):
            raise Exception("argument host must support the buffer protocol (got %r)" % host)
        
        if PyObject_GetBuffer(host, & view, py_flags) < 0:
            raise Exception("argument host must support the buffer protocol (got %r)" % host)
            
        if PyBuffer_IsContiguous(& view, 'C'):
            
            buffer_id = clCreateBuffer(ctx, mem_flags, view.len, view.buf, & err_code)
            
            PyBuffer_Release(& view)
            
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            tmp = < char *> view.format
            buffer.format = < char *> malloc(len(view.format) + 1)
            strcpy(buffer.format, view.format)
            buffer.readonly = 1
            buffer.itemsize = view.itemsize
            buffer.ndim = view.ndim
            
            buffer.buf = NULL
            buffer.shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * view.ndim)
            buffer.strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * view.ndim)
            buffer.suboffsets = NULL
            
            for i in range(view.ndim):
                buffer.shape[i] = view.shape[i]
                buffer.strides[i] = view.strides[i]

            cy_buffer = CyView_Create(buffer_id, buffer, None, 0)
#            cy_buffer._host_pointer = host
            
            if not copy:
                # This will keep the referenced array around until we are done with 
                # the opencl memory
                
                #FIXME: for now this function does not appear to be safe on ubuntu
                #cy_buffer.add_destructor_callback(mock_callback, host)
                
                cy_buffer._host_pointer = host
                
            return cy_buffer
        else:
            raise NotImplementedError("data must be contiguous")
        

    def __getitem__(self, args):
        
        if not isinstance(args, tuple):
            args = (args,)
            
        if len(args) != self.buffer.ndim:
            raise IndexError("too many indices expected %i (got %i)" % (self.buffer.ndim, len(args)))
        
        ndim = self.buffer.ndim
        shape = list(self.shape)
        strides = list(self.strides)
        
        cdef size_t offset = < size_t > self.buffer.buf
        
        i = 0 
        for arg in args:
            if isinstance(arg, slice):
                start, stop, step = arg.indices(shape[i])
                shape[i] = (stop - start) // step
                modd = (stop - start) % step
                if modd != 0: shape[i] += 1
                
                offset += start * strides[i]
                strides[i] = strides[i] * step
                
                i += 1
                
            else:
                if arg < 0:
                    arg = shape[i] + arg
                
                offset += arg * strides[i]
                ndim -= 1
                del strides[i]
                del shape[i]
        
        cdef Py_buffer * buffer = < Py_buffer *> malloc(sizeof(Py_buffer)) 
        buffer.buf = NULL
        buffer.format = self.buffer.format
        buffer.readonly = self.readonly
        buffer.itemsize = self.buffer.itemsize
        buffer.ndim = ndim
        
        buffer.shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * ndim)
        buffer.strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * ndim)
        buffer.suboffsets = NULL
        
        for i in range(ndim):
            buffer.shape[i] = shape[i]
            buffer.strides[i] = strides[i]

        cdef cl_mem sub_buffer = NULL
        cdef cl_mem base = self._get_base()

        cdef cl_int err_code
        cdef size_t mem_size = self.mem_size
        cdef cl_buffer_region buffer_create_info
        
        if offset == 0:
            new_view =  CyView_Create(self.buffer_id, buffer, self.ctype, 1)
        else:
        
            if base == NULL:
                base = self.buffer_id
        
            buffer_create_info.origin = offset
            buffer_create_info.size = mem_size - offset

#        sub_buffer = clCreateSubBuffer(base, CL_MEM_READ_WRITE, CL_BUFFER_CREATE_TYPE_REGION, & buffer_create_info, & err_code)
#        if err_code != CL_SUCCESS:
#            raise OpenCLException(err_code, msg='offset=%r; mem_size=%r; strides=%r; shape=%r' % (offset, mem_size, strides, shape))
        
            buffer.buf = < void *> offset
        
            new_view = CyView_Create(base, buffer, self.ctype, 1)
    
        new_view._host_pointer = self._host_pointer
        
        return new_view 
    property size:
        'Total number of elements'
        def __get__(self):
            shape = self.shape
            size = 1
            for i in range(self.buffer.ndim):
                size *= shape[i]
            return size

    property nbytes:
        'Total number of bytes'
        def __get__(self):
            return self.size * self.buffer.itemsize

    def __len__(self):
        return self.size 
            
    property is_contiguous:
        'is this array C-contiguous'
        def __get__(self):
            
            strides = [self.buffer.itemsize]
            for i in range(self.buffer.ndim - 1):
                stride = strides[i]
                size = self.shape[-i - 1]
                strides.append(stride * size)
                
            return self.strides == tuple(strides[::-1])
        
    def copy(self, queue):
        '''
        Copy this buffer into a new object
        '''
        cdef size_t src_row_pitch = 0   
        cdef size_t src_slice_pitch = 0 
        cdef size_t dst_row_pitch = 0
        cdef size_t dst_slice_pitch = 0
        
        dest = empty(self.context, self.shape, ctype=self.format)
        
        cdef size_t offset = < size_t > self.buffer.buf
        if self.is_contiguous:
            queue.enqueue_copy_buffer(self, dest, src_offset=offset, dst_offset=0, size=self.nbytes, wait_on=())
            
        elif any(stride < 0 for stride in self.strides):
            raise NotImplementedError("stride < 0")
        
        elif self.buffer.ndim == 1:
            src_row_pitch = self.buffer.strides[0]
            src_slice_pitch = 0 
            dst_row_pitch = 0
            dst_slice_pitch = 0
            
            region = (dest.itemsize, dest.size, 1)
            src_origin = (offset, 0, 0)
            dst_origin = (0, 0, 0)
            
            queue.enqueue_copy_buffer_rect(self, dest, region, src_origin, dst_origin,
                                           src_row_pitch, src_slice_pitch,
                                           dst_row_pitch, dst_slice_pitch, wait_on=())
        elif self.buffer.ndim == 2:
            
            shape2 = self.buffer.itemsize
            shape1 = self.buffer.shape[1]
            shape0 = self.buffer.shape[0]
            
            src_row_pitch = self.buffer.strides[1]
            src_slice_pitch = self.buffer.strides[0] 

            region = shape2, shape1, shape0
            src_origin = (< size_t > self.buffer.buf, 0, 0)
            dst_origin = (0, 0, 0)
            
            queue.enqueue_copy_buffer_rect(self, dest, region, src_origin, dst_origin,
                                           src_row_pitch, src_slice_pitch,
                                           dst_row_pitch, dst_slice_pitch, wait_on=())
        else:
            raise Exception()
        
        return dest
    
    def __float__(self):
        ctype = self.item()
        return float(ctype.value)
    
    def __int__(self):
        ctype = self.item()
        return int(ctype.value)
     
    def item(self, queue=None):
        '''
        Return a python object if the size of this array is 1. 
        '''
        if self.size != 1:
            raise ValueError('can only convert an array  of size 1 to a Python scalar')
        if queue is None:
            import opencl
            queue = opencl.Queue(self.context)
        
        out = self.ctype()
        self.read(queue, out, blocking=True)
        
        return out
    
    property ctype:
        def __get__(self):
            if self._ctype is None:
                self._ctype = ctype_from_format(self.format)
            return self._ctype
        
        
    def read(self, queue, out, wait_on=(), blocking=False):
        '''
        buf.read(queue, out, wait_on=(), blocking=False)
        
        Read this buffer into a memory view
        '''
        return queue.enqueue_read_buffer(self, out, self.offset_, self.nbytes, wait_on, blocking_read=blocking)

    def write(self, queue, buf, wait_on=(), blocking=False):
        '''
        view.write(queue, buf, wait_on=(), blocking=False)
        
        Write data from a memoryview to the device.
        '''
        return queue.enqueue_write_buffer(self, buf, self.offset_, self.nbytes, wait_on, blocking_read=blocking)
           
    def __releasebuffer__(self, Py_buffer * view):
        pass
    
    @classmethod
    def _view_as_this(cls, obj):
        '''
        view DeviceMemoryView obj as this class.   
        
        Call this for subclasses of DeviceMemoryView.
        '''
        if not isinstance(obj, DeviceMemoryView):
            raise TypeError('can not create a new memory view from obj %r' % obj)
            
        cdef Py_buffer orig_buffer
        CyView_GetBuffer(obj, & orig_buffer)
        cdef Py_buffer * buffer = < Py_buffer *> malloc(sizeof(Py_buffer))
        memcpy(buffer, & orig_buffer, sizeof(Py_buffer))
        
        cdef cl_mem buffer_id = CyMemoryObject_GetID(obj)
        
        cdef char * format = buffer.format
        cdef Py_ssize_t * shape = buffer.shape
        cdef Py_ssize_t * strides = buffer.strides
        
        buffer.shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
        buffer.strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
        buffer.suboffsets = NULL
        
        
        buffer.buf = orig_buffer.buf
        
        strcpy(buffer.format, format)
        
        for i in range(buffer.ndim):
            buffer.shape[i] = shape[i]
            buffer.strides[i] = strides[i]
        
        return CyView_CreateSubclass(cls, buffer_id, buffer, obj.ctype, 1) 

def is_string(obj):

    if sys.version_info.major < 3:
        import __builtin__ as builtins
        return isinstance(obj, (str, builtins.unicode))
    else:
        return isinstance(obj, (str,))
        
def empty(context, shape, ctype='B'):
    '''
    empty(context, shape, ctype='B') -> view
    
    Create an empty buffer.
    '''
    if not CyContext_Check(context):
        raise TypeError("argument 'context' must be a valid opencl.Context object")

    cdef cl_context ctx = CyContext_GetID(context)

    cdef cl_mem_flags flags = CL_MEM_READ_WRITE
    
    cdef cl_int err_code
    
    if is_string(ctype):
        format = ctype
        ctype = ctype_from_format(format)
    else:
        format = type_format(ctype)

    cdef size_t itemsize = size_from_format(format)
    cdef size_t size = itemsize
    for i in shape:
        size *= i
        
    cdef cl_mem buffer_id = clCreateBuffer(ctx, flags, size, NULL, & err_code)

    if err_code != CL_SUCCESS:
        raise OpenCLException(err_code)

    cdef Py_buffer * buffer = < Py_buffer *> malloc(sizeof(Py_buffer))
    
    buffer.format = < char *> malloc(len(format) + 1)
    
    if is_string(format):
        format = format.encode()
        
    cdef char * tmp = < char *> format
    strcpy(buffer.format, tmp)
    buffer.buf = NULL
    buffer.readonly = 0
    buffer.itemsize = itemsize
    buffer.ndim = len(shape)
    
    buffer.shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    buffer.strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    buffer.suboffsets = NULL
    
    for i in range(buffer.ndim):
        buffer.shape[i] = shape[i]
    
    PyBuffer_FillContiguousStrides(buffer.ndim, buffer.shape, buffer.strides, buffer.itemsize, 'C')
    
    return CyView_Create(buffer_id, buffer, ctype, 0)
    

cdef class ImageFormat:
    '''
    '''
    CHANNEL_ORDERS = {
        CL_R : 'CL_R',
        CL_Rx : 'CL_Rx',
        CL_A : 'CL_A',
        CL_INTENSITY : 'CL_INTENSITY',
        CL_LUMINANCE : 'CL_LUMINANCE',
        CL_RG : 'CL_RG',
        CL_RGx : 'CL_RGx',
        CL_RA : 'CL_RA',
        CL_RGB : 'CL_RGB',
        CL_RGBx : 'CL_RGBx',
        CL_RGBA : 'CL_RGBA',
        CL_ARGB : 'CL_ARGB',
        CL_BGRA : 'CL_BGRA',
        }
        
    CHANNEL_DTYPES = {
        CL_SNORM_INT8 : 'CL_SNORM_INT8',
        CL_SNORM_INT16 : 'CL_SNORM_INT16',
        CL_UNORM_INT8 : 'CL_UNORM_INT8',
        CL_UNORM_INT16 : 'CL_UNORM_INT16',
        CL_UNORM_SHORT_565 : 'CL_UNORM_SHORT_565',
        CL_UNORM_SHORT_555 : 'CL_UNORM_SHORT_555',
        CL_UNORM_INT_101010 : 'CL_UNORM_INT_101010',
        CL_SIGNED_INT8 : 'CL_SIGNED_INT8',
        CL_SIGNED_INT16 : 'CL_SIGNED_INT16',
        CL_SIGNED_INT32 : 'CL_SIGNED_INT32',
        CL_UNSIGNED_INT8 : 'CL_UNSIGNED_INT8',
        CL_UNSIGNED_INT16 : 'CL_UNSIGNED_INT16',
        CL_UNSIGNED_INT32 : 'CL_UNSIGNED_INT32',
        CL_HALF_FLOAT : 'CL_HALF_FLOAT',
        CL_FLOAT : 'CL_FLOAT',
                      }
    
    _CHANNEL_CTYPE_MAP = {
        CL_SNORM_INT8 : 'b',
        CL_SNORM_INT16 : 'h',
        CL_UNORM_INT8 : 'B',
        CL_UNORM_INT16 : 'H',
#        CL_UNORM_SHORT_565 : 'CL_UNORM_SHORT_565',
#        CL_UNORM_SHORT_555 : 'CL_UNORM_SHORT_555',
#        CL_UNORM_INT_101010 : 'CL_UNORM_INT_101010',
        CL_SIGNED_INT8 : 'b',
        CL_SIGNED_INT16 : 'h',
        CL_SIGNED_INT32 : 'l',
        CL_UNSIGNED_INT8 : 'B',
        CL_UNSIGNED_INT16 : 'H',
        CL_UNSIGNED_INT32 : 'L',
#        CL_HALF_FLOAT : 'CL_HALF_FLOAT',
        CL_FLOAT : 'f',

                                }
    
    _CHANNEL_ORDER_CTYPE_MAP = {
        CL_R : 'T{%(dtype)s:r:}',
        #CL_Rx : 'CL_Rx',
        #CL_A : 'CL_A',
        CL_INTENSITY : 'T{%(dtype)s:i:}',
#        CL_LUMINANCE : 'CL_LUMINANCE',
#        CL_RG : 'CL_RG',
#        CL_RGx : 'CL_RGx',
#        CL_RA : 'CL_RA',
        CL_RGB : 'T{%(dtype)s:r:%(dtype)s:g:%(dtype)s:b:}',
#        CL_RGBx : 'CL_RGBx',
        CL_RGBA : 'T{%(dtype)s:r:%(dtype)s:g:%(dtype)s:b:%(dtype)s:a:}',
        CL_ARGB : 'T{%(dtype)s:a:%(dtype)s:r:%(dtype)s:g:%(dtype)s:b:}',
        CL_BGRA : 'T{%(dtype)s:b:%(dtype)s:g:%(dtype)s:r:%(dtype)s:a:}',
        }

    cdef cl_image_format cl_format
    
    @classmethod
    def supported_formats(cls, context, readable=True, wirteable=True):
        
        if not CyContext_Check(context):
            raise TypeError("argument 'context' must be a valid opencl.Context object")
        
        cdef cl_mem_flags flags
        
        if readable and wirteable:
            flags = CL_MEM_READ_WRITE
        elif not (readable ^ wirteable):
            raise TypeError("al least one of readable or wirteable must be True")
        elif readable:
            flags = CL_MEM_READ_ONLY
        else:
            flags = CL_MEM_WRITE_ONLY
            
        cdef cl_context ctx = CyContext_GetID(context)

        cdef cl_int err_code
        cdef cl_image_format * image_formats
        cdef cl_uint num_image_formats
        cdef cl_mem_object_type image_type = CL_MEM_OBJECT_IMAGE2D
        
        err_code = clGetSupportedImageFormats(ctx, flags, image_type, 0, NULL, & num_image_formats)
    
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
        
        image_formats = < cl_image_format *> malloc(sizeof(cl_image_format) * num_image_formats)

        err_code = clGetSupportedImageFormats(ctx, flags, image_type, num_image_formats, image_formats, NULL)
    
    
        if err_code != CL_SUCCESS:
            free(image_formats)
            raise OpenCLException(err_code)
        
        
        image_format_list = []
        
        cdef ImageFormat fmt
        for i in range(num_image_formats):
            fmt = CyImageFormat_New(image_formats[i])
            image_format_list.append(fmt)

        free(image_formats)
        
        return image_format_list

    @classmethod
    def from_ctype(cls, format):
        
        cdef ImageFormat fmt
        
        if not is_string(format):
            format = type_format(format)
        
        for cl_order, order in cls._CHANNEL_ORDER_CTYPE_MAP.items():
            for cl_dtype, dtype in cls._CHANNEL_CTYPE_MAP.items():
                expected_format = order % dict(dtype=dtype)
                
                if format == expected_format:
                    fmt = ImageFormat.__new__(ImageFormat)
                    fmt.cl_format.image_channel_data_type = cl_dtype
                    fmt.cl_format.image_channel_order = cl_order
                    return fmt
        else:
            raise TypeError("Could not create opencl image format from ctype format specifier (got %r)" % (format,))

    def __init__(self, str order, str dtype):
        
        order_lookup = dict([(value, key) for key, value in self.CHANNEL_ORDERS.items()])
        self.cl_format.image_channel_order = order_lookup[order]

        dtype_lookup = dict([(value, key) for key, value in self.CHANNEL_DTYPES.items()])
        self.cl_format.image_channel_data_type = dtype_lookup[dtype]
        
    property format:
        def __get__(self):
            type_format = self._CHANNEL_CTYPE_MAP[self.cl_format.image_channel_data_type]
            type_struct = self._CHANNEL_ORDER_CTYPE_MAP[self.cl_format.image_channel_order]
            
            return type_struct % dict(dtype=type_format) 

    property ctype:
        def __get__(self):
            format = self.format
            return ctype_from_format(format, struct_name=self.CHANNEL_ORDERS[self.channel_order])
        
    
    property channel_order:
        def __get__(self):
            return self.cl_format.image_channel_order

    property channel_data_type:
        def __get__(self):
            return self.cl_format.image_channel_data_type
    
    def __repr__(self):
        order = self.CHANNEL_ORDERS[self.channel_order]
        dtype = self.CHANNEL_DTYPES[self.channel_data_type]
        
        return "<ImageFormat channel_order=%r channel_data_type=%r>" % (order, dtype)
    
    def __richcmp__(ImageFormat self, other, op):
        
        if not ImageFormat_Check(other):
            return False
        
        cdef cl_image_format cl_format = ImageFormat_Get(other)
        
        if op == 2: # == 
            return ((self.cl_format.image_channel_data_type == cl_format.image_channel_data_type) and
                    self.cl_format.image_channel_order == cl_format.image_channel_order)
        else:
            return NotImplemented
        
    
cdef class Image(MemoryObject):
    cdef Py_buffer * buffer    
    cdef object __weakref__
    
    def __cinit__(self):
        self.buffer = NULL
        
    property image_format:
        def __get__(self):
            cdef cl_int err_code
            
            cdef cl_image_format image_format
            err_code = clGetImageInfo(self.buffer_id, CL_IMAGE_FORMAT, sizeof(cl_image_format), & image_format, NULL)
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            return CyImageFormat_New(image_format)

    property image_width:
        def __get__(self):
            cdef cl_int err_code
            cdef size_t value
            err_code = clGetImageInfo(self.buffer_id, CL_IMAGE_WIDTH, sizeof(size_t), & value, NULL)
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            return value

    property image_height:
        def __get__(self):
            cdef cl_int err_code
            cdef size_t value
            err_code = clGetImageInfo(self.buffer_id, CL_IMAGE_HEIGHT, sizeof(size_t), & value, NULL)
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            return value

    property image_depth:
        def __get__(self):
            cdef cl_int err_code
            cdef size_t value
            err_code = clGetImageInfo(self.buffer_id, CL_IMAGE_DEPTH, sizeof(size_t), & value, NULL)
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            return value
        
    property format:
        def __get__(self):
            if self.buffer.format != NULL:
                return self.buffer.format.decode('UTF-8')
            else:
                return "B"
        
    property shape:
        def __get__(self):
            shape = []
            for i in range(self.buffer.ndim):
                shape.append(self.buffer.shape[i])
            return tuple(shape)

    property strides:
        def __get__(self):
            strides = []
            for i in range(self.buffer.ndim):
                strides.append(self.buffer.strides[i])
            return tuple(strides)

    def map(self, queue, blocking=True, readonly=False):
        
        from opencl.queue import ImageMap 
        
        cdef cl_map_flags flags = CL_MAP_READ
        
        if not readonly: 
            flags |= CL_MAP_WRITE
        
        cdef cl_bool blocking_map = 1 if blocking else 0
            
        return ImageMap(queue, self, blocking_map, flags)


def broadcast(DeviceMemoryView view, shape):
    if not isinstance(view, DeviceMemoryView):
        raise TypeError("argument 'view' must be a valid opencl.DeviceMemoryView object")
    
    cdef DeviceMemoryView clview = < DeviceMemoryView > view
    
    cdef Py_buffer * result_buffer = < Py_buffer *> malloc(sizeof(Py_buffer))
    cdef Py_buffer buffer
    
    CyView_GetBuffer(clview, & buffer)
    cdef cl_mem memobj = CyMemoryObject_GetID(clview)
    
    cdef size_t ndim = len(shape)
    
    if ndim < buffer.ndim:
        raise TypeError("ndim of arguement shape must be >= view.ndim")
    
    cdef size_t noff = ndim - buffer.ndim
    
    for i in range(buffer.ndim):
        if  buffer.shape[i] > 1:
            if shape[noff + i] != buffer.shape[i]:
                raise TypeError("Can not broadcast dim %i from %i to %i" % (i, buffer.shape[i], shape[noff + i]))
                
    result_buffer.buf = buffer.buf
    result_buffer.ndim = ndim
    result_buffer.itemsize = buffer.itemsize
    
    result_buffer.format = < char *> malloc(len(buffer.format) + 1)
    strcpy(result_buffer.format, buffer.format)
    
    result_buffer.shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * ndim)
    result_buffer.strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * ndim)
    
    result_buffer.internal = NULL
    result_buffer.suboffsets = NULL
    
    for i in range(ndim):
        result_buffer.shape[i] = shape[i]
        result_buffer.strides[i] = 0
    
    for i in range(buffer.ndim):
        if  buffer.shape[i] > 1:
            result_buffer.strides[noff + i] = buffer.strides[i] 
        
    return CyView_Create(memobj, result_buffer, view.ctype, 1)
    
def empty_image(context, shape, image_format):
    '''
    Create an image object.
    '''
    if not CyContext_Check(context):
        raise TypeError("argument 'context' must be a valid opencl.Context object")
    
    if len(shape) not in [2, 3]:
        raise TypeError("shape must be 2 or 3 dimentional (got ndim=%i)" % len(shape))
    
    cdef cl_context ctx = CyContext_GetID(context)

    cdef cl_mem_flags flags = CL_MEM_READ_WRITE
    
    cdef cl_int err_code
    
    
    if not ImageFormat_Check(image_format):
        raise TypeError("arguement 'image_format' must be a valid ImageFormat object")
    
    cdef cl_image_format fmt = ImageFormat_Get(image_format)

    cdef size_t image_width = shape[0]
    cdef size_t image_height = shape[1]
    cdef size_t image_depth
    cdef size_t image_row_pitch = 0
    cdef size_t image_slice_pitch = 0
    cdef void * host_ptr = NULL
        
    cdef cl_mem buffer_id
    if len(shape) == 2:
        buffer_id = clCreateImage2D(ctx, flags, & fmt, image_width, image_height, image_row_pitch, NULL, & err_code)
    else:
        image_depth = shape[2]
        buffer_id = clCreateImage3D(ctx, flags, & fmt, image_width, image_height, image_depth, image_row_pitch, image_slice_pitch, NULL, & err_code)

    if err_code != CL_SUCCESS:
        raise OpenCLException(err_code)

    cdef Py_buffer * buffer = < Py_buffer *> malloc(sizeof(Py_buffer))
    
    buffer.buf = NULL
    format = image_format.format
    buffer.format = < char *> malloc(len(format) + 1)
    
    if isinstance(format, str):
        bytes_format = format.encode()
        
    cdef char * tmp = < char *> bytes_format
    
    strcpy(buffer.format, tmp)
    buffer.readonly = 0
    
    buffer.itemsize = size_from_format(format)
    buffer.ndim = len(shape)
    
    buffer.shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    buffer.strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    buffer.suboffsets = NULL
    
    for i in range(buffer.ndim):
        buffer.shape[i] = shape[i]
    
    PyBuffer_FillContiguousStrides(buffer.ndim, buffer.shape, buffer.strides, buffer.itemsize, 'C')
    
    return CyImage_Create(buffer_id, buffer, 0)

#===============================================================================
# API
#===============================================================================

cdef api object CyMemoryObject_Create(cl_mem buffer_id):
    cdef MemoryObject cview = < MemoryObject > MemoryObject.__new__(MemoryObject)
    clRetainMemObject(buffer_id)
    cview.buffer_id = buffer_id
    return cview

cdef api int CyView_GetBuffer(object view, Py_buffer * buffer):
    cdef DeviceMemoryView dview = < DeviceMemoryView > view
    buffer[0] = dview.buffer[0]
    return 0

    
cdef api object CyView_Create(cl_mem buffer_id, Py_buffer * buffer, object ctype, int incref):
    cdef DeviceMemoryView dview = < DeviceMemoryView > DeviceMemoryView.__new__(DeviceMemoryView)
    if incref:
        clRetainMemObject(buffer_id)
        
    dview.buffer_id = buffer_id
    dview.buffer = buffer
    dview._ctype = ctype
    
    return dview

cdef api object CyView_CreateSubclass(object cls, cl_mem buffer_id, Py_buffer * buffer, object ctype, int incref):
    cdef DeviceMemoryView dview = < DeviceMemoryView > cls.__new__(cls)
    if incref:
        clRetainMemObject(buffer_id)
        
    dview.buffer_id = buffer_id
    dview.buffer = buffer
    dview._ctype = ctype

    return dview

cdef api Py_buffer * CyView_GetPyBuffer(object memobj):
    obj = (< DeviceMemoryView > memobj)
    return obj.buffer



cdef api object CyImage_Create(cl_mem buffer_id, Py_buffer * buffer, int incref):
    cdef Image image = < Image > Image.__new__(Image)
    if incref:
        clRetainMemObject(buffer_id)
        
    image.buffer_id = buffer_id
    image.buffer = buffer
    
    return image

cdef api int CyImage_GetBuffer(object view, Py_buffer * buffer):
    cdef Image dview = < Image > view
    buffer[0] = dview.buffer[0]
    return 0

cdef api int CyMemoryObject_Check(object memobj):
    return isinstance(memobj, MemoryObject)

cdef api cl_mem CyMemoryObject_GetID(object memobj):
    obj = (< MemoryObject > memobj)
    cdef cl_mem buffer_id = obj.buffer_id
    return buffer_id


cdef api int ImageFormat_Check(object fmt):
    return isinstance(fmt, ImageFormat)

cdef api cl_image_format ImageFormat_Get(object fmt):
    return (< ImageFormat > fmt).cl_format

cdef api object CyImageFormat_New(cl_image_format image_format):
    cdef ImageFormat fmt = < ImageFormat > ImageFormat.__new__(ImageFormat)
    fmt.cl_format = image_format
    return fmt

cdef api object CyImage_New(cl_mem buffer_id):
    cdef Image image = < Image > Image.__new__(Image)
    image.buffer_id = buffer_id
    
    cdef Py_buffer * buffer = < Py_buffer *> malloc(sizeof(Py_buffer))
    
    format = image.image_format.format
    
    buffer.format = < char *> malloc(len(format) + 1)
    cdef char * tmp = < char *> format
    strcpy(buffer.format, tmp)
    
    buffer.readonly = 0
    buffer.itemsize = size_from_format(format)
#    buffer.ndim = len(shape)
    if image.type == CL_MEM_OBJECT_IMAGE2D:
        buffer.ndim = 2
    elif image.type == CL_MEM_OBJECT_IMAGE3D:
        buffer.ndim = 3
    else:
        raise TypeError("CyImage_New takes a valid image object as an argument")
    
    buffer.buf = NULL
    buffer.shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    buffer.strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    buffer.suboffsets = NULL
    
    buffer.shape[0] = image.image_width
    buffer.shape[1] = image.image_height
    
    if buffer.ndim == 3:
        buffer.shape[2] = image.image_depth
    
    PyBuffer_FillContiguousStrides(buffer.ndim, buffer.shape, buffer.strides, buffer.itemsize, 'C')
    
    image.buffer = buffer
    return image

