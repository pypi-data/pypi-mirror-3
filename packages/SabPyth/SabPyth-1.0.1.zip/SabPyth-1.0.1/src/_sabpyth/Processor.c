#include "Sablotmodule.h"


static PyMethodDef pys_Processor_methods[] = {
    {"run", (PyCFunction)pys_Processor_run, METH_VARARGS},
    {"getResultArg", (PyCFunction)pys_Processor_getResultArg, METH_VARARGS},
    {"freeResultArgs", (PyCFunction)pys_Processor_freeResultArgs, METH_VARARGS},
    {"regHandler", (PyCFunction)pys_Processor_regHandler, METH_VARARGS},
    {"unregHandler", (PyCFunction)pys_Processor_unregHandler, METH_VARARGS},
    {"setBase", (PyCFunction)pys_Processor_setBase, METH_VARARGS},
    {"setBaseForScheme", (PyCFunction)pys_Processor_setBaseForScheme, METH_VARARGS},
    {"setLog", (PyCFunction)pys_Processor_setLog, METH_VARARGS},
    {"clearError", (PyCFunction)pys_Processor_clearError, METH_VARARGS},
    {NULL, NULL}
} ;


staticforward PyTypeObject pys_Processor_Type;


/* -------------------- */


static void initHandlerList(Pys_HandlerList *hl)
{
    hl->handlers = NULL;
    hl->count = hl->size = 0;
}

static void destroyHandlerList(Pys_HandlerList *hl)
{
    int i;
    
    for (i = 0; i < hl->count; ++i)
	Py_XDECREF(hl->handlers[i].pyhandler);
    if (hl->handlers != NULL)
	free(hl->handlers);
}

static int addHandler(Pys_HandlerList *hl,
		      HandlerType type, PyObject *pyhandler)
{
    if (hl->size <= hl->count) {
	hl->size += 20;
	hl->handlers = realloc(hl->handlers, hl->size * sizeof(Pys_Handler));
    }
    if (hl->handlers == NULL)
	return -1;
    hl->handlers[hl->count].type = type;
    hl->handlers[hl->count].pyhandler = pyhandler;
    Py_INCREF(pyhandler);
    return hl->count++;
}

static int findHandler(Pys_HandlerList *hl,
		       HandlerType type, PyObject *pyhandler)
{
    int i;

    for (i = 0; i < hl->count; ++i)
	if (hl->handlers[i].type == type
	    && hl->handlers[i].pyhandler == pyhandler)
	    return i;
    return -1;
}

static void removeHandler(Pys_HandlerList *hl, int i)
{
    int j;

    Py_XDECREF(hl->handlers[i].pyhandler);
    --hl->count;
    for (j = i; j < hl->count; ++j)
	hl->handlers[j] = hl->handlers[j + 1];
}


/* -------------------- */

static void pys_freeAllBuffers(Pys_Processor *self);

Pys_Processor *pys_Processor_new(void)
{
    Pys_Processor *self = PyObject_NEW(Pys_Processor, &pys_Processor_Type);
    int err;

    if (self == NULL)
	return NULL;
    initHandlerList(&self->hl);
    self->bufcount = self->bufsize = 0;
    self->buflist = NULL;
    err = SablotCreateProcessor(&(self->processor));
    if (err) {
	/* free our stuff here?  make sure dealloc() does not SablotDestroy().
	 */
	return (Pys_Processor *)pys_sablotError(err);
    } else {
	SablotSetInstanceData(self->processor, self);
	return self;
    }
}


void pys_Processor_dealloc(Pys_Processor *self)
{
    int err;

    err = SablotDestroyProcessor(self->processor);
    destroyHandlerList(&self->hl);
    pys_freeAllBuffers(self);
    PyObject_Del(self);
}


PyObject *pys_Processor_getattr(Pys_Processor *self, char *name)
{
    return Py_FindMethod(pys_Processor_methods, (PyObject *)self, name);
}


static char **makedbllist(PyObject *seq);
static void freedbllist(char **dbllist);


