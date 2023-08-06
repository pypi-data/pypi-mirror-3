#include "Sablotmodule.h"


static long pys_longResult(PyObject *pyres, long errdefault, long deflt)
{
    long res;

    if (pyres == NULL)
	return errdefault;
    if (PyInt_Check(pyres))
	res = PyInt_AsLong(pyres);
    else
	res = deflt;
    Py_DECREF(pyres);
    return res;
}

static int checkSchemeError(int errdefault, int deflt)
{
    /*
     * if the python handler has raised a Sablot.SchemeError exception,
     * try to get the return code of the handler from the error parameter
     * and clear the error condition
     */
    PyObject *errtype, *errvalue, *errtraceback, *args, *sargs;
    int errnum;

    if (PyErr_Occurred()) { /* this should be true because we are called only
			       after Python returned NULL */
	if (PyErr_ExceptionMatches(pys_schemeError)) {
	    PyErr_Fetch(&errtype, &errvalue, &errtraceback);
	    sargs = PyString_FromString("args");
	    if (sargs != NULL)
		args = PyObject_GetAttr(errvalue, sargs);
	    else
		args = NULL;
	    if (args && PyArg_ParseTuple(args, "i", &errnum))
		errdefault = errnum;
	    Py_XDECREF(sargs);
	    Py_XDECREF(args);
	    Py_XDECREF(errtype);
	    Py_XDECREF(errvalue);
	    Py_XDECREF(errtraceback);
	}
	return errdefault;
    } else
	return deflt;
}
	

int pys_hscheme_getAll(void *userData, SablotHandle processor_,
	   const char *scheme, const char *rest, 
		       char **buffer, int *byteCount)
{
    PyObject *pyhandler = (PyObject *)userData, *pyres;
    Pys_Processor *sp = SablotGetInstanceData(processor_);

    pyres =  PyObject_CallMethod(pyhandler, "getAll", "ssi",
				scheme, rest, *byteCount);
    if (pyres == NULL)
	return checkSchemeError(SH_ERR_NOT_OK, SH_ERR_NOT_OK);
    if (! PyString_Check(pyres)) {
	Py_DECREF(pyres);
	pys_makeSablotError(PYS_NOSTRING, "return type string expected");
	return 1;
    }
    *buffer = PyString_AsString(pyres);
    *byteCount = PyString_Size(pyres);
    pys_keepBuffer(sp, pyres);
    return SH_ERR_OK;
}


int pys_hscheme_freeMemory(void *userData, SablotHandle processor_,
		char *buffer)
{
    Pys_Processor *sp = SablotGetInstanceData(processor_);

    pys_freeBuffer(sp, buffer);
    return SH_ERR_OK;
}


int pys_hscheme_open(void *userData, SablotHandle processor_,
	  const char *scheme, const char *rest, int *handle)
{
    PyObject *pyhandler = (PyObject *)userData, *pyres;

    pyres =  PyObject_CallMethod(pyhandler, "open", "ss", scheme, rest);
    if (pyres == NULL)
	return checkSchemeError(SH_ERR_NOT_OK, SH_ERR_NOT_OK);
    if (! PyInt_Check(pyres)) {
	Py_DECREF(pyres);
	pys_makeSablotError(PYS_NOINT, "return type int expected");
	return 1;
    }
    *handle = (int)PyInt_AsLong(pyres);
    Py_DECREF(pyres);
    return SH_ERR_OK;
    /* catch some python error and return SH_ERR_UNSUPPORTED_SCHEME instead */
}


int pys_hscheme_get(void *userData, SablotHandle processor_,
	 int handle, char *buffer, int *byteCount)
{
    PyObject *pyhandler = (PyObject *)userData, *pyres;

    pyres =  PyObject_CallMethod(pyhandler, "get", "ii", handle, *byteCount);
    if (pyres == NULL)
	return checkSchemeError(SH_ERR_NOT_OK, SH_ERR_NOT_OK);
    if (! PyString_Check(pyres)) {
	Py_DECREF(pyres);
	pys_makeSablotError(PYS_NOSTRING, "return type string expected");
	return 1;
    }
    if (PyString_Size(pyres) > *byteCount) {
	Py_DECREF(pyres);
	pys_makeSablotError(PYS_TOOLONG, "return string too long");
	return 1;
    }
    *byteCount = PyString_Size(pyres);
    memcpy(buffer, PyString_AsString(pyres), *byteCount);
    Py_DECREF(pyres);
    return SH_ERR_OK;
}


