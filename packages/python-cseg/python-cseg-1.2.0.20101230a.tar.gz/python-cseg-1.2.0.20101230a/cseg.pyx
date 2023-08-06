cimport cstd
cimport python
cimport cseg

import exceptions

SCWS_XDICT_XDB=1
SCWS_XDICT_MEM=2
SCWS_XDICT_TXT=4

cdef class Seg(object):
	'''
	Seg class
	'''

	cdef cseg.scws_t handle

	def __cinit__(self):
		self.handle = cseg.scws_new()

	def __init__(self):
		pass

	def __dealloc__(self):
		cseg.scws_free(self.handle)
		self.handle = <cseg.scws_t>0

	def add_dict(self, char* path, int xdict_mode = 1):
		return cseg.scws_add_dict(self.handle, path, xdict_mode)

	def set_charset(self, char* charset):
		cseg.scws_set_charset(self.handle, charset)

	def set_rule(self, char* path):
		cseg.scws_set_rule(self.handle, path)

	def set_ignore(self, int yes):
		cseg.scws_set_ignore(self.handle, yes)

	def set_multi(self, int mode):
		cseg.scws_set_multi(self.handle, mode)

	def set_debug(self, int yes):
		cseg.scws_set_debug(self.handle, yes)

	def set_duality(self, int yes):
		cseg.scws_set_duality(self.handle, yes)

	def seg(self, text):
		cdef char* ptext = <char*>0
		cdef long len = 0
		if -1 == python.PyString_AsStringAndSize(text, &ptext, &len):
			raise exceptions.TypeError('Invalid parameter type, string is expected.')

		cseg.scws_send_text(self.handle, ptext, len)

		ret = []

		cdef cseg.scws_res_t res = cseg.scws_get_result(self.handle)
		cdef cseg.scws_res_t cur
		while res:
			cur = res
			while cur:
				segment = python.PyString_FromStringAndSize(ptext + cur.off, cur.len)
				ret.append((segment, cur.idf, cur.attr))
				cur = <cseg.scws_res_t>cur.next

			cseg.scws_free_result(res)

			res = cseg.scws_get_result(self.handle)

		return ret

	def stat(self, text, int limit = 0, char* attr = ''):
		'''
		'''
		cdef char* ptext = <char*>0
		cdef long len = 0
		if -1 == python.PyString_AsStringAndSize(text, &ptext, &len):
			raise exceptions.TypeError('Invalid parameter type, string is expected.')

		cseg.scws_send_text(self.handle, ptext, len)

		ret = []

		cdef cseg.scws_top_t top
		if limit > 0:
			top = cseg.scws_get_tops(self.handle, limit, attr)
		else:
			top = cseg.scws_get_words(self.handle, attr)
		cdef cseg.scws_top_t xtop = top

		if top:
			while xtop:
				ret.append((xtop.word, xtop.weight, xtop.times, xtop.attr[:2]))
				xtop = <cseg.scws_top_t>xtop.next
			cseg.scws_free_tops(top)

		return ret
