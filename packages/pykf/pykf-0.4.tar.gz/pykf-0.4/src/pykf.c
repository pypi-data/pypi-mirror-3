/*********************************************************************

Japanese Kanji filter module
    Copyright (c) 2002, Atsuo Ishimoto.  All rights reserved. 

Permission to use, copy, modify, and distribute this software and its 
documentation for any purpose and without fee is hereby granted, provided that
the above copyright notice appear in all copies and that both that copyright 
notice and this permission notice appear in supporting documentation, and that
the name of Atsuo Ishimoto not be used in advertising or publicity pertaining 
to distribution of the software without specific, written prior permission. 

ATSUO ISHIMOTO DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, 
INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO
EVENT SHALL ATSUO ISHIMOTO BE LIABLE FOR ANY SPECIAL, INDIRECT OR 
CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE. 

---------------------------------------------------------------------
This module is besed on kf.c written by Haruhiko Okumura.
    Copyright (c) 1995-2000 Haruhiko Okumura
	This file may be freely modified/redistributed.

Original kf.c:
	http://www.matsusaka-u.ac.jp/~okumura/kf.html
*********************************************************************/

#include <Python.h>
#include "pykf.h"
#include "convert.h"

#if PY_MAJOR_VERSION >= 3
    #define PyInt_FromLong PyLong_FromLong
    #define PyString_FromStringAndSize PyBytes_FromStringAndSize
#endif

static PyObject *EncodingError;
#define BADENCODING(d) {PyErr_Format(EncodingError, "%d", d);}
#define GUESSFAILED() {PyErr_Format(EncodingError, "Failed to detect encodnig");}



#if defined(MS_WIN32) || defined(macintosh)
static int default_enc = SJIS;
#else
static int default_enc = EUC;
#endif

#define SETDEFAULT_DOC "setdefault(enc) -> None\n\
\tSet default input encoding"

static PyObject*
pykf_setdefault(PyObject* self, PyObject* args)
{
	int enc;
	if (!PyArg_ParseTuple(args, "i:setdefalult", &enc)) 
		return NULL;

	switch (enc) {
	case UNKNOWN: case ASCII: case SJIS: case EUC: case JIS:
		default_enc = enc;
		break;
	default:
		BADENCODING(enc); return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}


#define GETDEFAULT_DOC "getdefault() -> enc\n\
\tGet default input encoding"

static PyObject*
pykf_getdefault(PyObject* self, PyObject* args)
{
    if (!PyArg_ParseTuple(args, ":getdefault")) 
		return NULL;

	return PyInt_FromLong(default_enc);
}

static int check_strict = 0;

#define SETSTRICT_DOC "setstrict(True/False) -> None\n\
\tSet strict check mode."

static PyObject*
pykf_setstrict(PyObject* self, PyObject* args)
{
	if (!PyArg_ParseTuple(args, "i:setstrict", &check_strict)) 
		return NULL;
	Py_INCREF(Py_None);
	return Py_None;
}

#define GETSTRICT_DOC "getstrict() -> int\n\
\tGet strict check mode."

static PyObject*
pykf_getstrict(PyObject* self, PyObject* args)
{
    if (!PyArg_ParseTuple(args, ":getstrict")) 
		return NULL;

	return PyInt_FromLong(check_strict);
}


#define GUESS_DOC "guess(s) -> encoding\n\
\tGuess string encoding"

static PyObject*
pykf_guess(PyObject* self, PyObject* args)
{
	unsigned char *s;
	int ret, len;
	int strict = check_strict;
	
    if (!PyArg_ParseTuple(args, "s#|i:guess", &s, &len, &strict)) 
		return NULL;

	ret = guess(len, s, strict);
	return PyInt_FromLong(ret);
}



#define TOJIS_DOC "tojis(s[, enc]) -> converted string\n\
\tConvet string to JIS encoding"

static PyObject*
pykf_tojis(PyObject* self, PyObject* args, PyObject* kwds)
{
	unsigned char *s, *conv;
	int enc=UNKNOWN, len, convlen;
	PyObject *ret;
	int strict = check_strict;
	int j0208 = 0;
	static char *kwlist[] = {"s", "enc", "strict", "j0208", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "s#|iii:tojis", kwlist, &s, &len, &enc, &strict, &j0208))
		return NULL;

//    if (!PyArg_ParseTuple(args, "s#|ii:tojis", &s, &len, &enc, &strict))

	if (enc == UNKNOWN) {
		enc = guess(len, s, strict);
		if (strict && enc == ERROR) {
			GUESSFAILED(); return NULL;
		}
		if (enc == UNKNOWN)
			enc = default_enc;
		if (enc == UNKNOWN) {
			GUESSFAILED(); return NULL;
		}
	}
	
	switch (enc) {
	case SJIS:
		if (sjistojis(len, s, &conv, &convlen, j0208)) {
			if (convlen) {
				ret = PyString_FromStringAndSize((char*)conv, convlen);
				free(conv);
			}
			else {
				ret = PyString_FromStringAndSize("", 0);
			}
			return ret;
		}
		break;
	case EUC:
		if (euctojis(len, s, &conv, &convlen, j0208)) {
			if (convlen) {
				ret = PyString_FromStringAndSize((char*)conv, convlen);
				free(conv);
			}
			else {
				ret = PyString_FromStringAndSize("", 0);
			}
			return ret;
		}
		break;
	case JIS:
	case ASCII:
		return PyString_FromStringAndSize((char*)s, len);
	default:
		BADENCODING(enc); return NULL;
	}
	return PyErr_NoMemory();
}


