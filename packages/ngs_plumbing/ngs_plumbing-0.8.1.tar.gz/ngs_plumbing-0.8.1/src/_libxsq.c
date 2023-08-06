/* This file is part of ngs_plumbing. */

/* ngs_plumbing is free software: you can redistribute it and/or modify */
/* it under the terms of the GNU General Public License as published by */
/* the Free Software Foundation, either version 3 of the License, or */
/* (at your option) any later version. */

/* ngs_plumbing is distributed in the hope that it will be useful, */
/* but WITHOUT ANY WARRANTY; without even the implied warranty of */
/* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the */
/* GNU General Public License for more details. */

/* You should have received a copy of the GNU General Public License */
/* along with ngs_plumbing.  If not, see <http://www.gnu.org/licenses/>. */

/* Copyright 2012 Laurent Gautier */

#define PY_SSIZE_T_CLEAN 
#include "Python.h"

PyDoc_STRVAR(module_doc,
	     "C-level utilities to work with XSQ files");


#if (PY_VERSION_HEX < 0x03010000)
#define PyBytes PyString
#endif


#define LIBXSQ_FROMBYTES(TYPENAME, PROCESSNAME)				\
  Py_ssize_t n = TYPENAME ## _GET_SIZE(data_bytes);			\
  char *string = NULL; /* dummy */					\
  PyObject *seq_a = TYPENAME ## _FromStringAndSize(string, n);		\
  PyObject *qual_a = TYPENAME ## _FromStringAndSize(string, n);		\
  PROCESSNAME(TYPENAME ## _AS_STRING(data_bytes), n,			\
	      TYPENAME ## _AS_STRING(seq_a),				\
	      TYPENAME ## _AS_STRING(qual_a));				\
  PyTuple_SET_ITEM(res, 0, seq_a);					\
  PyTuple_SET_ITEM(res, 1, qual_a);					\
  return res;								\
  
#define LIBXSQ_FROMBUFFER(TYPENAME, PROCESSNAME)			\
  char *string = NULL; /* dummy */					\
  PyObject *seq_a = TYPENAME ## _FromStringAndSize(string, buffer_ptr->len); \
  PyObject *qual_a = TYPENAME ## _FromStringAndSize(string, buffer_ptr->len); \
  PROCESSNAME((char *)(buffer_ptr->buf), buffer_ptr->len,		\
	      TYPENAME ## _AS_STRING(seq_a),				\
	      TYPENAME ## _AS_STRING(qual_a));				\
  PyTuple_SET_ITEM(res, 0, seq_a);					\
  PyTuple_SET_ITEM(res, 1, qual_a);					\
  
#define LIBXSQ_BUFFERCHECK						\
  if ((buffer_ptr->ndim) > 1) {						\
    PyErr_Format(PyExc_ValueError,					\
		 "Only accepts buffer_ptrs of dimension one, or zero."); \
    PyBuffer_Release(buffer_ptr);					\
    return NULL;							\
  }									\
  if (buffer_ptr->itemsize !=1) {					\
    PyErr_Format(PyExc_ValueError,					\
	       "Only accepts buffer_ptrs with items of size 1");	\
  PyBuffer_Release(buffer_ptr);					\
  return NULL;								\
  }									\
  if (!PyBuffer_IsContiguous(buffer_ptr, 'A')) {			\
    PyErr_Format(PyExc_ValueError,					\
	       "Only accepts contiguous buffer_ptrs.");			\
  PyBuffer_Release(buffer_ptr);					\
  return NULL;								\
  }									\


static const char _ACGT[] = "ACGT";

static inline void basequal(const char *read, const Py_ssize_t n, 
			    char *base_ptr, char *qual_ptr)
{
  /* build the bases and corresponding qualities from the bit-packed
     values. */
  Py_ssize_t i;
  for (i=0; i<n; i++)
    {
      base_ptr[i] = _ACGT[read[i] & 0x3];
      qual_ptr[i] = ((unsigned char)(read[i])) >> 2;
      switch (qual_ptr[i]) {
      case 63: /* */
      case 0:
      case 1:
      case 2:
	base_ptr[i] = 'N';
	break;
      }
    }
}


static inline void colourqual(const char *read, const Py_ssize_t n, 
			      char *colour_ptr, char *qual_ptr)
{
  /* build the colours and corresponding qualities from the bit-packed
     values. */
  Py_ssize_t i;
  for (i=0; i < n; i++)
    {
      colour_ptr[i] = (char)(read[i] & 0x3);
      qual_ptr[i] = ((unsigned char)(read[i])) >> 2;
      switch (qual_ptr[i]) {
      case 63: /* */
      case 0:
      case 1:
      case 2:
	colour_ptr[i] = -2;
	break;
      }
    }
}

PyDoc_STRVAR(colourqual_frombytes_doc,
"Takes a bytes object and returns a pair (tuple of length 2)"
"with the colour values and the quality values.\n");
static PyObject* colourqual_frombytes(PyObject *self, PyObject *data_bytes)
{

  PyObject *res = PyTuple_New(2);
  if (PyBytes_Check(data_bytes)) {
    LIBXSQ_FROMBYTES(PyBytes, colourqual);
  } else {
    PyErr_Format(PyExc_TypeError, "Parameter must be a string (bytes).");
    return NULL;
  }
}

PyDoc_STRVAR(colourqual_frombytearray_doc,
"Takes a bytearray object and returns a pair (tuple of length 2)"
"with the colour values and the quality values.\n");
static PyObject* colourqual_frombytearray(PyObject *self, PyObject *data_bytes)
{

  PyObject *res = PyTuple_New(2);
  if (PyByteArray_Check(data_bytes)) {
    LIBXSQ_FROMBYTES(PyByteArray, colourqual);
  } else {
    PyErr_Format(PyExc_TypeError, "Parameter must be a bytearray.");
    return NULL;
  }
}

PyDoc_STRVAR(colourqual_frombuffer_doc,
"Takes a buffer-implementing object and a returns a pair (tuple of length 2)"
"with the colour values and the quality values.\n");
static PyObject* colourqual_frombuffer(PyObject *self, PyObject *data_bytes)
{
  PyObject *res = PyTuple_New(2);
  Py_buffer buffer;
  Py_buffer *buffer_ptr = &buffer;
  int err_buf = PyObject_GetBuffer(data_bytes, buffer_ptr, PyBUF_SIMPLE);
  if (err_buf == 0) {
    LIBXSQ_BUFFERCHECK
    LIBXSQ_FROMBUFFER(PyByteArray, colourqual);
    PyBuffer_Release(buffer_ptr);
    return res;
  } else {
    return NULL;
  }
}



PyDoc_STRVAR(basequal_frombytes_doc,
"Takes a bytes object a returns a pair (tuple of length 2)"
"with the base values and the quality values.\n");
static PyObject* basequal_frombytes(PyObject *self, PyObject *data_bytes)
{

  PyObject *res = PyTuple_New(2);
  if (PyBytes_Check(data_bytes)) {
    LIBXSQ_FROMBYTES(PyBytes, basequal);
  } else {
    PyErr_Format(PyExc_TypeError, "Parameter must be a string (bytes).");
    return NULL;
  }
}

PyDoc_STRVAR(basequal_frombytearray_doc,
"Takes a bytearray object a returns a pair (tuple of length 2)"
"with the colour values and the quality values.\n");
static PyObject* basequal_frombytearray(PyObject *self, PyObject *data_bytes)
{

  PyObject *res = PyTuple_New(2);
  if (PyByteArray_Check(data_bytes)) {
    LIBXSQ_FROMBYTES(PyByteArray, basequal);
  } else {
    PyErr_Format(PyExc_TypeError, "Parameter must be a bytearray.");
    return NULL;
  }
}

PyDoc_STRVAR(basequal_frombuffer_doc,
"Takes a buffer-implementing object and a returns a pair (tuple of length 2)"
"with the base values and the quality values.\n");
static PyObject* basequal_frombuffer(PyObject *self, PyObject *data_bytes)
{
  PyObject *res = PyTuple_New(2);
  Py_buffer buffer;
  Py_buffer *buffer_ptr = &buffer;
  int err_buf = PyObject_GetBuffer(data_bytes, buffer_ptr, PyBUF_SIMPLE);
  if (err_buf == 0) {
    LIBXSQ_BUFFERCHECK
    LIBXSQ_FROMBUFFER(PyByteArray, basequal);
    PyBuffer_Release(buffer_ptr);
    return res;
  } else {
    return NULL;
  }
}

PyDoc_STRVAR(bytearray_phredtoascii_doc,
"Transform a PHRED score into its ASCII representation"
" (by adding the value 64).\n");
static PyObject* bytearray_phredtoascii(PyObject *self, PyObject *data_bytes)
{

  if (! PyByteArray_Check(data_bytes)) {
    return NULL;
  }
  
  Py_ssize_t n = PyByteArray_GET_SIZE(data_bytes);
  char *string = NULL;
  PyObject *res = PyByteArray_FromStringAndSize(string ,n);
  char *bytes_in = PyByteArray_AS_STRING(data_bytes);
  char *bytes_out = PyByteArray_AS_STRING(res);
  Py_ssize_t i;
  for (i=0; i < n; i++) {
    bytes_out[i] = bytes_in[i] + 33;
  }
  return res;
}

PyDoc_STRVAR(bytearray_addint_doc,
"Add an integer to all values in a bytearray (without overflow checking). "
"To transform a PHRED score into its ASCII representation, add 64.");
static PyObject* bytearray_addint(PyObject *self, PyObject *args)
{

  unsigned char val;
  PyObject *data_bytes;
  if (!PyArg_ParseTuple(args, "O!b", &PyByteArray_Type, &data_bytes, &val)) { 
    return NULL; 
  }

  Py_ssize_t n = PyByteArray_GET_SIZE(data_bytes);
  char *string = NULL;
  PyObject *res = PyByteArray_FromStringAndSize(string ,n);
  char *bytes_in = PyByteArray_AS_STRING(data_bytes);
  char *bytes_out = PyByteArray_AS_STRING(res);
  Py_ssize_t i;
  for (i=0; i < n; i++) {
    bytes_out[i] = bytes_in[i] + val;
  }
  return res;
}

static PyMethodDef libxsq_methods[] = {
  {"colourqual_frombytes",   (PyCFunction)colourqual_frombytes,  METH_O,
   colourqual_frombytes_doc},
  {"basequal_frombytes",   (PyCFunction)basequal_frombytes,  METH_O,
   basequal_frombytes_doc},
  {"colourqual_frombytearray",   (PyCFunction)colourqual_frombytearray,  METH_O,
   colourqual_frombytearray_doc},
  {"basequal_frombytearray",   (PyCFunction)basequal_frombytearray,  METH_O,
   basequal_frombytearray_doc},
  {"colourqual_frombuffer",   (PyCFunction)colourqual_frombuffer,  METH_O,
   colourqual_frombuffer_doc},
  {"basequal_frombuffer",   (PyCFunction)basequal_frombuffer,  METH_O,
   basequal_frombuffer_doc},
  {"bytearray_phredtoascii",   (PyCFunction)bytearray_phredtoascii,  METH_O,
   bytearray_phredtoascii_doc},
  {"bytearray_addint",   (PyCFunction)bytearray_addint,  METH_VARARGS,
   bytearray_addint_doc},
  {NULL,                NULL}           /* sentinel */
};



#if (PY_VERSION_HEX < 0x03010000)
#else
static struct PyModuleDef libxsqmodule = {
   PyModuleDef_HEAD_INIT,
   "_libxsq",           /* name of module */
   module_doc,               /* module documentation, may be NULL */
   -1,                     /* size of per-interpreter state */
   libxsq_methods       /* method table */
 };
#endif

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC
#if (PY_VERSION_HEX < 0x03010000)
init_libxsq(void)
#else
PyInit__libxsq(void)
#endif
{
  /* Finalize the type object including setting type of the new type
         * object; doing it here is required for portability to Windows 
         * without requiring C++. */

  PyObject *m, *d;
  //  static void *PyRinterface_API[PyRinterface_API_pointers];
  //PyObject *c_api_object;

#if (PY_VERSION_HEX < 0x03010000)
  m = Py_InitModule3("_libxsq", libxsq_methods, module_doc);
#else
  m = PyModule_Create(&libxsqmodule);
#endif
  if (m == NULL) {
#if (PY_VERSION_HEX < 0x03010000)
    return;
#else
    return NULL;
#endif
  }

/*   /\* Initialize the C API pointer array *\/ */
/*   PyRinterface_API[ PyRinterface_IsInitialized_NUM ] =	\ */
/*     (void *)PyRinterface_IsInitialized; */
/*   PyRinterface_API[ PyRinterface_FindFun_NUM ] =	\ */
/*     (void *)PyRinterface_FindFun; */
/*   /\* Create a Capsule containing the API pointer array's address *\/ */
/*   c_api_object = PyCapsule_New((void *)PyRinterface_API,  */
/* 			       PyRinterface_API_NAME, NULL); */
/*   if (c_api_object == NULL) { */
/* #if (PY_VERSION_HEX < 0x03010000) */
/*     return; */
/* #else */
/*     return NULL; */
/* #endif */
/*   } else { */
/*     PyModule_AddObject(m, "_C_API", c_api_object); */
/*   } */
  d = PyModule_GetDict(m);

  //PyModule_AddObject(m, "initoptions", initOptions);
  //PyModule_AddObject(m, "Sexp", (PyObject *)&Sexp_Type);
#if (PY_VERSION_HEX < 0x03010000)
#else
  return m;
#endif
}

