#include "stringio.h"

#define IO_MAXFREELIST 1024

static StringIOObject *io_free_list[IO_MAXFREELIST];
static int io_numfree = 0;

inline void
StringIOObject_list_fill(void)
{
    StringIOObject *io;
    while (io_numfree < IO_MAXFREELIST) {
        io = PyObject_NEW(StringIOObject, &StringIOObjectType);
        io_free_list[io_numfree++] = io;
    }
}

inline void
StringIOObject_list_clear(void)
{
    StringIOObject *op;

    while (io_numfree) {
        op = io_free_list[--io_numfree];
        PyObject_DEL(op);
    }
}

static inline StringIOObject*
alloc_StringIOObject(void)
{
    StringIOObject *io;
    if (io_numfree) {
        io = io_free_list[--io_numfree];
        _Py_NewReference((PyObject *)io);
#ifdef DEBUG
        printf("use pooled StringIOObject %p\n", io);
#endif
    }else{
        io = PyObject_NEW(StringIOObject, &StringIOObjectType);
#ifdef DEBUG
        printf("alloc StringIOObject %p\n", io);
#endif
    }
    return io;
}

static inline void
dealloc_StringIOObject(StringIOObject *io)
{
    if(io->buffer){
        free_buffer(io->buffer);
        io->buffer = NULL;
    }
    if (io_numfree < IO_MAXFREELIST){
#ifdef DEBUG
        printf("back to StringIOObject pool %p\n", io);
#endif
        io_free_list[io_numfree++] = io;
    }else{
        PyObject_DEL(io);
    }
}

inline int 
CheckStringIOObject(PyObject *obj)
{
    if (obj->ob_type != &StringIOObjectType){
        return 0;
    }
    return 1;
}

inline PyObject*
StringIOObject_New(buffer *buffer)
{
    StringIOObject *io;
    io = alloc_StringIOObject();
    io->buffer = buffer;
    io->pos = 0;
    return (PyObject *)io;
}

inline void
StringIOObject_dealloc(StringIOObject *self)
{
    if(self->buffer){
        free_buffer(self->buffer);
        self->buffer = NULL;
    }
    dealloc_StringIOObject(self);
}

static inline int
is_close(StringIOObject *self)
{
    if(self->buffer == NULL){
        PyErr_SetString(PyExc_IOError, "closed");
        return 1;
    }
    return 0;
}

static inline PyObject*
StringIOObject_flush(StringIOObject *self, PyObject *args)
{
    Py_RETURN_NONE;
}

static inline PyObject* 
StringIOObject_getval(StringIOObject *self, PyObject *args)
{
    if(self->buffer == NULL){
        Py_RETURN_NONE;
    }
    PyObject *o;
    o = getPyString(self->buffer);
    self->buffer = NULL;
    return o;
}

static inline PyObject* 
StringIOObject_isatty(PyObject *self, PyObject *args)
{
    Py_INCREF(Py_False);
    return Py_False;
}

static inline PyObject* 
StringIOObject_read(StringIOObject *self, PyObject *args)
{
    Py_ssize_t n = -1, l = 0;
    PyObject *s;

    if (!PyArg_ParseTuple(args, "|n:read", &n)){
        return NULL;
    }
    if(is_close(self)){
        return NULL;
    }
    l = self->buffer->len - self->pos;
    if (n < 0 || n > l) {
        n = l;
        if (n < 0) {
            n = 0;
        }
    }
    s = PyString_FromStringAndSize(self->buffer->buf + self->pos, n);
    self->pos += n;
    //printf("%s# read %d\n", self->buffer->buf, n);
    return s;
}

static inline int
inner_readline(StringIOObject *self, char **output) {
    char *start, *end;
    Py_ssize_t l = 0;
    
    start = self->buffer->buf + self->pos;
    end = self->buffer->buf + self->buffer->len; 
    
    while(start < end){
        if(*start == '\n'){
            break;
        }
        start++;
        l++;
    }

    if (start < end){
        start++;
        l++;
    }
    //seek current pos
    *output = self->buffer->buf + self->pos;
    self->pos += l;
    return (int)l;
}

static inline PyObject* 
StringIOObject_readline(StringIOObject *self, PyObject *args)
{
    int len, size = -1, delta;
    char *output;

    if(args){
        if (!PyArg_ParseTuple(args, "|i:readline", &size)){
            return NULL;
        }
    }
    if(is_close(self)){
        return NULL;
    }

    if((len = inner_readline(self, &output)) < 0){
        return NULL;
    }
    if (size >= 0 && size < len) {
        delta = len - size;
        len -= delta;
        //back
        self->pos -= delta;
    }
    return PyString_FromStringAndSize(output, len);
}

