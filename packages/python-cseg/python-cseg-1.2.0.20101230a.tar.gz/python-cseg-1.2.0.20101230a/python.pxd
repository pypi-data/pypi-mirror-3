
cdef extern from "Python.h":
	cdef int PyInt_Check(object)
	cdef object PyInt_FromLong(long)
	cdef long PyInt_AsLong(object)
	cdef int PyString_Check(object)
	cdef object PyString_FromStringAndSize(char*, long)
	cdef char* PyString_AsString(object)
	cdef int PyString_AsStringAndSize(object, char**, long*)

