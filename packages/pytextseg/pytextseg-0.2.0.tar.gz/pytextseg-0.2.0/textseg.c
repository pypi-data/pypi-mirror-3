/*
 * textseg.c - Implementation of _textseg module for Python.
 *
 * Copyright (C) 2012 by Hatuka*nezumi - IKEDA Soji.
 *
 * This file is part of the pytextseg package.  This program is free
 * software; you can redistribute it and/or modify it under the terms of
 * either the GNU General Public License or the Artistic License, as
 * specified in the README file.
 *
 */

#include <sombok.h>
#include <Python.h>
#include "structmember.h"
#include "python_compat.h"
/* for Win32 with Visual Studio (MSVC) */
#ifdef _MSC_VER
#  define strcasecmp _stricmp
#endif /* _MSC_VER */

/***
 *** Objects
 ***/

struct _TDictObject;

typedef struct {
    PyObject_HEAD
    linebreak_t * obj;
    struct _TDictObject * tdict;
} LineBreakObject;

typedef struct {
    PyObject_HEAD
    gcstring_t * obj;
} GCStrObject;

typedef enum {
    TDICT_LBC,
    TDICT_EAW
} tdicttype;

typedef struct _TDictObject {
    PyObject_HEAD
    PyObject * lb;
    tdicttype ttype;
    struct _TDictObject * prev;
    struct _TDictObject * next;
} TDictObject;

static PyTypeObject LineBreak_Type;
static PyTypeObject GCStr_Type;
static PyTypeObject TDict_Type;

#define LineBreak_Check(op) PyObject_TypeCheck(op, &LineBreak_Type)
#define LineBreak_CheckExact(op) (Py_TYPE(op) == &LineBreak_Type)
#define GCStr_Check(op) PyObject_TypeCheck(op, &GCStr_Type)
#define GCStr_CheckExact(op) (Py_TYPE(op) == &GCStr_Type)
/* TDictObject does not expect subclassing. */
#define TDict_CheckExact(op) (Py_TYPE(op) == &TDict_Type)

/***
 *** Constants
 ***/

static PyObject * TEXTSEG_SIMPLE, * TEXTSEG_NEWLINE, * TEXTSEG_TRIM,
		* TEXTSEG_BREAKURI, * TEXTSEG_NONBREAKURI,
		* TEXTSEG_UAX11, * TEXTSEG_FORCE, * TEXTSEG_RAISE;

/***
 *** Data conversion.
 ***/

/*
 * Convert PyUnicodeObject to Unicode string.
 * If error occurred, exception will be raised and NULL will be returned.
 * @note Unicode buffer will be copied.
 */
static unistr_t *
unicode_ToCstruct(unistr_t * unistr, PyObject * pyobj)
{
    size_t i;
    unichar_t *uni;
    PyObject *pystr;
    Py_ssize_t len;
    void *ucs;
#ifdef OLDAPI_Py_UNICODE_NARROW
    unichar_t uc1, uc2;
    size_t unilen;
    int pass;
#else				/* OLDAPI_Py_UNICODE_NARROW */
    int kind;
#endif				/* OLDAPI_Py_UNICODE_NARROW */

    if (pyobj == NULL)
	return NULL;
    else if (PyUnicode_Check(pyobj))
	pystr = pyobj;
    else if ((pystr = PyObject_Unicode(pyobj)) == NULL)
	return NULL;

    if (PyUnicode_READY(pystr) != 0) {
	if (!PyUnicode_Check(pyobj)) {
	    Py_DECREF(pystr);
	}
	return NULL;
    }
    if ((len = PyUnicode_GET_LENGTH(pystr)) == 0) {
	if (!PyUnicode_Check(pyobj)) {
	    Py_DECREF(pystr);
	}
	unistr->str = NULL;
	unistr->len = 0;
	return unistr;
    }
    ucs = PyUnicode_DATA(pystr);

#ifdef OLDAPI_Py_UNICODE_NARROW
    for (pass = 1; pass <= 2; pass++) {
	for (i = 0, unilen = 0; i < len; i++, unilen++) {
	    uc1 = (unichar_t) ((Py_UCS2 *) ucs)[i];
	    if (Py_UNICODE_IS_HIGH_SURROGATE(uc1) &&
		i + 1 < len &&
		(uc2 = (unichar_t) ((Py_UCS2 *) ucs)[i + 1]) &&
		Py_UNICODE_IS_LOW_SURROGATE(uc2)) {
		if (pass == 2)
		    uni[unilen] = Py_UNICODE_JOIN_SURROGATES(uc1, uc2);
		i++;
	    } else if (pass == 2)
		uni[unilen] = uc1;
	}

	if (pass == 1) {
	    if ((uni = malloc(sizeof(unichar_t) * (unilen + 1))) == NULL) {
		PyErr_SetFromErrno(PyExc_RuntimeError);

		if (!PyUnicode_Check(pyobj)) {
		    Py_DECREF(pystr);
		}
		return NULL;
	    }
	    uni[unilen] = 0;
	}
    }

    unistr->str = uni;
    unistr->len = unilen;
#else				/* OLDAPI_Py_UNICODE_NARROW */
    kind = PyUnicode_KIND(pystr);

    if ((uni = malloc(sizeof(unichar_t) * (len + 1))) == NULL) {
	PyErr_SetFromErrno(PyExc_RuntimeError);

	if (!PyUnicode_Check(pyobj)) {
	    Py_DECREF(pystr);
	}
	return NULL;
    }
    uni[len] = 0;

    if ((kind == PyUnicode_1BYTE_KIND &&
	 sizeof(Py_UCS1) == sizeof(unichar_t)) ||
	(kind == PyUnicode_2BYTE_KIND &&
	 sizeof(Py_UCS2) == sizeof(unichar_t)) ||
	(kind == PyUnicode_4BYTE_KIND &&
	 sizeof(Py_UCS4) == sizeof(unichar_t)))
	memcpy(uni, ucs, sizeof(unichar_t) * len);
    else if (kind == PyUnicode_1BYTE_KIND)
	for (i = 0; i < len; i++)
	    uni[i] = (unichar_t) ((Py_UCS1 *) ucs)[i];
    else if (kind == PyUnicode_2BYTE_KIND)
	for (i = 0; i < len; i++)
	    uni[i] = (unichar_t) ((Py_UCS2 *) ucs)[i];
    else if (kind == PyUnicode_4BYTE_KIND)
	for (i = 0; i < len; i++)
	    uni[i] = (unichar_t) ((Py_UCS4 *) ucs)[i];
    else {
	PyErr_SetString(PyExc_SystemError, "invalid kind.");

	free(uni);
	return NULL;
    }

    unistr->str = uni;
    unistr->len = len;
#endif				/* OLDAPI_Py_UNICODE_NARROW */

    if (!PyUnicode_Check(pyobj)) {
	Py_DECREF(pystr);
    }
    return unistr;
}

/*
 * Convert Unicode string to PyUnicodeObject
 * If error occurred, exception will be raised and NULL will be returned.
 * @note buffer of Unicode characters will be copied.
 */
static PyObject *
unicode_FromCstruct(unistr_t * unistr)
{
    size_t i, unilen;
    void *ucs;
    PyObject *ret;
#ifdef OLDAPI_Py_UNICODE_NARROW
    size_t len;
    unichar_t unichar;
    int pass;
#else				/* OLDAPI_Py_UNICODE_NARROW */
    int kind;
#endif				/* OLDAPI_Py_UNICODE_NARROW */

    if (unistr->str == NULL || unistr->len == 0) {
	Py_UCS2 buf[1] = { 0 };
	return PyUnicode_FromKindAndData(PyUnicode_2BYTE_KIND, buf, 0);
    }

    unilen = unistr->len;

#ifdef OLDAPI_Py_UNICODE_NARROW
    for (pass = 1; pass <= 2; pass++) {
	for (i = 0, len = 0; i < unilen; i++, len++) {
	    unichar = unistr->str[i];

	    if ((unichar_t) 0x10000 <= unichar) {
		if (pass == 2) {
		    ((Py_UCS2 *) ucs)[len] =
			(Py_UCS2) Py_UNICODE_HIGH_SURROGATE(unichar);
		    ((Py_UCS2 *) ucs)[len + 1] =
			(Py_UCS2) Py_UNICODE_LOW_SURROGATE(unichar);
		}
		len++;
	    } else if (pass == 2)
		((Py_UCS2 *) ucs)[len] = (Py_UCS2) unichar;
	}

	if (pass == 1) {
	    if ((ucs = PyMem_Malloc(sizeof(Py_UCS2) * len)) == NULL)
		return NULL;
	}
    }
    ret = PyUnicode_FromKindAndData(PyUnicode_2BYTE_KIND, ucs, len);
    PyMem_Free(ucs);
#else				/* OLDAPI_Py_UNICODE_NARROW */
    unistr_KIND(kind, unistr->str, unichar_t, unilen);

    if ((kind == PyUnicode_1BYTE_KIND &&
	 sizeof(Py_UCS1) == sizeof(unichar_t)) ||
	(kind == PyUnicode_2BYTE_KIND &&
	 sizeof(Py_UCS2) == sizeof(unichar_t)) ||
	(kind == PyUnicode_4BYTE_KIND &&
	 sizeof(Py_UCS4) == sizeof(unichar_t)))
	ret = PyUnicode_FromKindAndData(kind, unistr->str, unilen);
    else {
	if (kind == PyUnicode_1BYTE_KIND) {
	    if ((ucs = PyMem_Malloc(sizeof(Py_UCS1) * unilen)) == NULL)
		return NULL;
	    for (i = 0; i < unilen; i++)
		((Py_UCS1 *) ucs)[i] = (Py_UCS1) unistr->str[i];
	} else if (kind == PyUnicode_2BYTE_KIND) {
	    if ((ucs = PyMem_Malloc(sizeof(Py_UCS2) * unilen)) == NULL)
		return NULL;
	    for (i = 0; i < unilen; i++)
		((Py_UCS2 *) ucs)[i] = (Py_UCS2) unistr->str[i];
	} else if (kind == PyUnicode_4BYTE_KIND) {
	    if ((ucs = PyMem_Malloc(sizeof(Py_UCS4) * unilen)) == NULL)
		return NULL;
	    for (i = 0; i < unilen; i++)
		((Py_UCS4 *) ucs)[i] = (Py_UCS4) unistr->str[i];
	} else {
	    PyErr_SetString(PyExc_SystemError, "invalid kind.");
	    return NULL;
	}
	ret = PyUnicode_FromKindAndData(kind, ucs, unilen);
	PyMem_Free(ucs);
    }
#endif				/* OLDAPI_Py_UNICODE_NARROW */

    return ret;
}

/**
 * Convert LineBreakObject to linebreak object.
 */
#define LineBreak_AS_CSTRUCT(pyobj) \
    (((LineBreakObject *)(pyobj))->obj)

#define STASH_DICT(lb) PyTuple_GetItem((lb)->stash, 0)
#define STASH_TYPE(lb) ((PyTypeObject *) PyTuple_GetItem((lb)->stash, 1))
#define STASH_GCSTRTYPE(lb) ((PyTypeObject *) PyTuple_GetItem((lb)->stash, 2))
#define STASH_EXCEPTION(lb) ((PyTypeObject *) PyTuple_GetItem((lb)->stash, 3))
 

linebreak_t *
LineBreak_AsCstruct(PyObject * pyobj)
{
    if (LineBreak_Check(pyobj))
	return LineBreak_AS_CSTRUCT(pyobj);
    PyErr_Format(PyExc_TypeError,
		 "expected LineBreak object, %200s found",
		 Py_TYPE(pyobj)->tp_name);
    return NULL;
}

/**
 * Convert linebreak object to LineBreakObject.
 */
static PyObject *
LineBreak_FromCstruct(PyTypeObject * type, linebreak_t * lb)
{
    PyObject *self;

    if ((self = type->tp_alloc(type, 0)) == NULL)
	return NULL;
    LineBreak_AS_CSTRUCT(self) = lb;
    return self;
}

/**
 * Convert GCStrObject to gcstring object.
 */
#define GCStr_AS_CSTRUCT(pyobj) \
    (((GCStrObject *)(pyobj))->obj)

gcstring_t *
GCStr_AsCstruct(PyObject * pyobj)
{
    if (GCStr_Check(pyobj))
	return GCStr_AS_CSTRUCT(pyobj);
    PyErr_Format(PyExc_TypeError,
		 "expected GCStr object, %200s found",
		 Py_TYPE(pyobj)->tp_name);
    return NULL;
}

/**
 * Convert grapheme cluster string to GCStr object or its subtype.
 */
static PyObject *
GCStr_FromCstruct(PyTypeObject * type, gcstring_t * gcstr)
{
    PyObject *self;

    if ((self = type->tp_alloc(type, 0)) == NULL)
	return NULL;
    GCStr_AS_CSTRUCT(self) = gcstr;
    return self;
}

/**
 * Convert Python object, Unicode string or GCStrObject to
 * grapheme cluster string.
 * If error occurred, exception will be raised and NULL will be returned.
 * @note if pyobj was GCStrObject, returned object will be original
 * object (not a copy of it).  Otherwise, _new_ object will be returned.
 */

static gcstring_t *
genericstr_ToCstruct(PyObject * pyobj, linebreak_t * lb)
{
    unistr_t unistr = { NULL, 0 };
    gcstring_t *gcstr;

    if (pyobj == NULL)
	return NULL;
    if (GCStr_Check(pyobj))
	return GCStr_AS_CSTRUCT(pyobj);
    if (unicode_ToCstruct(&unistr, pyobj) == NULL)
	return NULL;
    if ((gcstr = gcstring_new(&unistr, lb)) == NULL) {
	PyErr_SetFromErrno(PyExc_RuntimeError);

	free(unistr.str);
	return NULL;
    }
    return gcstr;
}

/**
 * Convert Python object, Byte string, Unicode string or GCStrObject to 
 * NULL-termineted string.
 * If error occurred, exception will be raised and NULL will be returned.
 * @note string buffer must be free()'ed by caller.
 */

