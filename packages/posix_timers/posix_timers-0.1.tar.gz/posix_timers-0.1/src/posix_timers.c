#include <Python.h>
#include <time.h>

static PyObject *ptimers_timespec_as_rational(struct timespec *spec);

typedef struct {
    PyObject_HEAD
    clockid_t clk_id;
} ptimers_ClockObject;

static PyTypeObject ptimers_ClockType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "posix_timers.Clock",      /*tp_name*/
    sizeof(ptimers_ClockObject), /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,                         /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Identifies a posix clock.",   /*tp_doc*/
};

static PyObject *
ptimers_Clock_get_resolution(ptimers_ClockObject *self, void *closure)
{
    struct timespec resolution;

    if (clock_getres(self->clk_id, &resolution) == -1)
        return PyErr_SetFromErrno(PyExc_OSError);

    return ptimers_timespec_as_rational(&resolution);
}

static PyObject *
ptimers_clock_getres(PyObject *self, PyObject *args)
{
    ptimers_ClockObject *clock_object;

    if (!PyArg_ParseTuple(args, "O!:clock_getres", &ptimers_ClockType, &clock_object))
        return NULL;

    return ptimers_Clock_get_resolution(clock_object, NULL);
}

static PyObject *
ptimers_Clock_get_time(ptimers_ClockObject *self, void *closure)
{
    struct timespec result;

    if (clock_gettime(self->clk_id, &result) == -1)
        return PyErr_SetFromErrno(PyExc_OSError);

    return ptimers_timespec_as_rational(&result);
}

static PyObject *
ptimers_clock_gettime(PyObject *self, PyObject *args)
{
    ptimers_ClockObject *clock_object;

    if (!PyArg_ParseTuple(args, "O!:clock_gettime", &ptimers_ClockType, &clock_object))
        return NULL;

    return ptimers_Clock_get_time(clock_object, NULL);
}

static PyObject *
ptimers_timespec_as_rational(struct timespec *spec)
{
    double value = spec->tv_sec + spec->tv_nsec * 1e-9;
    return PyFloat_FromDouble(value);
}

int
ptimers_add_clock(PyObject *module, const char *name, clockid_t clk_id)
{
    ptimers_ClockObject *clock = (ptimers_ClockObject *) PyType_GenericAlloc(&ptimers_ClockType, 0);
    if (! clock)
        return -1;
    clock->clk_id = clk_id;
    return PyModule_AddObject(module, name, (PyObject *) clock);
}

static PyGetSetDef ptimers_Clock_getsetdef[] = {
    {"resolution",
        (getter) ptimers_Clock_get_resolution, NULL,
        "Resolution of the clock in seconds.", NULL },
    {"time",
        (getter) ptimers_Clock_get_time, NULL,
        "Time of this clock in seconds.", NULL },
    { NULL }  /* Sentinel */
};


static PyMethodDef ptimers_methods[] = {
    { "clock_getres", ptimers_clock_getres, METH_VARARGS,
        "Find the resolution of a posix clock." },
    { "clock_gettime", ptimers_clock_gettime, METH_VARARGS,
        "Read the value of a posix clock." },
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initposix_timers(void)
{
    PyObject *module = NULL;

    ptimers_ClockType.tp_getset = ptimers_Clock_getsetdef;
    if (PyType_Ready(&ptimers_ClockType) < 0)
        return;

    module = Py_InitModule3("posix_timers", ptimers_methods,
            "POSIX Timers API module");

#define ADD_CLOCK(name, clk_id) \
    if (ptimers_add_clock(module, name, clk_id) == -1) \
        return

    ADD_CLOCK("CLOCK_REALTIME", CLOCK_REALTIME);
    ADD_CLOCK("CLOCK_MONOTONIC", CLOCK_MONOTONIC);
    ADD_CLOCK("CLOCK_PROCESS_CPUTIME", CLOCK_PROCESS_CPUTIME_ID);
    ADD_CLOCK("CLOCK_THREAD_CPUTIME", CLOCK_THREAD_CPUTIME_ID );

    PyObject_SetAttrString(module, "Clock", (PyObject *) &ptimers_ClockType);
}

