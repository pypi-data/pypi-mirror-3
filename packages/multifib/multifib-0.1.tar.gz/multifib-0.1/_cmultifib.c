#include <Python.h>

/*
 * Calculate the n'th fibonacci number using a straight-
 * forward but inefficient recursive algorithm.
 */
unsigned long fib_recursive(unsigned long n)
{
    if (n <= 1)
        return n;

    return fib_recursive(n - 1) + fib_recursive(n - 2);
}

/*
 * CPython wrapper for fib_recursive; performs type and
 * boundary checking, then delegates to fib_recursive.
 */
static PyObject * _cmultifib_fib_recursive(PyObject *mod, PyObject *args)
{
    long n;

    if (!PyArg_ParseTuple(args, "k", &n)) {
        if (PySequence_Length(args) != 1)
            PyErr_SetString(PyExc_TypeError, "fib_recursive takes exactly one argument");
        else
            PyErr_SetString(PyExc_TypeError, "\"n\" must be an integer");
        return NULL;
    }

    if (n < 0) {
        PyErr_SetString(PyExc_ValueError, "cannot calculate negative fibonacci numbers");
        return NULL;
    }

    return PyInt_FromLong(fib_recursive(n));
}


/*
 * Calculate the n'th fibonacci number using a reasonably
 * efficient iterative algorithm.
 */
unsigned long fib_iterative(unsigned long n)
{
    unsigned long penultimate, ultimate, tmp, i;

    if (n <= 1)
        return n;

    penultimate = 0;
    ultimate = 1;

    for (i = 1; i < n; i++) {
        tmp = ultimate + penultimate;
        penultimate = ultimate;
        ultimate = tmp;
    }

    return ultimate;
}

/*
 * CPython wrapper for fib_iterative; performs type and
 * boundary checking, then delegates to fib_iterative.
 */
static PyObject * _cmultifib_fib_iterative(PyObject *mod, PyObject *args)
{
    long n;

    if (!PyArg_ParseTuple(args, "k", &n)) {
        if (PySequence_Length(args) != 1)
            PyErr_SetString(PyExc_TypeError, "fib_iterative takes exactly one argument");
        else
            PyErr_SetString(PyExc_TypeError, "\"n\" must be an integer");
        return NULL;
    }

    if (n < 0) {
        PyErr_SetString(PyExc_ValueError, "cannot calculate negative fibonacci numbers");
        return NULL;
    }

    return PyInt_FromLong(fib_iterative(n));
}

/*
 * List the functions in the module to be exported.
 */
static PyMethodDef CMultifibMethods[] = {
    {"fib_recursive", _cmultifib_fib_recursive, METH_VARARGS,
     "C implementation of a recursive fibonacci algorithm."},
    {"fib_iterative", _cmultifib_fib_iterative, METH_VARARGS,
     "C implementation of an iterative fibonacci algorithm."},
    {NULL, NULL, 0, NULL}
};


/*
 * Initialize the module by pointing CPython at the functions
 * we want made available to Python.
 */
PyMODINIT_FUNC init_cmultifib(void)
{
    PyObject *mod;

    mod = Py_InitModule("_cmultifib", CMultifibMethods);
    if (mod == NULL)
        return;
}