static char *
genericstr_ToString(PyObject * pyobj)
{
    PyObject *pystr;
    char *ret;

    if (pyobj == NULL)
	return NULL;
    else if (PyBytes_Check(pyobj)) {
	if ((ret = strdup(PyBytes_AsString(pyobj))) == NULL) {
	    PyErr_SetFromErrno(PyExc_RuntimeError);
	    return NULL;
	}
    } else if (PyUnicode_Check(pyobj)) {
	if ((pystr = PyUnicode_AsEncodedString(pyobj, NULL, NULL)) == NULL)
	    return NULL;
	if ((ret = strdup(PyBytes_AsString(pystr))) == NULL) {
	    PyErr_SetFromErrno(PyExc_RuntimeError);

	    Py_DECREF(pystr);
	    return NULL;
	}
	Py_DECREF(pystr);
    } else {
	if ((pyobj = PyObject_Unicode(pyobj)) == NULL)
	    return NULL;
	if ((pystr = PyUnicode_AsEncodedString(pyobj, NULL, NULL)) == NULL) {
	    Py_DECREF(pyobj);
	    return NULL;
	}
	Py_DECREF(pyobj);
	if ((ret = strdup(PyBytes_AsString(pystr))) == NULL) {
	    PyErr_SetFromErrno(PyExc_RuntimeError);

	    Py_DECREF(pystr);
	    return NULL;
	}
	Py_DECREF(pystr);
    }
    return ret;
}

/**
 * Convert Python object, Integer, Byte string, Unicode string or
 * GCStrObject to UCS scalar value.
 * If error occurred, exception will be raised and -1 will be returned.
 */

static unichar_t
strOrInt_ToUCS(PyObject *pyobj)
{
    PyObject *pystr;
    unichar_t c;
    int kind;

    if (PyInt_Check(pyobj))
	c = (unichar_t) PyInt_AsLong(pyobj);
    else if (PyLong_Check(pyobj))
	c = (unichar_t) PyLong_AsLong(pyobj);
    else {
	if (PyUnicode_Check(pyobj))
	    pystr = pyobj;
	else if ((pystr = PyObject_Unicode(pyobj)) == NULL)
	    return (unichar_t)(-1);

	if (PyUnicode_READY(pystr) != 0) {
	    if (! PyUnicode_Check(pyobj)) {
		Py_DECREF(pystr);
	    }
	    return (unichar_t)(-1);
	}
	if (PyUnicode_GET_LENGTH(pystr) == 0) {
	    PyErr_SetString(PyExc_ValueError,
			    "empty string must not be a key");

	    if (! PyUnicode_Check(pyobj)) {
		Py_DECREF(pystr);
	    }
	    return (unichar_t)(-1);
	}
	kind = PyUnicode_KIND(pystr);
	if (kind == PyUnicode_1BYTE_KIND)
	    c = (unichar_t) *((Py_UCS1 *) PyUnicode_DATA(pystr));
	else if (kind == PyUnicode_2BYTE_KIND)
	    c = (unichar_t) *((Py_UCS2 *) PyUnicode_DATA(pystr));
	else if (kind == PyUnicode_4BYTE_KIND)
	    c = (unichar_t) *((Py_UCS4 *) PyUnicode_DATA(pystr));
	else {
	    PyErr_SetString(PyExc_SystemError, "invalid kind.");

	    if (! PyUnicode_Check(pyobj)) {
		Py_DECREF(pystr);
	    }
	    return (unichar_t)(-1);
	}
#ifdef OLDAPI_Py_UNICODE_NARROW
	/* FIXME: Add surrogate pair support. */
#endif				/* OLDAPI_Py_UNICODE_NARROW */

	if (! PyUnicode_Check(pyobj)) {
	    Py_DECREF(pystr);
	}
    }
    return c;
}

/***
 *** Other utilities
 ***/

/*
 * Do regex match once then returns offset and length.
 */
static void
do_re_search_once(PyObject * rx, unistr_t * str, unistr_t * text)
{
    PyObject *strobj, *matchobj, *func_search, *args, *pyobj;
    Py_ssize_t pos, endpos, start, end;
#ifdef OLDAPI_Py_UNICODE_NARROW
    size_t i;
#endif				/* OLDAPI_Py_UNICODE_NARROW */

#ifdef OLDAPI_Py_UNICODE_NARROW
    start = str->str - text->str;
    end = start + str->len;
    for (i = 0, pos = 0; i < start; i++, pos++)
	if (0x10000 <= text->str[i])
	    pos++;
    for (endpos = pos; i < end; i++, endpos++)
	if (0x10000 <= text->str[i])
	    endpos++;
#else				/* OLDAPI_Py_UNICODE_NARROW */
    pos = str->str - text->str;
    endpos = pos + str->len;
#endif				/* OLDAPI_Py_UNICODE_NARROW */

    if ((strobj = unicode_FromCstruct(text)) == NULL) {
	str->str = NULL;
	return;
    }
    if ((func_search = PyObject_GetAttrString(rx, "search")) == NULL) {
	Py_DECREF(strobj);
	str->str = NULL;
	return;
    }
    if (!PyCallable_Check(func_search)) {
	PyErr_SetString(PyExc_ValueError, "object is not callable");

	Py_DECREF(strobj);
	Py_DECREF(func_search);
	str->str = NULL;
	return;
    }
    if ((args = Py_BuildValue("(O" ARG_FORMAT_SSIZE_T ARG_FORMAT_SSIZE_T ")",
			      strobj, pos, endpos)) == NULL) {
	Py_DECREF(func_search);
	return;
    }
    matchobj = PyObject_CallObject(func_search, args);
    Py_DECREF(args);
    Py_DECREF(func_search);
    if (matchobj == NULL) {
	str->str = NULL;
	return;
    }

    if (matchobj != Py_None) {
	if ((pyobj = PyObject_CallMethod(matchobj, "start", NULL)) == NULL) {
	    Py_DECREF(matchobj);
	    str->str = NULL;
	    return;
	}
	start = PyLong_AsLong(pyobj);
	Py_DECREF(pyobj);

	if ((pyobj = PyObject_CallMethod(matchobj, "end", NULL)) == NULL) {
	    Py_DECREF(matchobj);
	    str->str = NULL;
	    return;
	}
	end = PyLong_AsLong(pyobj);
	Py_DECREF(pyobj);

#ifdef OLDAPI_Py_UNICODE_NARROW
	for (i = 0, pos = 0; i < start; i++, pos++)
	    if (0x10000 <= text->str[pos])
		i++;
	for (endpos = pos; i < end; i++, endpos++)
	    if (0x10000 <= text->str[endpos])
		i++;
	str->str = text->str + pos;
	str->len = endpos - pos;
#else				/* OLDAPI_Py_UNICODE_NARROW */
	str->str = text->str + start;
	str->len = end - start;
#endif				/* OLDAPI_Py_UNICODE_NARROW */
    } else
	str->str = NULL;
    Py_DECREF(matchobj);
}

/***
 *** Callbacks for linebreak library.  For more details see Sombok
 *** library documentations.
 ***/

/*
 * Increment/decrement reference count
 */
static void
ref_func(void * obj, int datatype, int d)
{
    if (0 < d) {
	Py_INCREF((PyObject *)obj);
    } else if (d < 0) {
	Py_DECREF((PyObject *)obj);
    }
}

/*
 * Call preprocessing function
 * @note Python callback may return list of broken text or single text.
 */
static gcstring_t *
prep_func(linebreak_t * lb, void *data, unistr_t * str, unistr_t * text)
{
    PyObject *rx = NULL, *func = NULL, *pyret, *pyobj, *args;
    int count, i, j;
    gcstring_t *gcstr, *ret;

    /* Pass I */

    if (text != NULL) {
	if ((rx = PyTuple_GetItem(data, 0)) == NULL) {
	    lb->errnum = EINVAL;
	    return NULL;
	}
	do_re_search_once(rx, str, text);
	return NULL;
    }

    /* Pass II */

    if ((func = PyTuple_GetItem(data, 1)) == NULL) {
	if ((ret = gcstring_newcopy(str, lb)) == NULL) {
	    lb->errnum = errno ? errno : ENOMEM;
	    return NULL;
	}
	return ret;
    }

    linebreak_incref(lb);	/* prevent destruction */
    if ((args = Py_BuildValue("(OO)",
			      LineBreak_FromCstruct(STASH_TYPE(lb), lb),
			      unicode_FromCstruct(str))) == NULL) {
	lb->errnum = LINEBREAK_EEXTN;
	return NULL;
    }
    pyret = PyObject_CallObject(func, args);
    Py_DECREF(args);
    if (PyErr_Occurred()) {
	if (!lb->errnum)
	    lb->errnum = LINEBREAK_EEXTN;
	return NULL;
    }
    if (pyret == NULL)
	return NULL;

    if (PyList_Check(pyret)) {
	if ((ret = gcstring_new(NULL, lb)) == NULL)
	    return (lb->errnum = errno ? errno : ENOMEM), NULL;

	count = PyList_Size(pyret);
	for (i = 0; i < count; i++) {
	    pyobj = PyList_GetItem(pyret, i);	/* borrowed ref. */
	    if (pyobj == Py_None)
		continue;
	    else if (GCStr_Check(pyobj))
		gcstr = gcstring_copy(GCStr_AS_CSTRUCT(pyobj));
	    else
		gcstr = genericstr_ToCstruct(pyobj, lb);
	    if (gcstr == NULL) {
		if (!lb->errnum)
		    lb->errnum = errno ? errno : LINEBREAK_EEXTN;

		Py_DECREF(pyret);
		return NULL;
	    }

	    for (j = 0; j < gcstr->gclen; j++) {
		if (gcstr->gcstr[j].flag &
		    (LINEBREAK_FLAG_ALLOW_BEFORE |
		     LINEBREAK_FLAG_PROHIBIT_BEFORE))
		    continue;
		if (0 < i && j == 0)
		    gcstr->gcstr[j].flag |= LINEBREAK_FLAG_ALLOW_BEFORE;
		else if (0 < j)
		    gcstr->gcstr[j].flag |= LINEBREAK_FLAG_PROHIBIT_BEFORE;
	    }

	    gcstring_append(ret, gcstr);
	    gcstring_destroy(gcstr);
	}
	Py_DECREF(pyret);
	return ret;
    }

    if (pyret == Py_None) {
	Py_DECREF(pyret);
	return NULL;
    }

    if (GCStr_Check(pyret))
	ret = gcstring_copy(GCStr_AS_CSTRUCT(pyret));
    else
	ret = genericstr_ToCstruct(pyret, lb);
    if (ret == NULL) {
	if (!lb->errnum)
	    lb->errnum = LINEBREAK_EEXTN;

	Py_DECREF(pyret);
	return NULL;
    }
    Py_DECREF(pyret);

    for (j = 0; j < ret->gclen; j++) {
	if (ret->gcstr[j].flag &
	    (LINEBREAK_FLAG_ALLOW_BEFORE | LINEBREAK_FLAG_PROHIBIT_BEFORE))
	    continue;
	if (0 < j)
	    ret->gcstr[j].flag |= LINEBREAK_FLAG_PROHIBIT_BEFORE;
    }

    return ret;
}

/*
 * Call format function
 */
static char *linebreak_states[] = {
    NULL, "sot", "sop", "sol", "", "eol", "eop", "eot", NULL
};
static gcstring_t *
format_func(linebreak_t * lb, linebreak_state_t action, gcstring_t * str)
{
    PyObject *func, *args, *pyret;
    char *actionstr;
    gcstring_t *gcstr;

    func = (PyObject *) lb->format_data;
    if (func == NULL)
	return NULL;

    if (action <= LINEBREAK_STATE_NONE || LINEBREAK_STATE_MAX <= action)
	return NULL;
    actionstr = linebreak_states[(size_t) action];

    linebreak_incref(lb);	/* prevent destruction */
    if ((args = Py_BuildValue("(OsO)",
			      LineBreak_FromCstruct(STASH_TYPE(lb), lb),
			      actionstr,
			      GCStr_FromCstruct(STASH_GCSTRTYPE(lb),
						gcstring_copy(str))))
	== NULL) {
	lb->errnum = LINEBREAK_EEXTN;
	return NULL;
    }
    pyret = PyObject_CallObject(func, args);
    Py_DECREF(args);

    if (PyErr_Occurred()) {
	if (!lb->errnum)
	    lb->errnum = LINEBREAK_EEXTN;
	if (pyret != NULL) {
	    Py_DECREF(pyret);
	}
	return NULL;
    }
    if (pyret == NULL)
	return NULL;

    if (pyret == Py_None) {
	Py_DECREF(pyret);
	return NULL;
    }

    if (GCStr_Check(pyret))
	gcstr = gcstring_copy(GCStr_AS_CSTRUCT(pyret));
    else if ((gcstr = genericstr_ToCstruct(pyret, lb)) == NULL) {
	if (!lb->errnum)
	    lb->errnum = errno ? errno : ENOMEM;
	PyErr_SetFromErrno(PyExc_RuntimeError);
	Py_DECREF(pyret);
	return NULL;
    }
    Py_DECREF(pyret);
    return gcstr;
}

/*
 * Call sizing function
 */
static double
sizing_func(linebreak_t * lb, double len,
	    gcstring_t * pre, gcstring_t * spc, gcstring_t * str)
{
    PyObject *func, *args, *pyret;
    PyTypeObject *gcstr_type;
    double ret;

    func = (PyObject *) lb->sizing_data;
    if (func == NULL)
	return -1.0;

    gcstr_type = STASH_GCSTRTYPE(lb);
    linebreak_incref(lb);	/* prevent destruction. */
    if ((args = Py_BuildValue("(OdOOO)",
			      LineBreak_FromCstruct(STASH_TYPE(lb), lb),
			      len,
			      GCStr_FromCstruct(gcstr_type,
						gcstring_copy(pre)),
			      GCStr_FromCstruct(gcstr_type,
						gcstring_copy(spc)),
			      GCStr_FromCstruct(gcstr_type,
						gcstring_copy(str))))
	== NULL) {
	lb->errnum = LINEBREAK_EEXTN;
	return -1.0;
    }
    pyret = PyObject_CallObject(func, args);
    Py_DECREF(args);

    if (PyErr_Occurred()) {
	if (!lb->errnum)
	    lb->errnum = LINEBREAK_EEXTN;
	if (pyret != NULL) {
	    Py_DECREF(pyret);
	}
	return -1.0;
    }

    ret = PyFloat_AsDouble(pyret);
    if (PyErr_Occurred()) {
	if (!lb->errnum)
	    lb->errnum = LINEBREAK_EEXTN;
	Py_DECREF(pyret);
	return -1.0;
    }
    Py_DECREF(pyret);

    return ret;
}

