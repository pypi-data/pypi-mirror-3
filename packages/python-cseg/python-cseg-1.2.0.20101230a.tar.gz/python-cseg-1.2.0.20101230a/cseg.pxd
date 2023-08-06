
cdef extern from "scws.h":
	struct scws_result "scws_result":
		int off
		float idf
		unsigned char len
		char* attr
		void* next
	ctypedef scws_result* scws_res_t

	struct scws_topword "scws_topword":
		char* word
		float weight
		short times
		char* attr
		void* next
	ctypedef scws_topword* scws_top_t

	struct scws_zchar "scws_zchar":
		pass

	ctypedef struct scws_st "scws_st":
		pass
	ctypedef scws_st* scws_t

	cdef scws_t scws_new()
	void scws_free(scws_t s)

	cdef int scws_add_dict(scws_t s, char* fpath, int mode) nogil
	cdef int scws_set_dict(scws_t s, char* fpath, int mode) nogil

	cdef void scws_set_charset(scws_t s, char* charset) nogil
	cdef void scws_set_rule(scws_t s, char* fpath) nogil

	cdef void scws_set_ignore(scws_t s, int yes)
	cdef void scws_set_multi(scws_t s, int mode)
	cdef void scws_set_debug(scws_t s, int yes)
	cdef void scws_set_duality(scws_t s, int yes)

	cdef void scws_send_text(scws_t s, char* text, int len)
	cdef scws_res_t scws_get_result(scws_t s)
	cdef void scws_free_result(scws_res_t result)

	cdef scws_top_t scws_get_tops(scws_t s, int limit, char* xattr)
	cdef void scws_free_tops(scws_top_t tops)

	cdef scws_top_t scws_get_words(scws_t s, char* xattr)
	cdef int scws_has_word(scws_t s, char* xattr)