int pys_hscheme_put(void *userData, SablotHandle processor_,
	 int handle, const char *buffer, int *byteCount)
{
    PyObject *pyhandler = (PyObject *)userData, *pyres;

    pyres =  PyObject_CallMethod(pyhandler, "put", "is#",
				handle, buffer, *byteCount);
    if (pyres == NULL)
	return checkSchemeError(SH_ERR_NOT_OK, SH_ERR_NOT_OK);
    Py_DECREF(pyres);
    return SH_ERR_OK;
}


int pys_hscheme_close(void *userData, SablotHandle processor_,
	   int handle)
{
    PyObject *pyhandler = (PyObject *)userData, *pyres;

    pyres =  PyObject_CallMethod(pyhandler, "close", "i", handle);
    if (pyres == NULL)
	return checkSchemeError(SH_ERR_NOT_OK, SH_ERR_NOT_OK);
    Py_DECREF(pyres);
    return SH_ERR_OK;
}


MH_ERROR pys_hmsg_makeCode(void *userData, SablotHandle processor_,
			   int severity, unsigned short facility,
			   unsigned short code)
{
    PyObject *pyhandler = (PyObject *)userData, *pyres;

    pyres = PyObject_CallMethod(pyhandler, "makeCode", "iii",
				(int)severity, (int)facility, (int)code);
    return (MH_ERROR)pys_longResult(pyres, 1, 0);
}

static PyObject *makeStringlist(const char **fields)
{
    int i, n;
    PyObject *pylist;

    for (n = 0; fields[n] != NULL; ++n)
	;
    pylist = PyList_New(n);
    if (pylist == NULL)
	return NULL;
    for (i = 0; i < n; ++i)
	PyList_SetItem(pylist, i, PyString_FromString(fields[i]));
    return pylist;
}

static MH_ERROR pys_hmsg_write(char *method,
			       void *userData, SablotHandle processor_,
			       MH_ERROR code, MH_LEVEL level, char **fields)
{
    PyObject *pyhandler = (PyObject *)userData, *pyres, *pyfields;

    pyfields = makeStringlist((const char **)fields);
    pyres = PyObject_CallMethod(pyhandler, method, "iiO",
				(int)code, (int)level, pyfields);
    Py_XDECREF(pyfields);
    return (MH_ERROR)pys_longResult(pyres, 1, 0);
}

MH_ERROR pys_hmsg_log(void *userData, SablotHandle processor_,
		      MH_ERROR code, MH_LEVEL level, char **fields)
{
    return pys_hmsg_write("log", userData, processor_, code, level, fields);
}

MH_ERROR pys_hmsg_error(void *userData, SablotHandle processor_,
		   MH_ERROR code, MH_LEVEL level, char **fields)
{
    return pys_hmsg_write("error", userData, processor_, code, level, fields);
}

void pys_misch_documentInfo(void* userData, SablotHandle processor_,
			    const char *contentType, const char *encoding)
{
    PyObject *pyhandler = (PyObject *)userData, *pyres;

    pyres = PyObject_CallMethod(pyhandler, "documentInfo", "ss",
				contentType, encoding);
    Py_XDECREF(pyres);
}


SAX_RETURN pys_saxh_startDocument(void* userData)
{
    PyObject *pyhandler = (PyObject *)userData, *pyres;

    pyres = PyObject_CallMethod(pyhandler, "startDocument", NULL);
    Py_XDECREF(pyres);
}

SAX_RETURN pys_saxh_startElement(void* userData, 
    const char* name, const char** atts)
{
    PyObject *pyhandler = (PyObject *)userData, *pyres, *pyatts;

    pyatts = makeStringlist(atts);
    pyres = PyObject_CallMethod(pyhandler, "startElement", "so", name, pyatts);
    Py_XDECREF(pyatts);
    Py_XDECREF(pyres);
}