/*
 * Call urgent breaking function
 */
static gcstring_t *
urgent_func(linebreak_t * lb, gcstring_t * str)
{
    PyObject *func, *args, *pyret, *pyobj;
    size_t count, i;
    gcstring_t *gcstr, *ret;

    func = (PyObject *) lb->urgent_data;
    if (func == NULL)
	return NULL;

    linebreak_incref(lb);	/* prevent destruction. */
    if ((args = Py_BuildValue("(OO)",
			      LineBreak_FromCstruct(STASH_TYPE(lb), lb),
			      GCStr_FromCstruct(STASH_GCSTRTYPE(lb),
						gcstring_copy(str))))
	== NULL) {
	lb->errnum = LINEBREAK_EEXTN;
	return NULL;
    }
    pyret = PyObject_CallObject(func, args);
    Py_DECREF(args);

    if (PyErr_Occurred()) {
	if (!lb->errnum)
	    lb->errnum = LINEBREAK_EEXTN;
	if (pyret != NULL) {
	    Py_DECREF(pyret);
	}
	return NULL;
    }
    if (pyret == NULL)
	return NULL;

    if (pyret == Py_None) {
	Py_DECREF(pyret);
	return NULL;
    }

    if (!PyList_Check(pyret)) {
	if (GCStr_Check(pyret))
	    ret = gcstring_copy(GCStr_AS_CSTRUCT(pyret));
	else
	    ret = genericstr_ToCstruct(pyret, lb);
	Py_DECREF(pyret);
	return ret;
    }

    ret = gcstring_new(NULL, lb);
    count = PyList_Size(pyret);
    for (i = 0; i < count; i++) {
	pyobj = PyList_GetItem(pyret, i);	/* borrowed ref. */
	if (pyobj == Py_None)
	    continue;
	else if (GCStr_Check(pyobj))
	    gcstr = gcstring_copy(GCStr_AS_CSTRUCT(pyobj));
	else
	    gcstr = genericstr_ToCstruct(pyobj, lb);
	if (gcstr == NULL) {
	    if (!lb->errnum)
		lb->errnum = errno ? errno : LINEBREAK_EEXTN;

	    Py_DECREF(pyret);
	    return NULL;
	}

	if (gcstr->gclen)
	    gcstr->gcstr[0].flag = LINEBREAK_FLAG_ALLOW_BEFORE;
	gcstring_append(ret, gcstr);
	gcstring_destroy(gcstr);
    }

    Py_DECREF(pyret);
    return ret;
}

/*** 
 *** Python module definitions
 ***/

/**
 ** Exceptions
 **/

static PyObject *LineBreakException;

/**
 ** LineBreak class
 **/

/*
 * Constructor & Destructor
 */

static void
LineBreak_dealloc(LineBreakObject * self)
{
    TDictObject * tdict;

    /* remove linkage to tailoring dictionaries */
    for (tdict = self->tdict; tdict != NULL; tdict = tdict->next)
	tdict->lb = NULL;

    linebreak_destroy(LineBreak_AS_CSTRUCT(self));
    Py_TYPE(self)->tp_free(self);
}

static PyObject *
LineBreak_subtype_new(PyTypeObject *, PyObject *, PyObject *);

static PyObject *
LineBreak_new(PyTypeObject * type, PyObject * args, PyObject * kwds)
{
    LineBreakObject *self;
    PyObject *stash;

    if (type != &LineBreak_Type)
        return LineBreak_subtype_new(type, args, kwds);

    if ((self = (LineBreakObject *) type->tp_alloc(type, 0)) == NULL)
	return NULL;

    if ((self->obj = linebreak_new(ref_func)) == NULL) {
	PyErr_SetFromErrno(PyExc_RuntimeError);
	Py_DECREF(self);
	return NULL;
    }

    /*
     * stash is a tuple of
     * (<dict>, <LineBreak type>, <GCStr type>, <Exception type>).
     * <dict> is used by mapping methods.  Others are type of Python 
     * objects used in the callback functions.
     */
    Py_INCREF(&LineBreak_Type);
    Py_INCREF(&GCStr_Type);
    Py_INCREF(LineBreakException);
    if ((stash = Py_BuildValue("({}OOO)",
			       (PyObject *)&LineBreak_Type,
			       (PyObject *)&GCStr_Type,
			       LineBreakException)) == NULL) {
	Py_DECREF(self);
	return NULL;
    }

    linebreak_set_stash(self->obj, stash);
    Py_DECREF(stash);		/* fixup */

    /* tailoring dictionary */
    self->tdict = NULL;

    return (PyObject *) self;
}

static PyObject *
LineBreak_subtype_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *tmp, *newobj;

    assert(PyType_IsSubtype(type, &LineBreak_Type));
    if ((tmp = LineBreak_new(&LineBreak_Type, args, kwds)) == NULL)
	return NULL;
    assert(LineBreak_CheckExact(tmp));
    if ((newobj = type->tp_alloc(type, 0)) == NULL) {
	Py_DECREF(tmp);
	return NULL;
    }
    LineBreak_AS_CSTRUCT(newobj) = LineBreak_AS_CSTRUCT(tmp);
    LineBreak_AS_CSTRUCT(tmp) = NULL;
    Py_DECREF(tmp);
    return newobj;
}

static PyGetSetDef LineBreak_getseters[];

static int
LineBreak_init(LineBreakObject * self, PyObject * args, PyObject * kwds)
{
    PyObject *key, *value;
    Py_ssize_t pos;
    PyGetSetDef *getset;
    char *keystr;

    if (kwds == NULL)
	return 0;

    pos = 0;
    while (PyDict_Next(kwds, &pos, &key, &value)) {
	if ((keystr = genericstr_ToString(key)) == NULL)
	    return -1;
	for (getset = LineBreak_getseters; getset->name != NULL; getset++) {
	    if (getset->set == NULL)
		continue;
	    if (strcmp(getset->name, keystr) != 0)
		continue;
	    if ((getset->set) ((PyObject *) self, value, NULL) != 0) {
		free(keystr);
		return -1;
	    }
	    break;
	}
	if (getset->name == NULL) {
	    PyErr_Format(PyExc_ValueError, "invalid argument '%s'", keystr);
	    free(keystr);
	    return -1;
	}
	free(keystr);
    }
    return 0;
}

/*
 * Attribute methods
 */

static PyObject * TDict_FromLineBreak(PyObject *, tdicttype);

#define _get_Boolean(name, bit) \
    static PyObject * \
    LineBreak_get_##name(PyObject *self) \
    { \
        PyObject *val; \
    \
        val = (LineBreak_AS_CSTRUCT(self)->options & bit) ? \
              Py_True : Py_False; \
        Py_INCREF(val); \
        return val; \
    }

_get_Boolean(break_indent, LINEBREAK_OPTION_BREAK_INDENT)

static PyObject *
LineBreak_get_charmax(PyObject * self)
{
    return PyInt_FromSsize_t(LineBreak_AS_CSTRUCT(self)->charmax);
}

static PyObject *
LineBreak_get_width(PyObject * self)
{
    return PyFloat_FromDouble(LineBreak_AS_CSTRUCT(self)->colmax);
}

static PyObject *
LineBreak_get_minwidth(PyObject * self)
{
    return PyFloat_FromDouble(LineBreak_AS_CSTRUCT(self)->colmin);
}

_get_Boolean(complex_breaking, LINEBREAK_OPTION_COMPLEX_BREAKING)

_get_Boolean(eastasian_context, LINEBREAK_OPTION_EASTASIAN_CONTEXT)

static PyObject *
LineBreak_get_eaw(PyObject * self)
{
    return TDict_FromLineBreak(self, TDICT_EAW);
}

static PyObject *
LineBreak_get_format(PyObject * self)
{
    linebreak_t *lb = LineBreak_AS_CSTRUCT(self);
    PyObject *val;

    if (lb->format_func == NULL) {
	Py_RETURN_NONE;
    } else if (lb->format_func == linebreak_format_NEWLINE)
	val = TEXTSEG_NEWLINE;
    else if (lb->format_func == linebreak_format_SIMPLE)
	val = TEXTSEG_SIMPLE;
    else if (lb->format_func == linebreak_format_TRIM)
	val = TEXTSEG_TRIM;
    else if (lb->format_func == format_func)
	val = (PyObject *) lb->format_data;
    else {
	PyErr_Format(PyExc_RuntimeError, "internal error");
	return NULL;
    }
    Py_INCREF(val);
    return val;
}

_get_Boolean(hangul_as_al, LINEBREAK_OPTION_HANGUL_AS_AL)

static PyObject *
LineBreak_get_lbc(PyObject * self)
{
    return TDict_FromLineBreak(self, TDICT_LBC);
}

_get_Boolean(legacy_cm, LINEBREAK_OPTION_LEGACY_CM)

static PyObject *
LineBreak_get_newline(PyObject * self)
{
    return unicode_FromCstruct(&(LineBreak_AS_CSTRUCT(self)->newline));
}

static PyObject *
LineBreak_get_prep(PyObject * self)
{
    linebreak_t *lb = LineBreak_AS_CSTRUCT(self);
    PyObject *val;

    if (lb->prep_func == NULL || lb->prep_func[0] == NULL) {
	val = Py_None;
	Py_INCREF(val);
    } else {
	size_t i;
	PyObject *v;
	val = PyList_New(0);
	for (i = 0; lb->prep_func[i] != NULL; i++) {
	    if (lb->prep_func[i] == linebreak_prep_URIBREAK) {
		if (lb->prep_data == NULL || lb->prep_data[i] == NULL)
		    v = TEXTSEG_NONBREAKURI;
		else
		    v = TEXTSEG_BREAKURI;
	    } else if (lb->prep_data == NULL || lb->prep_data[i] == NULL) {
		v = Py_None;
	    } else {
		v = lb->prep_data[i];
	    }
	    /* Py_INCREF(v) */
	    PyList_Append(val, v);
	}
    }
    return val;
}

static PyObject *
LineBreak_get_sizing(PyObject * self)
{
    linebreak_t *lb = LineBreak_AS_CSTRUCT(self);
    PyObject *val;

    if (lb->sizing_func == NULL) {
	Py_RETURN_NONE;
    } else if (lb->sizing_func == linebreak_sizing_UAX11)
	val = TEXTSEG_UAX11;
    else if (lb->sizing_func == sizing_func)
	val = (PyObject *) lb->sizing_data;
    else {
	PyErr_Format(PyExc_RuntimeError, "internal error");
	return NULL;
    }
    Py_INCREF(val);

    return val;
}

static PyObject *
LineBreak_get_urgent(PyObject * self)
{
    linebreak_t *lb = LineBreak_AS_CSTRUCT(self);
    PyObject *val;

    if (lb->urgent_func == NULL) {
	Py_RETURN_NONE;
    } else if (lb->urgent_func == linebreak_urgent_ABORT)
	val = TEXTSEG_RAISE;
    else if (lb->urgent_func == linebreak_urgent_FORCE)
	val = TEXTSEG_FORCE;
    else if (lb->urgent_func == urgent_func) {
	val = (PyObject *) lb->urgent_data;
    } else {
	PyErr_Format(PyExc_RuntimeError, "internal error");
	return NULL;
    }

    Py_INCREF(val);
    return val;
}

_get_Boolean(virama_as_joiner, LINEBREAK_OPTION_VIRAMA_AS_JOINER)

#define _set_Boolean(name, bit) \
    static int \
    LineBreak_set_##name(PyObject *self, PyObject *arg, void *closure) \
    { \
        linebreak_t *lb = LineBreak_AS_CSTRUCT(self); \
        long ival; \
    \
        if (arg == NULL) { \
	    PyErr_Format(PyExc_NotImplementedError, \
		         "Can not delete attribute"); \
	    return -1; \
        } \
    \
        ival = PyInt_AsLong(arg); \
        if (PyErr_Occurred()) \
	    return -1; \
        if (ival) \
	    lb->options |= bit; \
        else \
	    lb->options &= ~bit; \
	return 0; \
    }

static int tdict_update(PyObject *, PyObject *, int);

static int
LineBreak_set_linebreakType(PyObject * self, PyObject * value, void *closure)
{
    if (! PyType_Check(value)) {
	PyErr_Format(PyExc_ValueError, "expected type object, %200s found",
		     Py_TYPE(value)->tp_name);
	return -1;
    }
    if (! PyType_IsSubtype((PyTypeObject *)value, &LineBreak_Type)) {
	PyErr_Format(PyExc_ValueError, "expected LineBreak type, %200s found",
		     ((PyTypeObject *)value)->tp_name);
	return -1;
    }
    Py_INCREF(value);	/* ref. to be stolen */
    if (PyTuple_SetItem(LineBreak_AS_CSTRUCT(self)->stash, 1, value) != 0)
	return -1;
    return 0;
}

static int
LineBreak_set_gcstrType(PyObject * self, PyObject * value, void *closure)
{
    if (! PyType_Check(value)) {
	PyErr_Format(PyExc_ValueError, "expected type object, %200s found",
		     Py_TYPE(value)->tp_name);
	return -1;
    }
    if (! PyType_IsSubtype((PyTypeObject *)value, &GCStr_Type)) {
	PyErr_Format(PyExc_ValueError, "expected GCStr type, %200s found",
		     ((PyTypeObject *)value)->tp_name);
	return -1;
    }
    Py_INCREF(value);	/* ref. to be stolen */
    if (PyTuple_SetItem(LineBreak_AS_CSTRUCT(self)->stash, 2, value) != 0)
	return -1;
    return 0;
}

