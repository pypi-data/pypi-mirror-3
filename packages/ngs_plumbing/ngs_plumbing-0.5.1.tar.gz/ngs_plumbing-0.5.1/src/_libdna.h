#ifndef Py__LIBDNA_H_
#define Py__LIBDNA_H_

#ifdef __cplusplus
extern "C" {
#endif

const unsigned char _ACGT[] = "ACGT";
const unsigned char _ASCII_TO_BIT2[] = \
  {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};


#define LIBDNA_BUFFERCHECK(NDIM_CHECK, ITEMSIZE)			\
  if (! ((buffer_ptr->ndim) NDIM_CHECK)) {				\
    PyErr_Format(PyExc_ValueError,					\
		 "Only accepts buffer_ptrs with ndim %s", #NDIM_CHECK); \
    PyBuffer_Release(buffer_ptr);					\
    return NULL;							\
  }									\
  if (buffer_ptr->itemsize != ITEMSIZE) {				\
    PyErr_Format(PyExc_ValueError,					\
		 "Only accepts buffer_ptrs with items of size %i", ITEMSIZE); \
    PyBuffer_Release(buffer_ptr);					\
    return NULL;							\
  }									\
  if (!PyBuffer_IsContiguous(buffer_ptr, 'A')) {			\
    PyErr_Format(PyExc_ValueError,					\
	       "Only accepts contiguous buffer_ptrs.");			\
    PyBuffer_Release(buffer_ptr);					\
  return NULL;								\
  }									\




#ifdef __cplusplus
}
#endif

#endif /* !Py__LIBDNA_H_ */