#define TOEUC_DOC "toeuc(s[, enc]) -> converted string\n\
\tConvet string to EUC encoding"

static PyObject*
pykf_toeuc(PyObject* self, PyObject* args, PyObject* kwds)
{
	unsigned char *s, *conv;
	int enc=UNKNOWN, len, convlen;
	PyObject *ret;
	int strict = check_strict;
	
	static char *kwlist[] = {"s", "enc", "strict", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "s#|ii:toeuc", kwlist, &s, &len, &enc, &strict))
		return NULL;

	if (enc == UNKNOWN) {
		enc = guess(len, s, strict);
		if (strict && enc == ERROR) {
			GUESSFAILED(); return NULL;
		}
		if (enc == UNKNOWN)
			enc = default_enc;
		if (enc == UNKNOWN) {
			GUESSFAILED(); return NULL;
		}
	}
	
	switch (enc) {
	case SJIS:
		if (sjistoeuc(len, s, &conv, &convlen)) {
			if (convlen) {
				ret = PyString_FromStringAndSize((char*)conv, convlen);
				free(conv);
			}
			else {
				ret = PyString_FromStringAndSize("", 0);
			}
			return ret;
		}
		break;
	case JIS:
		if (jistoeuc(len, s, &conv, &convlen)) {
			if (convlen) {
				ret = PyString_FromStringAndSize((char*)conv, convlen);
				free(conv);
			}
			else {
				ret = PyString_FromStringAndSize("", 0);
			}
			return ret;
		}
		break;
	case EUC:
	case ASCII:
		return PyString_FromStringAndSize((char*)s, len);
	default:
		BADENCODING(enc); return NULL;
	}

	return PyErr_NoMemory();
}


#define TOSJIS_DOC "tosjis(s[, enc]) -> converted string\n\
\tConvet string to SJIS encoding"

static PyObject*
pykf_tosjis(PyObject* self, PyObject* args, PyObject *kwds)
{
	unsigned char *s, *conv;
	int enc=UNKNOWN, len, convlen;
	PyObject *ret;
	int strict = check_strict;
	
	static char *kwlist[] = {"s", "enc", "strict", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "s#|ii:tosjis", kwlist, &s, &len, &enc, &strict))
		return NULL;


	if (enc == UNKNOWN) {
		enc = guess(len, s, strict);
		if (strict && enc == ERROR) {
			GUESSFAILED(); return NULL;
		}
		if (enc == UNKNOWN)
			enc = default_enc;
		if (enc == UNKNOWN) {
			GUESSFAILED(); return NULL;
		}
	}
	
	switch (enc) {
	case SJIS:
	case ASCII:
		return PyString_FromStringAndSize((char*)s, len);
	case JIS:
		if (jistosjis(len, s, &conv, &convlen)) {
			if (convlen) {
				ret = PyString_FromStringAndSize((char*)conv, convlen);
				free(conv);
			}
			else {
				ret = PyString_FromStringAndSize("", 0);
			}
			return ret;
		}
		break;
	case EUC:
		if (euctosjis(len, s, &conv, &convlen)) {
			if (convlen) {
				ret = PyString_FromStringAndSize((char*)conv, convlen);
				free(conv);
			}
			else {
				ret = PyString_FromStringAndSize("", 0);
			}
			return ret;
		}
		break;
	default:
		BADENCODING(enc); return NULL;
	}

	return PyErr_NoMemory();
}