static inline PyObject* 
StringIOObject_readlines(StringIOObject *self, PyObject *args)
{
    int len;
    char *output;
    PyObject *result, *new_line;
    int sizehint = 0, length = 0;
    
    if (!PyArg_ParseTuple(args, "|i:readlines", &sizehint)){
        return NULL;
    }
    if(is_close(self)){
        return NULL;
    }

    result = PyList_New(0);
    if (!result){
        return NULL;
    }

    while (1){
        if((len = inner_readline(self, &output)) < 0){
            goto err;
        }
        if (len == 0){
            break;
        }
        new_line = PyString_FromStringAndSize(output, len);
        if (!new_line){
            goto err;
        }
        if (PyList_Append(result, new_line) == -1) {
            Py_DECREF(new_line);
            goto err;
        }
        Py_DECREF(new_line);
        length += len;
        if (sizehint > 0 && length >= sizehint)
            break;
    }
    return result;
 err:
    Py_DECREF(result);
    return NULL;
}

static inline PyObject* 
StringIOObject_reset(StringIOObject *self, PyObject *args)
{
    self->pos = 0;
    Py_RETURN_NONE;
}

static inline PyObject* 
StringIOObject_tell(StringIOObject *self, PyObject *args)
{
    return PyInt_FromSsize_t(self->pos);
}

static inline PyObject* 
StringIOObject_truncate(StringIOObject *self, PyObject *args)
{
    Py_ssize_t pos = -1;
    
    if (!PyArg_ParseTuple(args, "|n:truncate", &pos)){
        return NULL;
    }
    if(is_close(self)){
        return NULL;
    }

    if (PyTuple_Size(args) == 0) {
        pos = self->pos;
    }

    if (pos < 0) {
        errno = EINVAL;
        PyErr_SetFromErrno(PyExc_IOError);
        return NULL;
    }
    
    //truncate
    if (self->buffer->len > pos){
        self->buffer->len = pos;
    }

    self->pos = self->buffer->len;
    Py_RETURN_NONE;
}

static inline PyObject* 
StringIOObject_close(StringIOObject *self, PyObject *args)
{
    free_buffer(self->buffer);
    self->buffer= NULL;
    self->pos = 0;
    Py_RETURN_NONE;
}

static inline PyObject* 
StringIOObject_seek(StringIOObject *self, PyObject *args)
{
    Py_ssize_t position;
    int mode = 0;

    if (!PyArg_ParseTuple(args, "n|i:seek", &position, &mode)){
        return NULL;
    }
    if(is_close(self)){
        return NULL;
    }

    if (mode == 2){
        position += self->buffer->len;
    }else if (mode == 1){
        position += self->pos;
    }

    if (position < 0){
        position = 0;
    }

    self->pos = position;

    Py_RETURN_NONE;
}

static inline PyObject *
StringIOObject_get_closed(StringIOObject *self, void *closure)
{
    PyObject *result = Py_False;

    if (self->buffer == NULL){
        result = Py_True;
    }
    Py_INCREF(result);
    return result;
}

static inline PyObject *
StringIOObject_iternext(StringIOObject *self)
{
    PyObject *next;
    if(is_close(self)){
        return NULL;
    }
    next = StringIOObject_readline(self, NULL);
    if (!next){
        return NULL;
    }
    if (!PyString_GET_SIZE(next)) {
        Py_DECREF(next);
        PyErr_SetNone(PyExc_StopIteration);
        return NULL;
    }
    return next;
}

static struct PyMethodDef StringIOObject_methods[] = {
  
  {"flush",     (PyCFunction)StringIOObject_flush,    METH_NOARGS, ""},
  {"getvalue",  (PyCFunction)StringIOObject_getval,   METH_VARARGS, ""},
  {"isatty",    (PyCFunction)StringIOObject_isatty,   METH_NOARGS, ""},
  {"read",    (PyCFunction)StringIOObject_read,     METH_VARARGS, ""},
  {"readline",    (PyCFunction)StringIOObject_readline, METH_VARARGS, ""},
  {"readlines",    (PyCFunction)StringIOObject_readlines,METH_VARARGS, ""},
  {"reset",    (PyCFunction)StringIOObject_reset,      METH_NOARGS, ""},
  {"tell",      (PyCFunction)StringIOObject_tell,     METH_NOARGS,  ""},
  {"truncate",  (PyCFunction)StringIOObject_truncate, METH_VARARGS, ""},
  {"close",     (PyCFunction)StringIOObject_close,    METH_NOARGS, ""},
  {"seek",      (PyCFunction)StringIOObject_seek,     METH_VARARGS, ""},  
  {NULL,    NULL}
};

static PyGetSetDef file_getsetlist[] = {
    {"closed", (getter)StringIOObject_get_closed, NULL, "True if the file is closed"},
    {0},
};


PyTypeObject StringIOObjectType = {
    PyObject_HEAD_INIT(&PyType_Type)
    0,
    "meinheld.stringio",             /*tp_name*/
    sizeof(StringIOObject), /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)StringIOObject_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "stringio",                 /* tp_doc */
    0,                       /* tp_traverse */
    0,                       /* tp_clear */
    0,                       /* tp_richcompare */
    0,                       /* tp_weaklistoffset */
    PyObject_SelfIter,        /*tp_iter */
    (iternextfunc)StringIOObject_iternext,        /* tp_iternext */
    StringIOObject_methods,        /* tp_methods */
    0,                         /* tp_members */
    file_getsetlist,            /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,                      /* tp_init */
    0,                         /* tp_alloc */
    0,                           /* tp_new */
};