static int
LineBreak_set_exceptionType(PyObject * self, PyObject * value, void *closure)
{
    if (! PyType_Check(value)) {
	PyErr_Format(PyExc_ValueError, "expected type object, %200s found",
		     Py_TYPE(value)->tp_name);
	return -1;
    }
    if (! PyType_IsSubtype((PyTypeObject *)value,
			   (PyTypeObject *)PyExc_Exception)) {
	PyErr_Format(PyExc_ValueError, "expected Exception type, %200s found",
		     ((PyTypeObject *)value)->tp_name);
	return -1;
    }
    Py_INCREF(value);	/* ref. to be stolen */
    if (PyTuple_SetItem(LineBreak_AS_CSTRUCT(self)->stash, 3, value) != 0)
	return -1;
    return 0;
}

_set_Boolean(break_indent, LINEBREAK_OPTION_BREAK_INDENT)

static int
LineBreak_set_charmax(PyObject * self, PyObject * value, void *closure)
{
    long ival;

    if (value == NULL) {
	PyErr_Format(PyExc_NotImplementedError,
		     "Can not delete attribute");
	return -1;
    }
    if (PyInt_Check(value))
	ival = (long) PyInt_AsLong(value);
    else if (PyLong_Check(value))
	ival = PyInt_AsLong(value);
    else {
	PyErr_Format(PyExc_TypeError,
		     "attribute must be non-negative integer, not %200s",
		     Py_TYPE(value)->tp_name);
	return -1;
    }
    if (ival < 0) {
	PyErr_Format(PyExc_ValueError,
		     "attribute must be non-negative integer, not %ld",
		     ival);
	return -1;
    }
    LineBreak_AS_CSTRUCT(self)->charmax = ival;
    return 0;
}

static int
LineBreak_set_width(PyObject * self, PyObject * value, void *closure)
{
    double dval;

    if (value == NULL) {
	PyErr_Format(PyExc_NotImplementedError,
		     "Can not delete attribute");
	return -1;
    }
    if (PyInt_Check(value))
	dval = (double) PyInt_AsLong(value);
    else if (PyLong_Check(value))
	dval = (double) PyInt_AsLong(value);
    else if (PyFloat_Check(value))
	dval = PyFloat_AsDouble(value);
    else {
	PyErr_Format(PyExc_TypeError,
		     "attribute must be non-negative real number, not %200s",
		     Py_TYPE(value)->tp_name);
	return -1;
    }
    if (dval < 0.0) {
	PyErr_Format(PyExc_ValueError,
		     "attribute must be non-negative real number, not %f",
		     dval);
	return -1;
    }
    LineBreak_AS_CSTRUCT(self)->colmax = dval;
    return 0;
}

static int
LineBreak_set_minwidth(PyObject * self, PyObject * value, void *closure)
{
    double dval;

    if (value == NULL) {
	PyErr_Format(PyExc_NotImplementedError,
		     "Can not delete attribute");
	return -1;
    }
    if (PyInt_Check(value))
	dval = (double) PyInt_AsLong(value);
    else if (PyLong_Check(value))
	dval = (double) PyInt_AsLong(value);
    else if (PyFloat_Check(value))
	dval = PyFloat_AsDouble(value);
    else {
	PyErr_Format(PyExc_TypeError,
		     "attribute must be non-negative real number, not %200s",
		     Py_TYPE(value)->tp_name);
	return -1;
    }
    if (dval < 0.0) {
	PyErr_Format(PyExc_ValueError,
		     "attribute must be non-negative real number, not %f",
		     dval);
	return -1;
    }
    LineBreak_AS_CSTRUCT(self)->colmin = dval;
    return 0;
}

_set_Boolean(complex_breaking, LINEBREAK_OPTION_COMPLEX_BREAKING)

_set_Boolean(eastasian_context, LINEBREAK_OPTION_EASTASIAN_CONTEXT)

static int
LineBreak_set_eaw(PyObject * self, PyObject * value, void *closure)
{
    PyObject *tdict;
    int result = 0;

    if (value == NULL) {
	PyErr_SetString(PyExc_AttributeError, "cannot remove attribute");
	return -1;
    }
    if ((tdict = TDict_FromLineBreak(self, TDICT_EAW)) == NULL)
	return -1;
    result = tdict_update(tdict, value, 1);
    Py_DECREF(tdict);
    return result;
}

static int
LineBreak_set_format(PyObject * self, PyObject * value, void *closure)
{
    linebreak_t *lb = LineBreak_AS_CSTRUCT(self);

    if (value == NULL)
	linebreak_set_format(lb, NULL, NULL);
    else if (value == Py_None)
	linebreak_set_format(lb, NULL, NULL);
    else if (PyString_Check(value) || PyUnicode_Check(value)) {
	char *str;
	if ((str = genericstr_ToString(value)) == NULL)
	    return -1;

	if (strcasecmp(str, "SIMPLE") == 0)
	    linebreak_set_format(lb, linebreak_format_SIMPLE, NULL);
	else if (strcasecmp(str, "NEWLINE") == 0)
	    linebreak_set_format(lb, linebreak_format_NEWLINE, NULL);
	else if (strcasecmp(str, "TRIM") == 0)
	    linebreak_set_format(lb, linebreak_format_TRIM, NULL);
	else {
	    PyErr_Format(PyExc_ValueError,
			 "unknown attribute value, %200s", str);

	    free(str);
	    return -1;
	}
	free(str);
    } else if (PyFunction_Check(value))
	linebreak_set_format(lb, format_func, (void *) value);
    else {
	PyErr_Format(PyExc_ValueError,
		     "attribute must be list, not %200s",
		     Py_TYPE(value)->tp_name);
	return -1;
    }
    return 0;
}

_set_Boolean(hangul_as_al, LINEBREAK_OPTION_HANGUL_AS_AL)

static int
LineBreak_set_lbc(PyObject * self, PyObject * value, void *closure)
{
    PyObject *tdict;
    int result = 0;

    if (value == NULL) {
	PyErr_SetString(PyExc_AttributeError, "cannot remove attribute");
	return -1;
    }
    if ((tdict = TDict_FromLineBreak(self, TDICT_LBC)) == NULL)
        return -1;
    result = tdict_update(tdict, value, 1);
    Py_DECREF(tdict);
    return result;
}

_set_Boolean(legacy_cm, LINEBREAK_OPTION_LEGACY_CM)

static int
LineBreak_set_newline(PyObject * self, PyObject * value, void *closure)
{
    linebreak_t *lb = LineBreak_AS_CSTRUCT(self);
    unistr_t unistr = { NULL, 0 };

    if (value == NULL)
	linebreak_set_newline(lb, &unistr);
    else if (value == Py_None)
	linebreak_set_newline(lb, &unistr);
    else {
	if (unicode_ToCstruct(&unistr, value) == NULL)
	    return -1;
	linebreak_set_newline(lb, &unistr);
	free(unistr.str);
    }
    return 0;
}

static int
LineBreak_set_prep(PyObject * self, PyObject * value, void *closure)
{
    linebreak_t *lb = LineBreak_AS_CSTRUCT(self);
    Py_ssize_t i, len;
    PyObject *item;
    char *str;

    if (value == NULL)
	linebreak_add_prep(lb, NULL, NULL);
    else if (value == Py_None)
	linebreak_add_prep(lb, NULL, NULL);
    else if (PyList_Check(value)) {
	linebreak_add_prep(lb, NULL, NULL);
	len = PyList_Size(value);
	for (i = 0; i < len; i++) {
	    item = PyList_GetItem(value, i);	/* borrowed ref. */
	    if (PyString_Check(item) || PyUnicode_Check(item)) {
		if ((str = genericstr_ToString(item)) == NULL)
		    break;
		else if (strcasecmp(str, "BREAKURI") == 0)
		    linebreak_add_prep(lb, linebreak_prep_URIBREAK,
				       Py_True);
		else if (strcasecmp(str, "NONBREAKURI") == 0)
		    linebreak_add_prep(lb, linebreak_prep_URIBREAK,
				       NULL);
		else {
		    PyErr_Format(PyExc_ValueError,
				 "unknown attribute value %200s", str);

		    free(str);
		    return -1;
		}
		free(str);
	    } else if (PyTuple_Check(item)) {
		PyObject *re_module, *patt, *flgs, *func_compile, *args;

		if (PyTuple_Size(item) < 2) {
		    PyErr_Format(PyExc_ValueError,
				 "argument size mismatch");
		    return -1;
		}

		patt = PyTuple_GetItem(item, 0);	/* borrowed ref. */
		if (PyString_Check(patt) || PyUnicode_Check(patt)) {
		    re_module = PyImport_ImportModule("re");
		    func_compile = PyObject_GetAttrString(re_module,
							  "compile");
		    Py_INCREF(patt); /* prevent destruction */
		    if (2 < PyTuple_Size(item)) {
			flgs = PyTuple_GetItem(item, 2);	/* borrwed */
			Py_INCREF(flgs);
		    } else
			flgs = PyInt_FromLong(0L);
		    if ((args = Py_BuildValue("(OO)", patt, flgs)) == NULL)
			return -1;
		    patt = PyObject_CallObject(func_compile, args);
		    Py_DECREF(args);

		    if (PyTuple_SetItem(item, 0, patt) != 0)
			return -1;
		}
		linebreak_add_prep(lb, prep_func, item);
	    } else {
		PyErr_Format(PyExc_TypeError,
			     "prep argument must be list of tuples, not %200s",
			     Py_TYPE(item)->tp_name);
		return -1;
	    }
	}
    } else {
	PyErr_Format(PyExc_TypeError,
		     "prep argument must be list of tuples, not %200s",
		     Py_TYPE(value)->tp_name);
	return -1;
    }
    return 0;
}

static int
LineBreak_set_sizing(PyObject * self, PyObject * value, void *closure)
{
    linebreak_t *lb = LineBreak_AS_CSTRUCT(self);

    if (value == NULL)
	linebreak_set_sizing(lb, NULL, NULL);
    if (value == Py_None)
	linebreak_set_sizing(lb, NULL, NULL);
    else if (PyString_Check(value) || PyUnicode_Check(value)) {
	char *str;
	if ((str = genericstr_ToString(value)) == NULL)
	    return -1;

	if (strcasecmp(str, "UAX11") == 0)
	    linebreak_set_sizing(lb, linebreak_sizing_UAX11, NULL);
	else {
	    PyErr_Format(PyExc_ValueError,
			 "unknown attribute value %200s", str);

	    free(str);
	    return -1;
	}
	free(str);
    } else if (PyFunction_Check(value))
	linebreak_set_sizing(lb, sizing_func, (void *) value);
    else {
	PyErr_Format(PyExc_ValueError,
		     "attribute must be function, not %200s",
		     Py_TYPE(value)->tp_name);
	return -1;
    }
    return 0;
}

static int
LineBreak_set_urgent(PyObject * self, PyObject * value, void *closure)
{
    linebreak_t *lb = LineBreak_AS_CSTRUCT(self);

    if (value == NULL)
	linebreak_set_urgent(lb, NULL, NULL);
    else if (value == Py_None)
	linebreak_set_urgent(lb, NULL, NULL);
    else if (PyString_Check(value) || PyUnicode_Check(value)) {
	char *str;

	if ((str = genericstr_ToString(value)) == NULL)
	    return -1;
	else if (strcasecmp(str, "FORCE") == 0)
	    linebreak_set_urgent(lb, linebreak_urgent_FORCE, NULL);
	else if (strcasecmp(str, "RAISE") == 0)
	    linebreak_set_urgent(lb, linebreak_urgent_ABORT, NULL);
	else {
	    PyErr_Format(PyExc_ValueError,
			 "unknown attribute value %200s", str);

	    free(str);
	    return -1;
	}
	free(str);
    } else if (PyFunction_Check(value))
	linebreak_set_urgent(lb, urgent_func, (void *) value);
    else {
	PyErr_Format(PyExc_ValueError,
		     "attribute must be list, not %200s",
		     Py_TYPE(value)->tp_name);
	return -1;
    }
    return 0;
}

_set_Boolean(virama_as_joiner, LINEBREAK_OPTION_VIRAMA_AS_JOINER)