static char **makedbllist(PyObject *seq)
{
    int i, n;
    char **dbllist, *s1, *s2;
    PyObject *o;

    if (!PySequence_Check(seq)) {
	PyErr_SetString(PyExc_TypeError, "sequence arg expected");
	return NULL;
    }
    n = PySequence_Length(seq);
    dbllist = malloc((n + 1) * 2 * sizeof(char *));
    if (dbllist == NULL) {
	PyErr_NoMemory();
	return NULL;
    }
    for (i = 0; i < n; ++i) {
	dbllist[2 * i] = dbllist[2 * i + 1] = NULL;
	o = PySequence_GetItem(seq, i);
	if (!PyArg_ParseTuple(o, "ss", &s1, &s2)) {
	    Py_DECREF(o);
	    freedbllist(dbllist);
	    return NULL;
	}
	dbllist[2 * i] = s1; /* strdup(s1); */
	dbllist[2 * i + 1] = s2; /* strdup(s2); */
	Py_DECREF(o);
    }
    dbllist[2 * n] = dbllist[2 * n + 1] = NULL;
    return dbllist;
}


static void freedbllist(char **dbllist)
{
/*      int i; */

    if (dbllist) {
/*  	for (i = 0; dbllist[i] || dbllist[i + 1]; i += 2) { */
/*  	    if (dbllist[i]) */
/*  		free(dbllist[i]); */
/*  	    if (dbllist[i + 1]) */
/*  		free(dbllist[i + 1]); */
/*  	} */
	free(dbllist);
    }
}


PyObject *pys_Processor_run(Pys_Processor *self, PyObject *args)
{
    int err;
    char *sheeturi, *inputuri, *resulturi, **params = NULL, **arguments = NULL;
    PyObject *pyparams, *pyargs, *res;

    if (!PyArg_ParseTuple(args, "sssOO", &sheeturi, &inputuri, &resulturi,
			  &pyparams, &pyargs))
	return NULL;
    params = makedbllist(pyparams);
    arguments = makedbllist(pyargs);
    if (params == NULL || arguments == NULL)
	res = NULL;
    else {
	err = SablotRunProcessor(self->processor,
				 sheeturi, inputuri, resulturi,
				 params, arguments);
	if (err)
	    res = pys_sablotError(err);
	else if (PyErr_Occurred())
	    res = NULL;
	else {
	    Py_INCREF(Py_None);
	    res = Py_None;
	}
    }
    freedbllist(params);
    freedbllist(arguments);
    return res;
}


PyObject *pys_Processor_getResultArg(Pys_Processor *self, PyObject *args)
{
    int err;
    char *arguri, *argval;
    PyObject *res;

    if (!PyArg_ParseTuple(args, "s", &arguri))
	return NULL;
    argval = NULL;
    err = SablotGetResultArg(self->processor, arguri, &argval);
    if (err)
	res = pys_sablotError(err);
    else if (argval != NULL)
	res = PyString_FromString(argval);
    else {
	Py_INCREF(Py_None);
	res = Py_None;
    }
    if (argval != NULL)
	SablotFree(argval);
    return res;
}


PyObject *pys_Processor_freeResultArgs(Pys_Processor *self, PyObject *args)
{
    int err;

    if (!PyArg_ParseTuple(args, ""))
	return NULL;
    if ((err = SablotFreeResultArgs(self->processor)))
	return pys_sablotError(err);
    Py_INCREF(Py_None);
    return Py_None;
}


PyObject *pys_Processor_regHandler(Pys_Processor *self, PyObject *args)
{
    HandlerType type;
    PyObject *pyhandler;
    void *handler;

    if (!PyArg_ParseTuple(args, "iO!", &type, &PyInstance_Type, &pyhandler))
	return NULL;
    handler = pys_handler(type);
    if (handler != NULL) {
	addHandler(&self->hl, type, pyhandler);
	SablotRegHandler(self->processor, type, handler, pyhandler);
    } else
	return pys_makeSablotError(-1, "Handlers of this type are not implemented in the Sab-pyth");
    Py_INCREF(Py_None);
    return Py_None;
}