SAX_RETURN pys_saxh_endElement(void* userData, const char* name)
{
    PyObject *pyhandler = (PyObject *)userData, *pyres;

    pyres = PyObject_CallMethod(pyhandler, "endElement", "s", name);
    Py_XDECREF(pyres);
}

SAX_RETURN pys_saxh_startNamespace(void* userData, 
    const char* prefix, const char* uri)
{
    PyObject *pyhandler = (PyObject *)userData, *pyres;

    pyres = PyObject_CallMethod(pyhandler, "startNamespace",
				"ss", prefix, uri);
    Py_XDECREF(pyres);
}

SAX_RETURN pys_saxh_endNamespace(void* userData, const char* prefix)
{
    PyObject *pyhandler = (PyObject *)userData, *pyres;

    pyres = PyObject_CallMethod(pyhandler, "endNamespace", "s", prefix);
    Py_XDECREF(pyres);
}

SAX_RETURN pys_saxh_comment(void* userData, 
    const char* contents)
{
    PyObject *pyhandler = (PyObject *)userData, *pyres;

    pyres = PyObject_CallMethod(pyhandler, "comment", "s", contents);
    Py_XDECREF(pyres);
}

SAX_RETURN pys_saxh_pi(void* userData, 
    const char* target, const char* contents)
{
    PyObject *pyhandler = (PyObject *)userData, *pyres;

    pyres = PyObject_CallMethod(pyhandler, "processingInstruction",
				"ss", target, contents);
    Py_XDECREF(pyres);
}

SAX_RETURN pys_saxh_characters(void* userData, 
    const char* contents, int length)
{
    PyObject *pyhandler = (PyObject *)userData, *pyres;

    pyres = PyObject_CallMethod(pyhandler, "characters",
				"s#", contents, length);
    Py_XDECREF(pyres);
}

SAX_RETURN pys_saxh_endDocument(void* userData)
{
    PyObject *pyhandler = (PyObject *)userData, *pyres;

    pyres = PyObject_CallMethod(pyhandler, "endDocument", NULL);
    Py_XDECREF(pyres);
}


SchemeHandler *pys_schemeHandler(void)
{
    static SchemeHandler sh;

    sh.getAll = pys_hscheme_getAll;
    sh.freeMemory = pys_hscheme_freeMemory;
    sh.open = pys_hscheme_open;
    sh.get = pys_hscheme_get;
    sh.put = pys_hscheme_put;
    sh.close = pys_hscheme_close;
    return &sh;
}

MessageHandler *pys_messageHandler(void)
{
    static MessageHandler mh;

    mh.makeCode = pys_hmsg_makeCode;
    mh.log = pys_hmsg_log;
    mh.error = pys_hmsg_error;
    return &mh;
}

MiscHandler *pys_miscHandler(void)
{
    static MiscHandler misch;

    misch.documentInfo = pys_misch_documentInfo;
    return &misch;
}

SAXHandler *pys_saxHandler(void)
{
    static SAXHandler sh;

    sh.startDocument = pys_saxh_startDocument;
    sh.endDocument = pys_saxh_endDocument;
    sh.startElement = pys_saxh_startElement;
    sh.endElement = pys_saxh_endElement;
    sh.startNamespace = pys_saxh_startNamespace;
    sh.endNamespace = pys_saxh_endNamespace;
    sh.comment = pys_saxh_comment;
    sh.processingInstruction = pys_saxh_pi;
    sh.characters = pys_saxh_characters;
    return &sh;
}

void *pys_handler(HandlerType type)
{
    switch (type) {
    case HLR_SCHEME:
	return (void *)pys_schemeHandler();
    case HLR_MESSAGE:
	return (void *)pys_messageHandler();
    case HLR_MISC:
	return (void *)pys_miscHandler();
    case HLR_SAX:
	return (void *)pys_saxHandler();
    default:
	return NULL;
    }
}