static PyGetSetDef LineBreak_getseters[] = {
    /* undocumented attributes */
    {"linebreakType",
     NULL,
     (setter) LineBreak_set_linebreakType,
     NULL},
    {"gcstrType",
     NULL,
     (setter) LineBreak_set_gcstrType,
     NULL},
    {"exceptionType",
     NULL,
     (setter) LineBreak_set_exceptionType,
     NULL},
    /* instance attributes */
    {"break_indent",
     (getter) LineBreak_get_break_indent,
     (setter) LineBreak_set_break_indent,
     PyDoc_STR("\
Always allows break after SPACEs at beginning of line, \
a.k.a. indent.  [UAX14]_ does not take account of such usage of SPACE.")},
    {"charmax",
     (getter) LineBreak_get_charmax,
     (setter) LineBreak_set_charmax,
     PyDoc_STR("\
Possible maximum number of characters in one line, \
not counting trailing SPACEs and newline sequence.  \
Note that number of characters generally doesn't represent length of line.  \
0 means unlimited.")},
    {"width",
     (getter) LineBreak_get_width,
     (setter) LineBreak_set_width,
     PyDoc_STR("\
Maximum :term:`number of columns` line may include not counting \
trailing spaces and newline sequence.  In other words, recommended maximum \
length of line.")},
    {"minwidth",
     (getter) LineBreak_get_minwidth,
     (setter) LineBreak_set_minwidth,
     PyDoc_STR("\
Minimum number of columns which line broken arbitrarily may \
include, not counting trailing spaces and newline sequences.")},
    {"complex_breaking",
     (getter) LineBreak_get_complex_breaking,
     (setter) LineBreak_set_complex_breaking,
     PyDoc_STR("\
Performs :term:`heuristic breaking<complex breaking>` on South East Asian \
complex context.  \
If word segmentation for South East Asian writing systems is not \
enabled, this does not have any effect.")},
    {"eastasian_context",
     (getter) LineBreak_get_eastasian_context,
     (setter) LineBreak_set_eastasian_context,
     PyDoc_STR("\
Enable East Asian language/region context.  \
If it is true, characters assigned to :term:`line breaking class` AI will \
be treated as :term:`ideographic character`\\ s (ID) and :term:`East_Asian_Width` \
A (ambiguous) will be treated as F (fullwidth).  \
Otherwise, they are treated as :term:`alphabetic character`\\ s (AL) and \
N (neutral), respectively.")},
    {"eaw",
     (getter) LineBreak_get_eaw,
     (setter) LineBreak_set_eaw,
     PyDoc_STR("\
Tailor classification of :term:`East_Asian_Width` property defined by \
[UAX11]_.  \
Value may be a dictionary with its keys are Unicode string or \
UCS scalar and with its values are any of East_Asian_Width properties \
(see documentation of textseg.Consts module).  \
If None is specified, all tailoring assigned before will be canceled.\n\
By default, no tailorings are available.\n\
See also \":ref:`Tailoring Character Properties`\".")},
    {"format",
     (getter) LineBreak_get_format,
     (setter) LineBreak_set_format,
     PyDoc_STR("\
Specify the method to format broken lines.\n\
\n\
``\"SIMPLE\"``\n\
    Just only insert newline at arbitrary breaking positions.\n\
``\"NEWLINE\"``\n\
    Insert or replace newline sequences with that specified by newline \n\
    option, remove SPACEs leading newline sequences or end-of-text.  Then \n\
    append newline at end of text if it does not exist.\n\
``\"TRIM\"``\n\
    Insert newline at arbitrary breaking positions.  Remove SPACEs \n\
    leading newline sequences.\n\
``None``\n\
    Do nothing, even inserting any newlines.\n\
callable object\n\
    See \":ref:`Formatting Lines`\".")},
    {"hangul_as_al",
     (getter) LineBreak_get_hangul_as_al,
     (setter) LineBreak_set_hangul_as_al,
     PyDoc_STR("\
Treat :term:`hangul` syllables and conjoining jamo as \
:term:`alphabetic character`\\ s (AL).")},
    {"lbc",
     (getter) LineBreak_get_lbc,
     (setter) LineBreak_set_lbc,
     PyDoc_STR("\
Tailor classification of line breaking property defined by [UAX14]_.  \
Value may be a dictionary with its keys are Unicode string or \
UCS scalar and its values with any of \
:term:`line breaking classes<line breaking class>` (See Consts module).  \
If ``None`` is specified, all tailoring assigned before will be canceled.\n\
By default, no tailorings are available.\n\
See also \":ref:`Tailoring Character Properties`\".")},
    {"legacy_cm",
     (getter) LineBreak_get_legacy_cm,
     (setter) LineBreak_set_legacy_cm,
     PyDoc_STR("\
Treat combining characters lead by a SPACE as an isolated \
combining character (ID).  As of Unicode 5.0, such use of SPACE is not \
recommended.")},
    {"newline",
     (getter) LineBreak_get_newline,
     (setter) LineBreak_set_newline,
     PyDoc_STR("\
Unicode string to be used for newline sequence.  \
It may be ``None``.")},
    {"prep",
     (getter) LineBreak_get_prep,
     (setter) LineBreak_set_prep,
     PyDoc_STR("\
Add user-defined line breaking behavior(s).  \
Value shall be list of items described below.\n\
\n\
``\"NONBREAKURI\"``\n\
    Won't break URIs.\n\
``\"BREAKURI\"``\n\
    Break URIs according to a rule suitable for printed materials.  For \n\
    more details see [CMOS]_, sections 6.17 and 17.11.\n\
(*regex*, *callable object*\\ [, *flags*])\n\
    The sequences matching *regex* will be broken by *callable object*.  \n\
    If *regex* is a string, not a regex object, *flags* may be specified. \n\
    For more details see \":ref:`User-Defined Breaking Behaviors`\".\n\
``None``\n\
    Cancel all methods assigned before.")},
    {"sizing",
     (getter) LineBreak_get_sizing,
     (setter) LineBreak_set_sizing,
     PyDoc_STR("\
Specify method to calculate size of string.  \
Following options are available.\n\
\n\
``\"UAX11\"``\n\
    Sizes are computed by columns of each characters.\n\
``None``\n\
    Number of grapheme clusters (See documentation of GCStr class) \n\
    contained in the string.\n\
callable object\n\
    See \":ref:`Calculating String Size`\".\n\
\n\
See also :attr:`eaw` attribute.")},
    {"urgent",
     (getter) LineBreak_get_urgent,
     (setter) LineBreak_set_urgent,
     PyDoc_STR("\
Specify method to handle excessing lines.  \
Following options are available.\n\
\n\
``\"RAISE\"``\n\
    Raise a :exc:`LineBreakException` exception.\n\
``\"FORCE\"``\n\
    Force breaking excessing fragment.\n\
``None``\n\
    Won't break excessing fragment.\n\
callable object\n\
    See \":ref:`User-Defined Breaking Behaviors`\".")},
    {"virama_as_joiner",
     (getter) LineBreak_get_virama_as_joiner,
     (setter) LineBreak_set_virama_as_joiner,
     PyDoc_STR("\
:term:`Virama sign` (\"halant\" in Hindi, \"coeng\" in Khmer) and its \n\
succeeding letter are not broken.\n\
\"Default\" grapheme cluster defined by [UAX29]_ does not contain this \
feature.")},
    {NULL}			/* Sentinel */
};

/*
 * Mapping methods
 */

static int
LineBreak_contains(PyObject *self, PyObject *value)
{
    return PySequence_Contains(STASH_DICT(LineBreak_AS_CSTRUCT(self)),
			       value);
}

static PySequenceMethods LineBreak_as_sequence = {
    0,				/* sq_length */
    0,				/* sq_concat */
    0,				/* sq_repeat */
    0,				/* sq_item */
    0,				/* sq_slice */
    0,				/* sq_ass_item */
    0,				/* sq_ass_slice */
    LineBreak_contains,		/* sq_contains */
    0,				/* sq_inplace_concat */
    0,				/* sq_inplace_repeat */
};

static Py_ssize_t
LineBreak_length(PyObject * self)
{
    return PyMapping_Length(STASH_DICT(LineBreak_AS_CSTRUCT(self)));
}

static PyObject *
LineBreak_subscript(PyObject * self, PyObject * key)
{
    return PyObject_GetItem(STASH_DICT(LineBreak_AS_CSTRUCT(self)), key);
}

static int
LineBreak_ass_subscript(PyObject * self, PyObject * key, PyObject * value)
{
    linebreak_t *lb = LineBreak_AS_CSTRUCT(self);

    if (value == NULL)
	return PyObject_DelItem(STASH_DICT(lb), key);
    else
	return PyObject_SetItem(STASH_DICT(lb), key, value);
}

static PyMappingMethods LineBreak_as_mapping = {
    LineBreak_length,		/* mp_length */
    LineBreak_subscript,	/* mp_subscript */
    LineBreak_ass_subscript	/* mp_ass_subscript */
};

static PyObject *
LineBreak_iter(PyObject *self)
{
    return PyObject_GetIter(STASH_DICT(LineBreak_AS_CSTRUCT(self)));
}