PyObject *pys_Processor_unregHandler(Pys_Processor *self, PyObject *args)
{
    HandlerType type;
    void *handler;
    PyObject *pyhandler;
    int i;

    if (!PyArg_ParseTuple(args, "iO!", &type, &PyInstance_Type, &pyhandler))
	return NULL;
    i = findHandler(&self->hl, type, pyhandler);
    if (i >= 0) {
	type = self->hl.handlers[i].type;
	handler = pys_handler(type);
	SablotUnregHandler(self->processor, type,
			   handler,
			   pyhandler);
	removeHandler(&self->hl, i);
    }
    Py_INCREF(Py_None);
    return Py_None;
}


PyObject *pys_Processor_setBase(Pys_Processor *self, PyObject *args)
{
    char *base;
    int err;

    if (!PyArg_ParseTuple(args, "s", &base))
	return NULL;
    if ((err = SablotSetBase(self->processor, base)))
	return pys_sablotError(err);
    Py_INCREF(Py_None);
    return Py_None;
}


PyObject *pys_Processor_setBaseForScheme(Pys_Processor *self, PyObject *args)
{
    char *scheme, *base;
    int err;

    if (!PyArg_ParseTuple(args, "ss", &scheme, &base))
	return NULL;
    if ((err = SablotSetBaseForScheme(self->processor, scheme, base)))
	return pys_sablotError(err);
    Py_INCREF(Py_None);
    return Py_None;
}


PyObject *pys_Processor_setLog(Pys_Processor *self, PyObject *args)
{
    char *logfn;
    int err, loglevel;

    if (!PyArg_ParseTuple(args, "si", &logfn, &loglevel))
	return NULL;
    if ((err = SablotSetLog(self->processor, logfn, loglevel)))
	return pys_sablotError(err);
    Py_INCREF(Py_None);
    return Py_None;
}


PyObject *pys_Processor_clearError(Pys_Processor *self, PyObject *args)
{
    int err;

    if (!PyArg_ParseTuple(args, ""))
	return NULL;
    if ((err = SablotClearError(self->processor)))
	return pys_sablotError(err);
    Py_INCREF(Py_None);
    return Py_None;
}


void pys_keepBuffer(Pys_Processor *self, PyObject *buffer)
{
    if (self->bufsize <= self->bufcount) {
	self->bufsize += 20;
	self->buflist = (PyObject **)realloc(self->buflist,
					     self->bufsize
					     * sizeof(PyObject *));
    }
    if (self->buflist == NULL)
	return ;
    self->buflist[self->bufcount++] = buffer;
}

void pys_freeBuffer(Pys_Processor *self, char *buffer)
{
    int i;

    for (i = 0; i < self->bufcount; ++i)
	if (PyString_AsString(self->buflist[i]) == buffer) {
	    Py_DECREF(self->buflist[i]);
	    --self->bufcount;
	    while (i < self->bufcount) {
		self->buflist[i] = self->buflist[i + 1];
		++i;
	    }
	    return ;
	}
}

static void pys_freeAllBuffers(Pys_Processor *self)
{
    int i;

    for (i = 0; i < self->bufcount; ++i)
	Py_XDECREF(self->buflist[i]);
    if (self->buflist)
	free(self->buflist);
    self->bufsize = self->bufcount = 0;
}

static PyTypeObject pys_Processor_Type = {
    PyObject_HEAD_INIT(NULL)
	0,					/*ob_size*/
	"SablotronProcessor",			/*tp_name*/
	sizeof(Pys_Processor),			/*tp_basicsize*/
	0,					/*tp_itemsize*/
	/* methods */
	(destructor)pys_Processor_dealloc,	/*tp_dealloc*/
	0,					/*tp_print*/
	(getattrfunc)pys_Processor_getattr,	/*tp_getattr*/
	0,					/*tp_setattr*/
	0,					/*tp_compare*/
	0,					/*tp_repr*/
	0,					/*tp_as_number*/
	0,					/*tp_as_sequence*/
	0,					/*tp_as_mapping*/
	0,					/*tp_hash*/
};

void init_Processor_Type(void)
{
	pys_Processor_Type.ob_type = &PyType_Type;
}
