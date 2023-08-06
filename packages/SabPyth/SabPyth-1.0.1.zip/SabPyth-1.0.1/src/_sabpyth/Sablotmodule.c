/* the Sablot module */

#include "Sablotmodule.h"


static PyObject *pys_processStrings(PyObject *self, PyObject *args)
{
    char *templ, *input, *ret;
    PyObject *retval;
    int err;
  
    if (!PyArg_ParseTuple(args, "ss:processStrings", &templ, &input))
	return NULL;      
    if ((err = SablotProcessStrings(templ, input, &ret)))
	return pys_sablotError(err);
    retval = PyString_FromString(ret);
    SablotFree(ret);
    return retval;
}

static char processStrings_doc[]
= "processStrings(styleSheet, xmlData) -> outputString";


static PyObject *pys_CreateProcessor(PyObject *self, PyObject *args)
{
    Pys_Processor *po;

    if (!PyArg_ParseTuple(args, ":CreateProcessor"))
	return NULL;
    po = pys_Processor_new();
    return (PyObject *)po;
}

static char CreateProcessor_doc[] = "CreateProcessor() -> Processor_object";


static PyObject *pys_getMsgText(PyObject *self, PyObject *args)
{
    int code;

    if (!PyArg_ParseTuple(args, "i:getMsgText", &code))
	return NULL;
    return PyString_FromString(SablotGetMsgText(code));
}

static char getMsgText_doc[] = "getMsgText(int) -> string";


static PyMethodDef SablotMethods[] = {
    {"CreateProcessor", pys_CreateProcessor, 1, CreateProcessor_doc},
    {"getMsgText", pys_getMsgText, 1, getMsgText_doc},
    {"processStrings",  pys_processStrings, 1, processStrings_doc},
    {NULL,     NULL}        /* Sentinel */
};


PyObject *pys_error, *pys_schemeError;


static void setConstants(PyObject *d)
{
    struct {char *n; int v;} iconstants[] = {
	{"HLR_MESSAGE", HLR_MESSAGE},
	{"HLR_SCHEME", HLR_SCHEME},
	{"HLR_SAX", HLR_SAX},
	{"HLR_MISC", HLR_MISC},
	{"SH_ERR_OK", SH_ERR_OK},
	{"SH_ERR_NOT_OK", SH_ERR_NOT_OK},
	{"SH_ERR_UNSUPPORTED_SCHEME", SH_ERR_UNSUPPORTED_SCHEME},
	{"MH_FACILITY_SABLOTRON", MH_FACILITY_SABLOTRON},
	{"MH_LEVEL_DEBUG", MH_LEVEL_DEBUG},
	{"MH_LEVEL_INFO", MH_LEVEL_INFO},
	{"MH_LEVEL_WARN", MH_LEVEL_WARN},
	{"MH_LEVEL_ERROR", MH_LEVEL_ERROR},
	{"MH_LEVEL_CRITICAL", MH_LEVEL_CRITICAL},
	{NULL, 0}};
    struct {char *n; char *v;} sconstants[] = {
        {"SABLOTRON_VERSION", SABLOTRON_VERSION},
        {"SABPYTH_VERSION", SABPYTH_VERSION},
        {NULL, NULL}};
    int i;
    PyObject *o;

    for (i = 0; iconstants[i].n != NULL; ++i) {
	o = PyInt_FromLong((long)iconstants[i].v);
	PyDict_SetItemString(d, iconstants[i].n, o);
	Py_XDECREF(o);
    }
    for (i = 0; sconstants[i].n != NULL; ++i) {
	o = PyString_FromString(sconstants[i].v);
	PyDict_SetItemString(d, sconstants[i].n, o);
	Py_XDECREF(o);
    }
}

void init_sablot(void)
{
    PyObject *m, *d;

    init_Processor_Type();
    m = Py_InitModule("_sablot", SablotMethods);
    d = PyModule_GetDict(m);
    pys_error = PyErr_NewException("Sablot.error", NULL, NULL);
    PyDict_SetItemString(d, "error", pys_error);
    Py_DECREF(pys_error);
    pys_schemeError = PyErr_NewException("Sablot.SchemeHandlerError",
                                         NULL, NULL);
    PyDict_SetItemString(d, "SchemeHandlerError", pys_schemeError);
    Py_DECREF(pys_schemeError);
    setConstants(d);
}

PyObject *pys_sablotError(int code)
{
    return pys_makeSablotError(code, SablotGetMsgText(code));
}

PyObject *pys_makeSablotError(int code, const char *text)
{
    PyObject *errcode;

    if (! PyErr_Occurred() && (errcode = Py_BuildValue("(is)", code, text))) {
	PyErr_SetObject(pys_error, errcode);
	Py_DECREF(errcode);
    }
    return NULL;   
}