#define LineBreak_dictmethod_noargs(meth) \
static PyObject * \
LineBreak_##meth(PyObject *self) \
{ \
    PyObject *dict, *method, *ret; \
    dict = STASH_DICT(LineBreak_AS_CSTRUCT(self)); \
    if ((method = PyObject_GetAttrString(dict, #meth)) == NULL) \
	return NULL; \
    ret = PyObject_CallObject(method, NULL); \
    Py_DECREF(method); \
    return ret; \
}
#define LineBreak_dictmethod_varargs(meth) \
static PyObject * \
LineBreak_##meth(PyObject *self, PyObject *args) \
{ \
    PyObject *dict, *method, *ret; \
    dict = STASH_DICT(LineBreak_AS_CSTRUCT(self)); \
    if ((method = PyObject_GetAttrString(dict, #meth)) == NULL) \
	return NULL; \
    ret = PyObject_CallObject(method, args); \
    Py_DECREF(method); \
    return ret; \
}
#define LineBreak_dictmethod_keywords(meth) \
static PyObject * \
LineBreak_##meth(PyObject *self, PyObject *args, PyObject *kw) \
{ \
    PyObject *dict, *method, *ret; \
    dict = STASH_DICT(LineBreak_AS_CSTRUCT(self)); \
    if ((method = PyObject_GetAttrString(dict, #meth)) == NULL) \
	return NULL; \
    ret = PyObject_Call(method, args, kw); \
    Py_DECREF(method); \
    return ret; \
}

LineBreak_dictmethod_varargs(get)
LineBreak_dictmethod_varargs(setdefault)
LineBreak_dictmethod_varargs(pop)
LineBreak_dictmethod_noargs(popitem)
LineBreak_dictmethod_noargs(keys)
LineBreak_dictmethod_noargs(items)
LineBreak_dictmethod_noargs(values)
LineBreak_dictmethod_keywords(update)
LineBreak_dictmethod_noargs(clear)
LineBreak_dictmethod_noargs(copy)

/*
 * Class-specific methods
 */

PyDoc_STRVAR(LineBreak_Copy__doc__, "\
Copy LineBreak object.");

static PyObject *
LineBreak_Copy(PyObject * self, PyObject * args)
{
    linebreak_t *lb;

    if ((lb = linebreak_copy(LineBreak_AS_CSTRUCT(self))) == NULL) {
	PyErr_SetFromErrno(PyExc_RuntimeError);
	return NULL;
    }
    return LineBreak_FromCstruct(Py_TYPE(self), lb);
}

PyDoc_STRVAR(LineBreak_breakingRule__doc__, "\
S.rule(before, after) -> int\n\
\n\
Get possible line breaking behavior between strings *before* and *after*.\n\
Returned value is one of:\n\
\n\
``MANDATORY``\n\
    :term:`Mandatory break`.\n\
``DIRECT``\n\
    Both :term:`direct break` and :term:`indirect break` are allowed.\n\
``INDIRECT``\n\
    Indirect break is allowed but direct break is prohibited.\n\
``PROHIBITED``\n\
    Breaking is prohibited.\n\
\n\
Following instance attributes of LineBreak object S will affect to result.\n\
\n\
- :attr:`eastasian_context`\n\
- :attr:`hangul_as_al`\n\
- :attr:`lbc`\n\
- :attr:`legacy_cm`\n\
\n\
.. note::\n\
   This method gives just approximate description of line breaking\n\
   behavior.  Use :meth:`wrap<LineBreak.wrap>` method or \n\
   :ref:`other functions<Functions>` to fold actual texts.");

static PyObject *
LineBreak_breakingRule(PyObject * self, PyObject * args)
{
    linebreak_t *lb = LineBreak_AS_CSTRUCT(self);
    PyObject *before, *after;
    gcstring_t *bgcstr, *agcstr;
    propval_t blbc, albc, ret;

    if (!PyArg_ParseTuple(args, "OO", &before, &after))
        return NULL;
    if ((bgcstr = genericstr_ToCstruct(before, lb)) == NULL)
	return NULL;
    if (bgcstr->gclen == 0) {
	if (! GCStr_Check(before))
	    gcstring_destroy(bgcstr);
	Py_RETURN_NONE;
    }
    if ((agcstr = genericstr_ToCstruct(after, lb)) == NULL) {
	if (! GCStr_Check(before))
	    gcstring_destroy(bgcstr);
	return NULL;
    }
    if (agcstr->gclen == 0) {
	if (! GCStr_Check(before))
	    gcstring_destroy(bgcstr);
	if (! GCStr_Check(after))
	    gcstring_destroy(agcstr);
	Py_RETURN_NONE;
    }

    blbc = gcstring_lbclass_ext(bgcstr, -1);
    albc = gcstring_lbclass(agcstr, 0);
    ret = linebreak_get_lbrule(lb, blbc, albc);

    if (! GCStr_Check(before))
	gcstring_destroy(bgcstr);
    if (! GCStr_Check(after))
	gcstring_destroy(agcstr);

    if (ret == PROP_UNKNOWN) {
	Py_RETURN_NONE;
    }
    return PyInt_FromLong((long)ret);
}

PyDoc_STRVAR(LineBreak_wrap__doc__, "\
S.wrap(text) -> [GCStr]\n\
\n\
Break a Unicode string *text* and returns list of lines contained in the\n\
result.  Each item of list is grapheme cluster string (:class:`GCStr`\n\
object).");

static PyObject *
LineBreak_wrap(PyObject * self, PyObject * args)
{
    linebreak_t *lb = LineBreak_AS_CSTRUCT(self);
    PyObject *str, *ret;
    PyTypeObject *gcstr_type;
    unistr_t unistr = { NULL, 0 };
    gcstring_t **broken;
    size_t i;

    if (!PyArg_ParseTuple(args, "O", &str))
	return NULL;
    if (unicode_ToCstruct(&unistr, str) == NULL)
	return NULL;

    linebreak_reset(lb);
    broken = linebreak_break(lb, &unistr);
    free(unistr.str);
    if (PyErr_Occurred()) {
	linebreak_free_result(broken, 1);
	return NULL;
    } else if (broken == NULL) {
	if (lb->errnum == LINEBREAK_ELONG)
	    PyErr_SetString((PyObject *)STASH_EXCEPTION(lb),
			    "Excessive line was found");
	else if (lb->errnum) {
	    errno = lb->errnum;
	    PyErr_SetFromErrno(PyExc_RuntimeError);
	} else
	    PyErr_SetString(PyExc_RuntimeError, "unknown error");
	return NULL;
    }

    if (GCStr_Check(str))
	gcstr_type = Py_TYPE(str);
    else
	gcstr_type = STASH_GCSTRTYPE(lb);

    ret = PyList_New(0);
    for (i = 0; broken[i] != NULL; i++) {
	PyObject *v;
	if ((v = GCStr_FromCstruct(gcstr_type, broken[i])) == NULL) {
	    Py_DECREF(ret);
	    for ( ; broken[i] != NULL; i++)
		gcstring_destroy(broken[i]);
	    linebreak_free_result(broken, 0);
	    return NULL;
	}
	PyList_Append(ret, v);
    }
    linebreak_free_result(broken, 0);

    Py_INCREF(ret);
    return ret;
}

static PyMethodDef LineBreak_methods[] = {
    {"__copy__",
     (PyCFunction) LineBreak_Copy, METH_NOARGS,
     LineBreak_Copy__doc__},
    {"breakingRule",
     (PyCFunction) LineBreak_breakingRule, METH_VARARGS,
     LineBreak_breakingRule__doc__},
    {"wrap",
     (PyCFunction) LineBreak_wrap, METH_VARARGS,
     LineBreak_wrap__doc__},

    {"get", (PyCFunction)LineBreak_get, METH_VARARGS, NULL},
    {"setdefault", (PyCFunction)LineBreak_setdefault, METH_VARARGS, NULL},
    {"pop", (PyCFunction)LineBreak_pop, METH_VARARGS, NULL},
    {"popitem", (PyCFunction)LineBreak_popitem, METH_NOARGS, NULL},
    {"keys", (PyCFunction)LineBreak_keys, METH_NOARGS, NULL},
    {"items", (PyCFunction)LineBreak_items, METH_NOARGS, NULL},
    {"values", (PyCFunction)LineBreak_values, METH_NOARGS, NULL},
    {"update", (PyCFunction)LineBreak_update, METH_VARARGS | METH_KEYWORDS,
     NULL},
    /*
    {"fromkeys", (PyCFunction)LineBreak_fromkeys, METH_VARARGS | METH_CLASS,
     NULL}, 
     */
    {"clear", (PyCFunction)LineBreak_clear, METH_NOARGS, NULL},
    {"copy", (PyCFunction)LineBreak_copy, METH_NOARGS, NULL},

    {NULL}			/* Sentinel */
};


static PyTypeObject LineBreak_Type = {
#if PY_MAJOR_VERSION >= 3
    PyVarObject_HEAD_INIT(NULL, 0)
#else				/* PY_MAJOR_VERSION */
    PyObject_HEAD_INIT(NULL)
    0,				/*ob_size */
#endif				/* PY_MAJOR_VERSION */
    "_textseg.LineBreak",	/*tp_name */
    sizeof(LineBreakObject),	/*tp_basicsize */
    0,				/*tp_itemsize */
    (destructor)LineBreak_dealloc,		/*tp_dealloc */
    0,				/*tp_print */
    0,				/*tp_getattr */
    0,				/*tp_setattr */
    0,				/*tp_compare */
    0,				/*tp_repr */
    0,				/*tp_as_number */
    &LineBreak_as_sequence,	/*tp_as_sequence */
    &LineBreak_as_mapping,	/*tp_as_mapping */
    0,				/*tp_hash */
    0,				/*tp_call */
    0,				/*tp_str */
    0,				/*tp_getattro */
    0,				/*tp_setattro */
    0,				/*tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,	/*tp_flags */
    "LineBreak objects",	/* tp_doc */
    0,				/* tp_traverse */
    0,				/* tp_clear */
    0,				/* tp_richcompare */
    0,				/* tp_weaklistoffset */
    &LineBreak_iter,		/* tp_iter */
    0,				/* tp_iternext */
    LineBreak_methods,		/* tp_methods */
    0,				/* tp_members */
    LineBreak_getseters,	/* tp_getset */
    0,				/* tp_base */
    0,				/* tp_dict */
    0,				/* tp_descr_get */
    0,				/* tp_descr_set */
    0,				/* tp_dictoffset */
    (initproc) LineBreak_init,	/* tp_init */
    0,				/* tp_alloc */
    LineBreak_new,		/* tp_new */
};

/**
 ** TailoringDict class
 **/

static void
TDict_dealloc(TDictObject * self)
{
    /* remove linkage from LineBreak object */
    if (self->lb != NULL) {
	if (self->next != NULL)
	    self->next->prev = self->prev;
	if (self->prev != NULL)
	    self->prev->next = self->next;
	else
	    ((LineBreakObject *)self->lb)->tdict = self->next;
    }

    Py_TYPE(self)->tp_free(self);
}

static PyObject *
TDict_FromLineBreak(PyObject *lb, tdicttype ttype)
{
    TDictObject * self;

    assert(LineBreak_Check(lb));

    if ((self = (TDictObject *)TDict_Type.tp_alloc(&TDict_Type, 0)) == NULL)
        return NULL;

    self->ttype = ttype;
    self->lb = lb;

    /* add linkage to LineBreak object */
    self->prev = NULL;
    self->next = ((LineBreakObject *) lb)->tdict;
    if (self->next != NULL)
	self->next->prev = self;
    ((LineBreakObject *) lb)->tdict = self;

    return (PyObject *) self;
}

/*
 * Mapping methods
 */

static PyObject *
TDict_subscript(PyObject * self, PyObject * key)
{
    TDictObject * tdict = (TDictObject *)self;
    unichar_t c;
    propval_t p;

    if (tdict->lb == NULL) {
	PyErr_SetString(PyExc_KeyError, "parent object has gone");
	return NULL;
    }
    if ((c = strOrInt_ToUCS(key)) == (unichar_t)(-1))
	return NULL;

    if (tdict->ttype == TDICT_LBC)
	p = linebreak_search_lbclass(LineBreak_AS_CSTRUCT(tdict->lb), c);
    else
	p = linebreak_search_eawidth(LineBreak_AS_CSTRUCT(tdict->lb), c);
    if (p == PROP_UNKNOWN) {
	PyErr_Format(PyExc_KeyError, "not found");
	return NULL;
    }
    return PyInt_FromLong((signed long) p);
}

static int
TDict_ass_subscript(PyObject * self, PyObject * key, PyObject * value)
{
    TDictObject * tdict = (TDictObject *)self;
    PyObject *item;
    unichar_t c;
    propval_t p;
    size_t i;

    if (value == NULL) {
	PyErr_SetString(PyExc_NotImplementedError,
			"Can not cancel tailoring by each");
	return -1;
    }
    if (tdict->lb == NULL) {
	PyErr_SetString(PyExc_AttributeError, "parent object has gone");
	return -1;
    }

    if (PyInt_Check(value))
	p = (propval_t) PyInt_AsLong(value);
    else if (PyLong_Check(value))
	p = (propval_t) PyLong_AsLong(value);
    else {
	PyErr_Format(PyExc_ValueError,
		     "value must be integer, not %200s",
		     Py_TYPE(value)->tp_name);
	return -1;
    }

    if (PySequence_Check(key)) {
	for (i = 0; (item = PySequence_GetItem(key, i)) != NULL; i++) {
	    if ((c = strOrInt_ToUCS(item)) == (unichar_t)(-1)) {
		Py_DECREF(item);
		return -1;
	    }
	    if (tdict->ttype == TDICT_LBC)
		linebreak_update_lbclass(LineBreak_AS_CSTRUCT(tdict->lb),
					 c, p);
	    else
		linebreak_update_eawidth(LineBreak_AS_CSTRUCT(tdict->lb),
					 c, p);
	    Py_DECREF(item);
	}
	PyErr_Clear();
	return 0;
    }
    if ((c = strOrInt_ToUCS(key)) == (unichar_t)(-1))
	return -1;
    if (tdict->ttype == TDICT_LBC)
	linebreak_update_lbclass(LineBreak_AS_CSTRUCT(tdict->lb), c, p);
    else
	linebreak_update_eawidth(LineBreak_AS_CSTRUCT(tdict->lb), c, p);
    return 0;
}

static int
tdict_clear(PyObject *self)
{
    TDictObject * tdict = (TDictObject *) self;

    if (tdict->lb == NULL)
	return 0;
    if (tdict->ttype == TDICT_LBC)
	linebreak_clear_lbclass(LineBreak_AS_CSTRUCT(tdict->lb));
    else
	linebreak_clear_eawidth(LineBreak_AS_CSTRUCT(tdict->lb));
    return 0;
}

static PyObject *
TDict_clear(PyObject *self)
{
    if (tdict_clear(self) != 0)
	return NULL;
    Py_RETURN_NONE;
}

static PyObject *
TDict_get(PyObject *self, PyObject *args)
{
    PyObject *key, *failobj = Py_None, *val;

    if (! PyArg_UnpackTuple(args, "get", 1, 2, &key, &failobj))	/* borrowed */
	return NULL;

    if ((val = PyObject_GetItem(self, key)) == NULL) {
	PyErr_Clear();
	val = failobj;
	Py_INCREF(val);
    }
    return val;
}

static PyObject *
TDict_setdefault(PyObject *self, PyObject *args)
{
    PyObject *key, *failobj = Py_None, *val;

    if (!PyArg_UnpackTuple(args, "get", 1, 2, &key, &failobj))	/* borrowed */
	return NULL;

    if ((val = PyObject_GetItem(self, key)) == NULL) {
	PyErr_Clear();
	if (PyObject_SetItem(self, key, failobj) != 0)
	    return NULL;
	val = failobj;
	Py_INCREF(val);
    }
    return val;
}

static int
tdict_update(PyObject * tdict, PyObject * arg, int clear)
{
    Py_ssize_t pos;
    PyObject *key, *value, *keys, *iter;
    linebreak_t *dst = NULL, *src = NULL;

    assert(TDict_CheckExact(tdict));
    assert(arg != NULL);

    if (((TDictObject *) tdict)->lb == NULL) {
	PyErr_SetString(PyExc_AttributeError, "parent object has gone");

	return -1;
    }
    dst = LineBreak_AS_CSTRUCT(((TDictObject *) tdict)->lb);
    if (TDict_CheckExact(arg)) {
	if (((TDictObject *) arg)->lb == NULL) {
	    PyErr_SetString(PyExc_AttributeError, "parent object has gone");

	    return -1;
	}
	src = LineBreak_AS_CSTRUCT(((TDictObject *) arg)->lb);
	if (dst == src)
	    return 0;
    }

    if (arg == Py_None || clear)
	tdict_clear(tdict);

    if (arg == Py_None)
	;
    else if (TDict_CheckExact(arg)) {
	if (((TDictObject *) arg)->ttype == TDICT_LBC)
	    linebreak_merge_lbclass(dst, src);
	else
	    linebreak_merge_eawidth(dst, src);
	if (dst->errnum) {
	    errno = dst->errnum;
	    PyErr_SetFromErrno(PyExc_RuntimeError);

	    return -1;
	}
    } else if (PyDict_Check(arg)) {
	pos = 0;
	while (PyDict_Next(arg, &pos, &key, &value))
	    if (PyObject_SetItem(tdict, key, value) != 0)
		return -1;
    } else if (PyObject_HasAttrString(arg, "keys")) {
	if ((keys = PyMapping_Keys(arg)) == NULL)
	    return -1;
	iter = PyObject_GetIter(keys);
	Py_DECREF(keys);
	if (iter == NULL)
	    return -1;

	for (key = PyIter_Next(iter); key != NULL; key = PyIter_Next(iter)) {
	    if ((value = PyObject_GetItem(arg, key)) == NULL) {
		Py_DECREF(key);
		Py_DECREF(iter);
		return -1;
	    }
	    if (PyObject_SetItem(tdict, key, value) != 0) {
		Py_DECREF(value);
		Py_DECREF(key);
		Py_DECREF(iter);
		return -1;
	    }
	    Py_DECREF(value);
	    Py_DECREF(key);
	}

	Py_DECREF(iter);
    } else {
	PyErr_Format(PyExc_TypeError,
		     "attribute must be dictionary or sequence of tuples, "
		     "not %200s",
		     Py_TYPE(arg)->tp_name);

	return -1;
    }
    return 0;
}

static PyObject *
TDict_update(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *arg = NULL;
    int result = 0;

    if (! PyArg_UnpackTuple(args, "update", 0, 1, &arg))
	result = -1;
    else if (arg != NULL)
	result = tdict_update(self, arg, 0);

    if (result == 0 && kwds != NULL) {
#if ! (PY_MAJOR_VERSION <= 2 || (PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION < 2))
	if (! PyArg_ValidateKeywordArguments(kwds))
	    result = -1;
	else
#endif
	result = tdict_update(self, kwds, 0);
    }

    if (result != 0)
	return NULL;
    Py_RETURN_NONE;
}

/*
 * Method for debugging use
 */
static PyObject *
TDict_dump(PyObject *self)
{
    mapent_t * map;
    size_t mapsiz, i;

    printf("TYPE = %s\n"
           "     UCS      LB EA GC SC\n"
           "------------- -- -- -- --\n",
	((TDictObject *)self)->ttype == TDICT_LBC ? "lbc" : "eaw");

    if (((TDictObject *)self)->lb == NULL) {
	printf("inactive\n"
               "-------------------------\n");
	Py_RETURN_NONE;
    }
    map = LineBreak_AS_CSTRUCT(((TDictObject *)self)->lb)->map;
    mapsiz = LineBreak_AS_CSTRUCT(((TDictObject *)self)->lb)->mapsiz;
    if (map == NULL || mapsiz == 0) {
        printf("empty\n"
               "-------------------------\n");
        Py_RETURN_NONE;
    }
    for (i = 0; i < mapsiz; i++)
	printf("%6X-%6X %2d %2d %2d %2d\n",
	       map[i].beg, map[i].end, (signed char) map[i].lbc,
	       (signed char) map[i].eaw, (signed char) map[i].gcb,
	       (signed char) map[i].scr);
    printf("-------------------------\n");
    Py_RETURN_NONE;
}

static PyMappingMethods TDict_as_mapping = {
    0,				/* mp_length */
    TDict_subscript,		/* mp_subscript */
    TDict_ass_subscript		/* mp_ass_subscript */
};

static PyMethodDef TDict_methods[] = {
    {"clear", (PyCFunction) TDict_clear, METH_NOARGS, NULL},
    {"get", (PyCFunction) TDict_get, METH_VARARGS, NULL},
    {"setdefault", (PyCFunction) TDict_setdefault, METH_VARARGS, NULL},
    {"update", (PyCFunction) TDict_update, METH_VARARGS | METH_KEYWORDS,
     NULL},
    {"_dump", (PyCFunction) TDict_dump, METH_NOARGS, NULL},
    {NULL,		NULL}   /* sentinel */
};


static PyTypeObject TDict_Type = {
#if PY_MAJOR_VERSION >= 3
    PyVarObject_HEAD_INIT(NULL, 0)
#else				/* PY_MAJOR_VERSION */
    PyObject_HEAD_INIT(NULL)
    0,				/*ob_size */
#endif				/* PY_MAJOR_VERSION */
    "_textseg.TailoringDict",	/*tp_name */
    sizeof(TDictObject),	/*tp_basicsize */
    0,				/*tp_itemsize */
    (destructor)TDict_dealloc,		/*tp_dealloc */
    0,				/*tp_print */
    0,				/*tp_getattr */
    0,				/*tp_setattr */
    0,				/*tp_compare */
    0,				/*tp_repr */
    0,				/*tp_as_number */
    0,				/*tp_as_sequence */
    &TDict_as_mapping,		/*tp_as_mapping */
    0,				/*tp_hash */
    0,				/*tp_call */
    0,				/*tp_str */
    0,				/*tp_getattro */
    0,				/*tp_setattro */
    0,				/*tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,	/*tp_flags */
    "TailoringDict objects",	/* tp_doc */
    0,				/* tp_traverse */
    0,				/* tp_clear */
    0,				/* tp_richcompare */
    0,				/* tp_weaklistoffset */
    0,				/* tp_iter */
    0,				/* tp_iternext */
    TDict_methods,		/* tp_methods */
    0,				/* tp_members */
    0,				/* tp_getset */
    0,				/* tp_base */
    0,				/* tp_dict */
    0,				/* tp_descr_get */
    0,				/* tp_descr_set */
    0,				/* tp_dictoffset */
    0,				/* tp_init */
    0,				/* tp_alloc */
    0,				/* tp_new */
};


/**
 ** GCStr class
 **/

/*
 * Constructor & Destructor
 */

static void
GCStr_dealloc(PyObject * self)
{
    gcstring_destroy(GCStr_AS_CSTRUCT(self));
    Py_TYPE(self)->tp_free(self);
}

static PyObject *
GCStr_subtype_new(PyTypeObject *, PyObject *, PyObject *);

static PyObject *
GCStr_Copy(PyObject *, PyObject *);

static PyObject *
GCStr_new(PyTypeObject * type, PyObject * args, PyObject * kwds)
{
    PyObject *pystr = NULL, *pyobj = NULL;
    static char *kwlist[] = { "object", "lb", NULL };
    gcstring_t *gcstr;
    linebreak_t *lb;

    if (type != &GCStr_Type)
	return GCStr_subtype_new(type, args, kwds);
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|OO!:GCStr", kwlist,
				     &pystr, &LineBreak_Type, &pyobj))
	return NULL;

    if (pyobj == NULL)
        lb = NULL;
    else
        lb = LineBreak_AS_CSTRUCT(pyobj);

    if (pystr == NULL) {
	if ((gcstr = gcstring_new(NULL, lb)) == NULL) {
	    PyErr_SetFromErrno(PyExc_RuntimeError);
	    return NULL;
	}
    } else if (GCStr_Check(pystr))
	return GCStr_Copy(pystr, NULL);
    else if ((gcstr = genericstr_ToCstruct(pystr, lb)) == NULL)
	return NULL;

    return GCStr_FromCstruct(&GCStr_Type, gcstr);
}

static PyObject *
GCStr_subtype_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *tmp, *newobj;

    assert(PyType_IsSubtype(type, &GCStr_Type));
    if ((tmp = GCStr_new(&GCStr_Type, args, kwds)) == NULL)
	return NULL;
    assert(GCStr_CheckExact(tmp));
    if ((newobj = type->tp_alloc(type, 0)) == NULL) {
	Py_DECREF(tmp);
	return NULL;
    }
    GCStr_AS_CSTRUCT(newobj) = GCStr_AS_CSTRUCT(tmp);
    GCStr_AS_CSTRUCT(tmp) = NULL;
    Py_DECREF(tmp);
    return newobj;
}

/*
 * Attribute methods
 */

static PyObject *
GCStr_get_chars(PyObject * self)
{
#ifdef OLDAPI_Py_UNICODE_NARROW
    gcstring_t *gcstr = GCStr_AS_CSTRUCT(self);
    size_t i, chars;

    if (gcstr->str == NULL)
	return PyInt_FromSsize_t(0);
    for (i = 0, chars = 0; i < gcstr->len; i++, chars++)
	if (0x10000 <= gcstr->str[i])
	    chars++;
    return PyInt_FromSsize_t(chars);
#else				/* OLDAPI_Py_UNICODE_NARROW */
    return PyInt_FromSsize_t(GCStr_AS_CSTRUCT(self)->len);
#endif				/* OLDAPI_Py_UNICODE_NARROW */
}

static PyObject *
GCStr_get_cols(PyObject * self)
{
    return PyInt_FromSsize_t(gcstring_columns(GCStr_AS_CSTRUCT(self)));
}

static PyObject *
GCStr_get_lbc(PyObject * self)
{
    propval_t ret;

    if ((ret = gcstring_lbclass(GCStr_AS_CSTRUCT(self), 0))
	== PROP_UNKNOWN) {
	Py_RETURN_NONE;
    }
    return PyInt_FromLong((long) ret);
}

static PyObject *
GCStr_get_lbcext(PyObject * self)
{
    propval_t ret;

    if ((ret = gcstring_lbclass_ext(GCStr_AS_CSTRUCT(self), -1))
	== PROP_UNKNOWN) {
        Py_RETURN_NONE;
    }
    return PyInt_FromLong((long) ret);
}

static PyGetSetDef GCStr_getseters[] = {
    {"chars",
     (getter) GCStr_get_chars, NULL,
     "Number of Unicode characters grapheme cluster string includes, "
     "i.e. length as Unicode string.",
     NULL},
    {"cols",
     (getter) GCStr_get_cols, NULL,
     "Total number of columns of grapheme clusters "
     "defined by built-in character database.  "
     "For more details see documentations of LineBreak class.",
     NULL},
    {"lbc",
     (getter) GCStr_get_lbc, NULL,
     ":term:`Line breaking class` of the first character of first "
     "grapheme cluster.",
     NULL},
    {"lbcext",
     (getter) GCStr_get_lbcext, NULL,
     ":term:`Line breaking class` of last grapheme extender of last "
     "grapheme cluster.  If there are no grapheme extenders or its "
     "class is CM, value of last grapheme base will be returned.",
     NULL},
    {NULL}			/* Sentinel */
};

/*
 * String methods
 */

#if PY_MAJOR_VERSION >= 3
static PyObject *
GCStr_Str(PyObject * self)
{
    return unicode_FromCstruct((unistr_t *) (GCStr_AS_CSTRUCT(self)));
}
#endif

static PyObject *
GCStr_compare(PyObject * a, PyObject * b, int op)
{
    gcstring_t *astr, *bstr;
    linebreak_t *lb;
    int cmp;

    if (GCStr_Check(a))
	lb = GCStr_AS_CSTRUCT(a)->lbobj;
    else if (GCStr_Check(b))
	lb = GCStr_AS_CSTRUCT(b)->lbobj;
    else
	lb = NULL;

    if ((astr = genericstr_ToCstruct(a, lb)) == NULL ||
	(bstr = genericstr_ToCstruct(b, lb)) == NULL) {
	if (a != NULL && !GCStr_Check(a))
	    gcstring_destroy(astr);
	return NULL;
    }
    cmp = gcstring_cmp(astr, bstr);
    if (!GCStr_Check(a))
	gcstring_destroy(astr);
    if (!GCStr_Check(b))
	gcstring_destroy(bstr);

    switch (op) {
    case Py_LT:
	return PyBool_FromLong(cmp < 0);
    case Py_LE:
	return PyBool_FromLong(cmp <= 0);
    case Py_EQ:
	return PyBool_FromLong(cmp == 0);
    case Py_NE:
	return PyBool_FromLong(cmp != 0);
    case Py_GT:
	return PyBool_FromLong(cmp > 0);
    case Py_GE:
	return PyBool_FromLong(cmp >= 0);
    default:
	Py_INCREF(Py_NotImplemented);
	return Py_NotImplemented;
    }
}

/*
 * Sequence methods
 */

static Py_ssize_t
GCStr_length(PyObject * self)
{
    return (Py_ssize_t) GCStr_AS_CSTRUCT(self)->gclen;
}

static PyObject *
GCStr_concat(PyObject * o1, PyObject * o2)
{
    gcstring_t *gcstr1, *gcstr2, *gcstr;
    linebreak_t *lb;
    PyTypeObject *gcstr_type;

    if (GCStr_Check(o1)) {
	lb = GCStr_AS_CSTRUCT(o1)->lbobj;
	gcstr_type = Py_TYPE(o1);
    } else if (GCStr_Check(o2)) {
	lb = GCStr_AS_CSTRUCT(o2)->lbobj;
	gcstr_type = Py_TYPE(o2);
    } else {
	lb = NULL;
	gcstr_type = &GCStr_Type;
    }

    if ((gcstr1 = genericstr_ToCstruct(o1, lb)) == NULL ||
	(gcstr2 = genericstr_ToCstruct(o2, lb)) == NULL) {
	if (!GCStr_Check(o1))
	    gcstring_destroy(gcstr1);
	return NULL;
    }
    if ((gcstr = gcstring_concat(gcstr1, gcstr2)) == NULL) {
	PyErr_SetFromErrno(PyExc_RuntimeError);

	if (!GCStr_Check(o1))
	    gcstring_destroy(gcstr1);
	if (!GCStr_Check(o2))
	    gcstring_destroy(gcstr2);
	return NULL;
    }

    if (!GCStr_Check(o1))
	gcstring_destroy(gcstr1);
    if (!GCStr_Check(o2))
	gcstring_destroy(gcstr2);
    return GCStr_FromCstruct(gcstr_type, gcstr);
}

static PyObject *
GCStr_repeat(PyObject * self, Py_ssize_t count)
{
    gcstring_t *gcstr;
    Py_ssize_t i;		/* need signed comparison */

    if ((gcstr = gcstring_new(NULL, GCStr_AS_CSTRUCT(self)->lbobj)) == NULL) {
	PyErr_SetFromErrno(PyExc_RuntimeError);
	return NULL;
    }
    for (i = 0; i < count; i++)
	if (gcstring_append(gcstr, GCStr_AS_CSTRUCT(self)) == NULL) {
	    PyErr_SetFromErrno(PyExc_RuntimeError);
	    return NULL;
	}
    return GCStr_FromCstruct(Py_TYPE(self), gcstr);
}

static PyObject *
GCStr_item(PyObject * self, Py_ssize_t i)
{
    gcstring_t *gcstr;

    if (GCStr_AS_CSTRUCT(self)->gclen == 0) {
	PyErr_SetString(PyExc_IndexError, "GCStr index out of range");
	return NULL;
    }
    if ((gcstr = gcstring_substr(GCStr_AS_CSTRUCT(self), i, 1))
	== NULL) {
	PyErr_SetFromErrno(PyExc_RuntimeError);
	return NULL;
    }
    if (gcstr->gclen == 0) {
	PyErr_SetString(PyExc_IndexError, "GCStr index out of range");
	gcstring_destroy(gcstr);
	return NULL;
    }
    return GCStr_FromCstruct(Py_TYPE(self), gcstr);
}

static PyObject *
GCStr_slice(PyObject * self, Py_ssize_t start, Py_ssize_t end)
{
    gcstring_t *gcstr;

    /* standard clamping */
    if (start < 0)
	start = 0;
    if (end < 0)
	end = 0;
    if (GCStr_AS_CSTRUCT(self)->gclen < end)
	end = GCStr_AS_CSTRUCT(self)->gclen;
    if (end < start)
	start = end;
    /* copy slice */
    if ((gcstr =
	 gcstring_substr(GCStr_AS_CSTRUCT(self), start, end - start))
	== NULL) {
	PyErr_SetFromErrno(PyExc_RuntimeError);
	return NULL;
    }
    return GCStr_FromCstruct(Py_TYPE(self), gcstr);
}

static int
GCStr_ass_item(PyObject * self, Py_ssize_t i, PyObject * v)
{
    gcstring_t *gcstr, *repl;

    if (GCStr_AS_CSTRUCT(self)->gclen == 0) {
	PyErr_SetString(PyExc_IndexError, "GCStr index out of range");
	return -1;
    }
    if (v == NULL) {
	PyErr_SetString(PyExc_TypeError,
			"object doesn't support item deletion");
	return -1;
    }
    if ((repl = genericstr_ToCstruct(v, GCStr_AS_CSTRUCT(self)->lbobj))
	== NULL)
	return -1;
    if ((gcstr = gcstring_replace(GCStr_AS_CSTRUCT(self), i, 1, repl))
	== NULL) {
	PyErr_SetFromErrno(PyExc_RuntimeError);

	if (!GCStr_Check(v))
	    gcstring_destroy(repl);
	return -1;
    }

    if (!GCStr_Check(v))
	gcstring_destroy(gcstr);
    return 0;
}

static int
GCStr_ass_slice(PyObject * self, Py_ssize_t start, Py_ssize_t end,
		PyObject * v)
{
    gcstring_t *gcstr, *repl;
    linebreak_t *lb = GCStr_AS_CSTRUCT(self)->lbobj;

    if (v == NULL)
	repl = gcstring_new(NULL, lb);
    else if ((repl = genericstr_ToCstruct(v, lb)) == NULL)
	return -1;

    /* standard clamping */
    if (start < 0)
	start = 0;
    if (end < 0)
	end = 0;
    if (GCStr_AS_CSTRUCT(self)->gclen < end)
	end = GCStr_AS_CSTRUCT(self)->gclen;
    if (end < start)
	start = end;

    if ((gcstr =
	 gcstring_replace(GCStr_AS_CSTRUCT(self), start, end - start,
			  repl)) == NULL) {
	PyErr_SetFromErrno(PyExc_RuntimeError);

	if (v == NULL || !GCStr_Check(v))
	    gcstring_destroy(repl);
	return -1;
    }

    if (v == NULL || !GCStr_Check(v))
	gcstring_destroy(repl);
    return 0;
}

static PyObject *
GCStr_subscript(PyObject * self, PyObject * item)
{
    Py_ssize_t k;
    gcstring_t *gcstr = GCStr_AS_CSTRUCT(self);

#if PY_MAJOR_VERSION == 2 && PY_MINOR_VERSION <= 4
    if (PyInt_Check(item))
	k = PyInt_AsSsize_t(item);
    else if (PyLong_Check(item))
	k = PyLong_AsSsize_t(item);
#else				/* PY_MAJOR_VERSION == 2 && ... */
    if (PyIndex_Check(item) || PyNumber_Check(item))
	k = PyNumber_AsSsize_t(item, PyExc_IndexError);
#endif				/* PY_MAJOR_VERSION == 2 && ... */
    else if (PySlice_Check(item)) {
	Py_ssize_t start, stop, step, len, cur, i;
	gcstring_t *result;

#if PY_MAJOR_VERSION == 2 || (PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION <= 1)
	if (PySlice_GetIndicesEx((PySliceObject *) item, gcstr->gclen,
				 &start, &stop, &step, &len) < 0)
	    return NULL;
#else				/* PY_MAJOR_VERSION ... */
	if (PySlice_GetIndicesEx((PyObject *) item, gcstr->gclen,
				 &start, &stop, &step, &len) < 0)
	    return NULL;
#endif				/* PY_MAJOR_VERSION ... */

	if (len <= 0)
	    return GCStr_FromCstruct(Py_TYPE(self),
				     gcstring_new(NULL, gcstr->lbobj));
	else if (step == 1)
	    return GCStr_FromCstruct(Py_TYPE(self),
				     gcstring_substr(gcstr, start, len));
	if ((result = gcstring_new(NULL, gcstr->lbobj)) == NULL) {
	    PyErr_SetFromErrno(PyExc_RuntimeError);
	    return NULL;
	}
	for (cur = start, i = 0; i < len; cur += step, i++)
	    if (gcstring_append(result, gcstring_substr(gcstr, cur, 1))
		== NULL) {
		PyErr_SetFromErrno(PyExc_RuntimeError);
		gcstring_destroy(result);
		return NULL;
	    }
	return GCStr_FromCstruct(Py_TYPE(self), result);
    } else {
	PyErr_SetString(PyExc_TypeError, "GCStr indices must be integers");
	return NULL;
    }

    if (k == -1 && PyErr_Occurred())
	return NULL;
    if (k < 0)
	k += gcstr->gclen;
    return GCStr_item(self, k);
}

static int
GCStr_ass_subscript(PyObject * self, PyObject * item, PyObject * v)
{
    Py_ssize_t k;
    gcstring_t *gcstr = GCStr_AS_CSTRUCT(self);

#if PY_MAJOR_VERSION == 2 && PY_MINOR_VERSION <= 4
    if (PyInt_Check(item))
	k = PyInt_AsSsize_t(item);
    else if (PyLong_Check(item))
	k = PyLong_AsSsize_t(item);
#else				/* PY_MAJOR_VERSION == 2 && ... */
    if (PyIndex_Check(item) || PyNumber_Check(item))
	k = PyNumber_AsSsize_t(item, PyExc_IndexError);
#endif				/* PY_MAJOR_VERSION == 2 && ... */
    else if (PySlice_Check(item)) {
	Py_ssize_t start, stop, step, len;
	gcstring_t *repl;

#if PY_MAJOR_VERSION == 2 || (PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION <= 1)
	if (PySlice_GetIndicesEx((PySliceObject *) item, gcstr->gclen,
				 &start, &stop, &step, &len) < 0)
	    return -1;
#else				/* PY_MAJOR_VERSION ... */
	if (PySlice_GetIndicesEx((PyObject *) item, gcstr->gclen,
				 &start, &stop, &step, &len) < 0)
	    return -1;
#endif				/* PY_MAJOR_VERSION ... */

	if (step != 1) {
	    PyErr_SetNone(PyExc_NotImplementedError);
	    return -1;
	}
	if (len < 0)
	    return 0;

	if (v == NULL) {
	    if ((repl = gcstring_new(NULL, gcstr->lbobj)) == NULL) {
		PyErr_SetFromErrno(PyExc_RuntimeError);
		return -1;
	    }
	    if (gcstring_replace(gcstr, start, len, repl) == NULL) {
		PyErr_SetFromErrno(PyExc_RuntimeError);

		gcstring_destroy(repl);
		return -1;
	    }
	    gcstring_destroy(repl);
	    return 0;
	}

	if ((repl = genericstr_ToCstruct(v, gcstr->lbobj)) == NULL)
	    return -1;
	if (gcstring_replace(gcstr, start, len, repl) == NULL) {
	    PyErr_SetFromErrno(PyExc_RuntimeError);

	    if (!GCStr_Check(v))
		gcstring_destroy(repl);
	    return -1;
	}
	if (!GCStr_Check(v))
	    gcstring_destroy(repl);
	return 0;
    } else {
	PyErr_SetString(PyExc_TypeError, "GCStr indices must be integers");
	return -1;
    }

    if (k == -1 && PyErr_Occurred())
	return -1;
    if (k < 0)
	k += gcstr->gclen;
    return GCStr_ass_item(self, k, v);
}

static PySequenceMethods GCStr_as_sequence = {
    GCStr_length,		/* sq_length */
    GCStr_concat,		/* sq_concat */
    GCStr_repeat,		/* sq_repeat */
    GCStr_item,			/* sq_item */
    GCStr_slice,		/* sq_slice: unused by 3.0 (?) */
    GCStr_ass_item,		/* sq_ass_item */
    GCStr_ass_slice,		/* sq_ass_slice: unused by 3.0 (?) */
    NULL,			/* sq_contains */
    NULL,			/* sq_inplace_concat */
    NULL			/* sq_inplace_repeat */
};

static PyMappingMethods GCStr_as_mapping = {
    GCStr_length,		/* mp_length */
    GCStr_subscript,		/* mp_subscript */
    GCStr_ass_subscript		/* mp_ass_subscript */
};

/*
 * Class specific methods
 */

PyDoc_STRVAR(GCStr_Copy__doc__, "\
Create a copy of GCStr object.");

static PyObject *
GCStr_Copy(PyObject * self, PyObject * args)
{
    gcstring_t *gcstr;

    if ((gcstr = gcstring_copy(GCStr_AS_CSTRUCT(self))) == NULL) {
	PyErr_SetFromErrno(PyExc_RuntimeError);
	return NULL;
    }
    return GCStr_FromCstruct(Py_TYPE(self), gcstr);
}

PyDoc_STRVAR(GCStr_flag__doc__, "S.flag(offset [, value]) => int\n\
\n\
Get and optionally set flag value of offset-th grapheme cluster.\n\
Flag value is an non-zero integer not greater than 255 and initially is 0.\n\
Predefined flag values are:\n\
\n\
``ALLOW_BEFORE``\n\
    Allow line breaking just before this grapheme cluster.\n\
``PROHIBIT_BEFORE``\n\
    Prohibit line breaking just before this grapheme cluster.");

static PyObject *
GCStr_flag(PyObject * self, PyObject * args)
{
    gcstring_t *gcstr = GCStr_AS_CSTRUCT(self);
    Py_ssize_t i;
    long v = -1L;
    PyObject *ret;

    if (!PyArg_ParseTuple(args, ARG_FORMAT_SSIZE_T "|i", &i, &v))
	return NULL;
    if (i < 0 || gcstr->gclen <= i) {
	Py_RETURN_NONE;
    }
    ret = PyInt_FromLong((unsigned long) gcstr->gcstr[i].flag);
    if (0 < v)
	gcstr->gcstr[i].flag = (propval_t) v;

    return ret;
}

/* FIXME: often unavailable */
static PyObject *
GCStr_radd(PyObject * self, PyObject * args)
{
    PyObject *pyobj;

    if (!PyArg_ParseTuple(args, "O", &pyobj))
	return NULL;
    return GCStr_concat(pyobj, self);
}

static PyObject *
GCStr_unicode(PyObject * self, PyObject * args)
{
    return unicode_FromCstruct((unistr_t *) (GCStr_AS_CSTRUCT(self)));
}

static PyMethodDef GCStr_methods[] = {
    {"__copy__",
     GCStr_Copy, METH_NOARGS,
     GCStr_Copy__doc__},
    {"flag",
     GCStr_flag, METH_VARARGS,
     GCStr_flag__doc__},
    {"__radd__",
     GCStr_radd, METH_VARARGS,
     "x.__radd__(y) <==> y+x"},
    {"__unicode__",
     GCStr_unicode, METH_NOARGS,
     "x.__unicode__() <==> unicode(x)\n\
      Convert grapheme cluster string to Unicode string."},
    {NULL}			/* Sentinel */
};


static PyTypeObject GCStr_Type = {
#if PY_MAJOR_VERSION >= 3
    PyVarObject_HEAD_INIT(NULL, 0)
#else				/* PY_MAJOR_VERSION */
    PyObject_HEAD_INIT(NULL)
    0,				/*ob_size */
#endif				/* PY_MAJOR_VERSION */
    "_textseg.GCStr",		/*tp_name */
    sizeof(GCStrObject),	/*tp_basicsize */
    0,				/*tp_itemsize */
    GCStr_dealloc,		/*tp_dealloc */
    0,				/*tp_print */
    0,				/*tp_getattr */
    0,				/*tp_setattr */
    0,				/*tp_compare */
    0,				/*tp_repr */
    0,				/*tp_as_number */
    &GCStr_as_sequence,		/*tp_as_sequence */
    &GCStr_as_mapping,		/*tp_as_mapping */
    0,				/*tp_hash */
    0,				/*tp_call */
#if PY_MAJOR_VERSION >= 3
    &GCStr_Str,			/*tp_str */
#else				/* PY_MAJOR_VERSION */
    0,				/*tp_str */
#endif				/* PY_MAJOR_VERSION */
    0,				/*tp_getattro */
    0,				/*tp_setattro */
    0,				/*tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,	/*tp_flags */
    "GCStr objects",		/* tp_doc */
    0,				/* tp_traverse */
    0,				/* tp_clear */
    GCStr_compare,		/* tp_richcompare */
    0,				/* tp_weaklistoffset */
    0,				/* tp_iter */
    0,				/* tp_iternext */
    GCStr_methods,		/* tp_methods */
    0,				/* tp_members */
    GCStr_getseters,		/* tp_getset */
    0,				/* tp_base */
    0,				/* tp_dict */
    0,				/* tp_descr_get */
    0,				/* tp_descr_set */
    0,				/* tp_dictoffset */
    0,				/* tp_init */
    0,				/* tp_alloc */
    GCStr_new,			/* tp_new */
};


/**
 * Initialize module
 */

static PyMethodDef module_methods[] = {
    {NULL}			/* Sentinel */
};

PyDoc_STRVAR(module__doc__, "\
Module for text segmentation.");

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef textseg_def = {
    PyModuleDef_HEAD_INIT,
    "_textseg",
    module__doc__,
    -1,
    module_methods,
    NULL, NULL, NULL, NULL
};

#define INITERROR return NULL
PyMODINIT_FUNC
PyInit__textseg(void)
#else				/* PY_MAJOR_VERSION */

#define INITERROR return
void
init_textseg(void)
#endif				/* PY_MAJOR_VERSION */
{
    PyObject *m;

    if ((LineBreakException =
	 PyErr_NewException("_textseg.LineBreakException", NULL, NULL))
	== NULL)
	INITERROR;
    if (PyType_Ready(&LineBreak_Type) < 0) {
	Py_DECREF(LineBreakException);
	INITERROR;
    }
    if (PyType_Ready(&GCStr_Type) < 0) {
	Py_DECREF(LineBreakException);
	INITERROR;
    }
    if (PyType_Ready(&TDict_Type) < 0) {
	Py_DECREF(LineBreakException);
	INITERROR;
    }
#if PY_MAJOR_VERSION >= 3
    m = PyModule_Create(&textseg_def);
#else				/* PY_MAJOR_VERSION */
    m = Py_InitModule3("_textseg", module_methods, module__doc__);
#endif				/* PY_MAJOR_VERSION */
    if (m == NULL) {
	Py_DECREF(LineBreakException);
	INITERROR;
    }

    Py_INCREF(LineBreakException);
    PyModule_AddObject(m, "LineBreakException", LineBreakException);
    Py_INCREF(&LineBreak_Type);
    PyModule_AddObject(m, "LineBreak", (PyObject *) & LineBreak_Type);
    Py_INCREF(&GCStr_Type);
    PyModule_AddObject(m, "GCStr", (PyObject *) & GCStr_Type);
    Py_INCREF(&TDict_Type);
    PyModule_AddObject(m, "TailoringDict", (PyObject *) & TDict_Type);

    TEXTSEG_SIMPLE = PyString_FromString("simple");
    TEXTSEG_NEWLINE = PyString_FromString("newline");
    TEXTSEG_TRIM = PyString_FromString("trim");
    TEXTSEG_BREAKURI = PyString_FromString("breakuri");
    TEXTSEG_NONBREAKURI = PyString_FromString("nonbreakuri");
    TEXTSEG_UAX11 = PyString_FromString("uax11");
    TEXTSEG_FORCE = PyString_FromString("force");
    TEXTSEG_RAISE = PyString_FromString("raise");

#if PY_MAJOR_VERSION >= 3
    return m;
#endif				/* PY_MAJOR_VERSION */
}
