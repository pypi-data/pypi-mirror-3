#ifndef __SABLOTMODULE_INCLUDED__
#  define __SABLOTMODULE_INCLUDED__

#ifndef BAD_STATIC_FORWARD
#    define BAD_STATIC_FORWARD 1
#endif

#include <Python.h>
#include <sablot.h>

/*
 * the version numbers should really be taken from elsewhere:
 * the Sablotron version should be somewhere in their headers
 * the Sabpyth-version should be taken from setup.py, maybe
 * by creating/updating a header in setup.py.
 */
#define SABPYTH_VERSION "Sabpyth 0.52"
#define SABLOTRON_VERSION "Sablotron 0.52"

extern PyObject *pys_error, *pys_schemeError;
PyObject *pys_sablotError(int code);
PyObject *pys_makeSablotError(int code, const char *text);

typedef struct {
    HandlerType type;
    PyObject *pyhandler;
} Pys_Handler;

typedef struct {
    int count, size;
    Pys_Handler *handlers;
} Pys_HandlerList;

typedef struct {
    PyObject_HEAD
    SablotHandle processor;
    Pys_HandlerList hl;
    int bufcount, bufsize;
    PyObject **buflist;
} Pys_Processor;

void init_Processor_Type(void);
Pys_Processor *pys_Processor_new(void);
void pys_Processor_dealloc(Pys_Processor *self);
PyObject *pys_Processor_getattr(Pys_Processor *self, char *name);
PyObject *pys_Processor_run(Pys_Processor *self, PyObject *args);
PyObject *pys_Processor_getResultArg(Pys_Processor *self, PyObject *args);
PyObject *pys_Processor_freeResultArgs(Pys_Processor *self, PyObject *args);
PyObject *pys_Processor_regHandler(Pys_Processor *self, PyObject *args);
PyObject *pys_Processor_unregHandler(Pys_Processor *self, PyObject *args);
PyObject *pys_Processor_setBase(Pys_Processor *self, PyObject *args);
PyObject *pys_Processor_setBaseForScheme(Pys_Processor *self, PyObject *args);
PyObject *pys_Processor_setLog(Pys_Processor *self, PyObject *args);
PyObject *pys_Processor_clearError(Pys_Processor *self, PyObject *args);
void pys_keepBuffer(Pys_Processor *self, PyObject *buffer);
void pys_freeBuffer(Pys_Processor *self, char *buffer);


void *pys_handler(HandlerType type);
void pys_keep_buffer(Pys_Processor *self, PyObject *buffer);
void pys_free_buffer(Pys_Processor *self, char *buffer);

#define PYS_ILL_HANDLER -1
#define PYS_NOSTRING -2
#define PYS_NOINT -3
#define PYS_TOOLONG -4

#endif