#define TOHALF_DOC "tohalf(s[, enc]) -> converted string\n\
\tConvet string to half width character"

static PyObject*
pykf_tohalfkana(PyObject* self, PyObject* args, PyObject *kwds)
{
	unsigned char *s, *conv;
	int enc=UNKNOWN, len, convlen;
	PyObject *ret;
	int strict = check_strict;
	
	static char *kwlist[] = {"s", "enc", "strict", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "s#|ii:tohalf", kwlist, &s, &len, &enc, &strict))
		return NULL;

	if (enc == UNKNOWN) {
		enc = guess(len, s, strict);
		if (strict && enc == ERROR) {
			GUESSFAILED(); return NULL;
		}
		if (enc == UNKNOWN)
			enc = default_enc;
		if (enc == UNKNOWN) {
			GUESSFAILED(); return NULL;
		}
	}
	
	switch (enc) {
	case SJIS:
		if (sjistohankana(len, s, &conv, &convlen)) {
			if (convlen) {
				ret = PyString_FromStringAndSize((char*)conv, convlen);
				free(conv);
			}
			else {
				ret = PyString_FromStringAndSize("", 0);
			}
			return ret;
		}
		break;
	case EUC:
		if (euctohankana(len, s, &conv, &convlen)) {
			if (convlen) {
				ret = PyString_FromStringAndSize((char*)conv, convlen);
				free(conv);
			}
			else {
				ret = PyString_FromStringAndSize("", 0);
			}
			return ret;
		}
		break;
	default:
		BADENCODING(enc); return NULL;
	}

	return PyErr_NoMemory();
}


#define TOFULL_DOC "tofull(s[, enc]) -> converted string\n\
\tConvet string to full width character"

static PyObject*
pykf_tofullkana(PyObject* self, PyObject* args, PyObject *kwds)
{
	unsigned char *s, *conv;
	int enc=UNKNOWN, len, convlen;
	int strict = check_strict;
	PyObject *ret;
	
	static char *kwlist[] = {"s", "enc", "strict", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "s#|ii:tofull", kwlist, &s, &len, &enc, &strict))
		return NULL;


	if (enc == UNKNOWN) {
		enc = guess(len, s, strict);
		if (strict && enc == ERROR) {
			GUESSFAILED(); return NULL;
		}
		if (enc == UNKNOWN)
			enc = default_enc;
		if (enc == UNKNOWN) {
			GUESSFAILED(); return NULL;
		}
	}
	
	switch (enc) {
	case SJIS:
		if (sjistofullkana(len, s, &conv, &convlen)) {
			if (convlen) {
				ret = PyString_FromStringAndSize((char*)conv, convlen);
				free(conv);
			}
			else {
				ret = PyString_FromStringAndSize("", 0);
			}
			return ret;
		}
		break;
	case EUC:
		if (euctofullkana(len, s, &conv, &convlen)) {
			if (convlen) {
				ret = PyString_FromStringAndSize((char*)conv, convlen);
				free(conv);
			}
			else {
				ret = PyString_FromStringAndSize("", 0);
			}
			return ret;
		}
		break;
	default:
		BADENCODING(enc); return NULL;
	}

	return PyErr_NoMemory();
}


#define SPLIT_DOC "tosjis(s[, enc]) -> list of chars\n\
\tConvet string to list of chars"

static PyObject*
pykf_split(PyObject* self, PyObject* args, PyObject *kwds)
{
	unsigned char *s;
	int enc=UNKNOWN, len;
	int pos;
	PyObject *ret, *o;
	int strict = check_strict;
    enum {NORMAL, KANJI, HANKANA} mode = NORMAL;
	
	static char *kwlist[] = {"s", "enc", "strict", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "s#|ii:split", kwlist, &s, &len, &enc, &strict))
		return NULL;

	if (enc == UNKNOWN) {
		enc = guess(len, s, strict);
		if (strict && enc == ERROR) {
			GUESSFAILED(); return NULL;
		}
		if (enc == UNKNOWN)
			enc = default_enc;
		if (enc == UNKNOWN) {
			GUESSFAILED(); return NULL;
		}
	}
	
	ret = PyList_New(0);
	if (!ret) {
		return NULL;
	}
	switch (enc) {
	case SJIS:
		for (pos = 0; pos < len; pos++) {
	        if (issjis1(s[pos]) && (pos + 1 < len) && issjis2(s[pos+1])) {
				o = PyString_FromStringAndSize((char*)s+pos, 2);
				pos++;
			}
			else {
				o = PyString_FromStringAndSize((char*)s+pos, 1);
			}
			if (!o) {
				Py_DECREF(ret);
				return NULL;
			}
			if (-1 == PyList_Append(ret, o)) {
				Py_DECREF(ret);
				return NULL;
			}
			Py_DECREF(o);
		}
		return ret;
	case ASCII:
		for (pos = 0; pos < len; pos++) {
			o = PyString_FromStringAndSize((char*)s+pos, 1);
			if (!o) {
				Py_DECREF(ret);
				return NULL;
			}
			if (-1 == PyList_Append(ret, o)) {
				Py_DECREF(ret);
				return NULL;
			}
			Py_DECREF(o);
		}
		return ret;
	case JIS:
		for (pos = 0; pos < len; pos++) {
			
			if ((pos + 2 < len) && 
				(!memcmp(s+pos, "\x1b$@", 3) || 
				 !memcmp(s+pos, "\x1b$B", 3))) {

				mode = KANJI;
				o = PyString_FromStringAndSize((char*)s+pos, 3);
				pos += 2;
			}
			else if ((pos + 3 < len) && !memcmp(s+pos, "\x1b$(O", 4)) {
				mode = KANJI;
				o = PyString_FromStringAndSize((char*)s+pos, 3);
				pos += 3;
			}
			else if ((pos + 2 < len) && 
					(!memcmp(s+pos, "\x1b(B", 3) || 
					 !memcmp(s+pos, "\x1b(J", 3))) {

				mode = NORMAL;
				o = PyString_FromStringAndSize((char*)s+pos, 3);
				pos += 2;
			}
			else if ((pos + 2 < len) && !memcmp(s+pos, "\x1b(I", 3)) {
				mode = HANKANA;
				o = PyString_FromStringAndSize((char*)s+pos, 3);
				pos += 2;
			}
			else if (s[pos] == '\x0e') {
				mode = HANKANA;
				o = PyString_FromStringAndSize((char*)s+pos, 1);
			}
			else if (s[pos] == '\x0f') {
				mode = NORMAL;
				o = PyString_FromStringAndSize((char*)s+pos, 1);
			}
			else if (mode == KANJI && isjis(s[pos]) && (pos+1 < len) && isjis(s[pos+1])) {
				o = PyString_FromStringAndSize((char*)s+pos, 2);
				pos++;
			} else if (mode == HANKANA && s[pos] >= 0x20 && s[pos] <= 0x5f) {
				o = PyString_FromStringAndSize((char*)s+pos, 1);
			} else {
				o = PyString_FromStringAndSize((char*)s+pos, 1);
			}
			if (!o) {
				Py_DECREF(ret);
				return NULL;
			}
			if (-1 == PyList_Append(ret, o)) {
				Py_DECREF(ret);
				return NULL;
			}
			Py_DECREF(o);
		}
		return ret;
	case EUC:
		for (pos = 0; pos < len; pos++) {
	        if (iseuc(s[pos]) && (pos + 1 < len) && iseuc(s[pos+1])) {
				o = PyString_FromStringAndSize((char*)s+pos, 2);
				pos++;
	        } else if ((s[pos] == 0x8e) && (pos + 1 < len) && ishankana(s[pos+1])) {
				o = PyString_FromStringAndSize((char*)s+pos, 2);
				pos++;
			}
			else {
				o = PyString_FromStringAndSize((char*)s+pos, 1);
			}
			if (!o) {
				Py_DECREF(ret);
				return NULL;
			}
			if (-1 == PyList_Append(ret, o)) {
				Py_DECREF(ret);
				return NULL;
			}
			Py_DECREF(o);
		}
		return ret;
	default:
		BADENCODING(enc); return NULL;
	}

	return PyErr_NoMemory();
}




static PyMethodDef pykf_methods[] = {
    {"setdefault",      (PyCFunction)pykf_setdefault,   METH_VARARGS, SETDEFAULT_DOC},
    {"getdefault",      (PyCFunction)pykf_getdefault,   METH_VARARGS, GETDEFAULT_DOC},
    {"guess",      (PyCFunction)pykf_guess,   METH_VARARGS, GUESS_DOC},
    {"tojis",      (PyCFunction)pykf_tojis,   METH_VARARGS|METH_KEYWORDS, TOJIS_DOC},
    {"tosjis",      (PyCFunction)pykf_tosjis,   METH_VARARGS|METH_KEYWORDS, TOSJIS_DOC},
    {"toeuc",      (PyCFunction)pykf_toeuc,   METH_VARARGS|METH_KEYWORDS, TOEUC_DOC},
    {"tohalf_kana",      (PyCFunction)pykf_tohalfkana,   METH_VARARGS|METH_KEYWORDS, TOHALF_DOC},
    {"tofull_kana",      (PyCFunction)pykf_tofullkana,   METH_VARARGS|METH_KEYWORDS, TOFULL_DOC},
    {"split",      (PyCFunction)pykf_split,   METH_VARARGS|METH_KEYWORDS, SPLIT_DOC},
    {"setstrict",      (PyCFunction)pykf_setstrict,   METH_VARARGS|METH_KEYWORDS, SETSTRICT_DOC},
    {"getstrict",      (PyCFunction)pykf_getstrict,   METH_VARARGS|METH_KEYWORDS, GETSTRICT_DOC},
    {NULL,      NULL}       /* sentinel */
};


static void _setint(PyObject* dict, char *name, int value)
{
	PyObject* v;
    v = PyInt_FromLong((long) value);
    PyDict_SetItemString(dict, name, v);
    Py_XDECREF(v);
}

#if PY_MAJOR_VERSION >= 3
    static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "pykf",              /* m_name */
        "",                  /* m_doc */
        -1,                  /* m_size */
        pykf_methods,        /* m_methods */
        NULL,                /* m_reload */
        NULL,                /* m_traverse */
        NULL,                /* m_clear */
        NULL,                /* m_free */
    };
#endif


#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC PyInit_pykf(void)
#else
DL_EXPORT(void) initpykf(void)
#endif
{
    PyObject *m, *d;
	int one = 1;
	int is_little_endian = (int)*(char*)&one;
#if PY_MAJOR_VERSION >= 3
	m = PyModule_Create(&moduledef);
#else
	m =  Py_InitModule("pykf", pykf_methods);
#endif
	d = PyModule_GetDict(m);

	EncodingError = PyErr_NewException("pykf.IllegalEncoding", NULL, NULL);
	PyDict_SetItemString(d, "IllegalEncoding", EncodingError);

	_setint(d, "ERROR", ERROR);
	_setint(d, "UNKNOWN", UNKNOWN);
	_setint(d, "ASCII", ASCII);
	_setint(d, "SJIS", SJIS);
	_setint(d, "EUC", EUC);
	_setint(d, "JIS", JIS);
	_setint(d, "UTF8", UTF8);
	_setint(d, "UTF16_LE", UTF16_LE);
	_setint(d, "UTF16_BE", UTF16_BE);
	if (is_little_endian) {
		_setint(d, "UTF16", UTF16_LE);
	}
	else {
		_setint(d, "UTF16", UTF16_BE);
	}

#if PY_MAJOR_VERSION >= 3
	return m;
#endif    
}



