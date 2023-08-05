cimport numpy as np
cimport cython

from numpy cimport *

from cpython cimport (PyDict_New, PyDict_GetItem, PyDict_SetItem,
                      PyDict_Contains, PyDict_Keys,
                      Py_INCREF, PyTuple_SET_ITEM,
                      PyTuple_SetItem,
                      PyTuple_New)
from cpython cimport PyFloat_Check

import numpy as np
isnan = np.isnan
cdef double NaN = <double> np.NaN
cdef double nan = NaN

from datetime import datetime as pydatetime

cdef inline int int_max(int a, int b): return a if a >= b else b
cdef inline int int_min(int a, int b): return a if a <= b else b

ctypedef unsigned char UChar

cdef int is_contiguous(ndarray arr):
    return np.PyArray_CHKFLAGS(arr, np.NPY_C_CONTIGUOUS)

cdef int _contiguous_check(ndarray arr):
    if not is_contiguous(arr):
        raise ValueError('Tried to use data field on non-contiguous array!')

cdef int16_t *get_int16_ptr(ndarray arr):
    _contiguous_check(arr)

    return <int16_t *> arr.data

cdef int32_t *get_int32_ptr(ndarray arr):
    _contiguous_check(arr)

    return <int32_t *> arr.data

cdef int64_t *get_int64_ptr(ndarray arr):
    _contiguous_check(arr)

    return <int64_t *> arr.data

cdef double_t *get_double_ptr(ndarray arr):
    _contiguous_check(arr)

    return <double_t *> arr.data

cimport util

cdef extern from "math.h":
    double sqrt(double x)
    double fabs(double)

cdef extern from "datetime.h":

    ctypedef class datetime.datetime [object PyDateTime_DateTime]:
        # cdef int *data
        # cdef long hashcode
        # cdef char hastzinfo
        pass

    int PyDateTime_GET_YEAR(datetime o)
    int PyDateTime_GET_MONTH(datetime o)
    int PyDateTime_GET_DAY(datetime o)
    int PyDateTime_DATE_GET_HOUR(datetime o)
    int PyDateTime_DATE_GET_MINUTE(datetime o)
    int PyDateTime_DATE_GET_SECOND(datetime o)
    int PyDateTime_DATE_GET_MICROSECOND(datetime o)
    int PyDateTime_TIME_GET_HOUR(datetime o)
    int PyDateTime_TIME_GET_MINUTE(datetime o)
    int PyDateTime_TIME_GET_SECOND(datetime o)
    int PyDateTime_TIME_GET_MICROSECOND(datetime o)
    bint PyDateTime_Check(object o)
    void PyDateTime_IMPORT()

# import datetime C API
PyDateTime_IMPORT

# initialize numpy
import_array()


cpdef map_indices_list(list index):
    '''
    Produce a dict mapping the values of the input array to their respective
    locations.

    Example:
        array(['hi', 'there']) --> {'hi' : 0 , 'there' : 1}

    Better to do this with Cython because of the enormous speed boost.
    '''
    cdef Py_ssize_t i, length
    cdef dict result = {}

    length = len(index)

    for i from 0 <= i < length:
        result[index[i]] = i

    return result


from libc.stdlib cimport malloc, free

cdef class MultiMap:
    '''
    Need to come up with a better data structure for multi-level indexing
    '''

    cdef:
        dict store
        Py_ssize_t depth, length

    def __init__(self, list label_arrays):
        cdef:
            int32_t **ptr
            Py_ssize_t i

        self.depth = len(label_arrays)
        self.length = len(label_arrays[0])
        self.store = {}

        ptr = <int32_t**> malloc(self.depth * sizeof(int32_t*))

        for i in range(self.depth):
            ptr[i] = <int32_t*> (<ndarray> label_arrays[i]).data

        free(ptr)

    cdef populate(self, int32_t **ptr):
        cdef Py_ssize_t i, j
        cdef int32_t* buf
        cdef dict level

        for i from 0 <= i < self.length:

            for j from 0 <= j < self.depth - 1:
                pass

    cpdef get(self, tuple key):
        cdef Py_ssize_t i
        cdef dict level = self.store

        for i from 0 <= i < self.depth:
            if i == self.depth - 1:
                return level[i]
            else:
                level = level[i]

        raise KeyError(key)


def isAllDates(ndarray[object, ndim=1] arr):
    cdef int i, size = len(arr)
    cdef object date

    if size == 0:
        return False

    for i from 0 <= i < size:
        date = arr[i]

        if not PyDateTime_Check(date):
            return False

    return True

def ismember(ndarray arr, set values):
    '''
    Checks whether

    Parameters
    ----------
    arr : ndarray
    values : set

    Returns
    -------
    ismember : ndarray (boolean dtype)
    '''
    cdef:
        Py_ssize_t i, n
        flatiter it
        ndarray[uint8_t] result
        object val

    it = <flatiter> PyArray_IterNew(arr)
    n = len(arr)
    result = np.empty(n, dtype=np.uint8)
    for i in range(n):
        val = PyArray_GETITEM(arr, PyArray_ITER_DATA(it))
        if val in values:
            result[i] = 1
        else:
            result[i] = 0
        PyArray_ITER_NEXT(it)

    return result.view(np.bool_)

def map_infer(ndarray arr, object f):
    '''
    Substitute for np.vectorize with pandas-friendly dtype inference

    Parameters
    ----------
    arr : ndarray
    f : function

    Returns
    -------
    mapped : ndarray
    '''
    cdef:
        Py_ssize_t i, n
        flatiter it
        ndarray[object] result
        object val

    it = <flatiter> PyArray_IterNew(arr)
    n = len(arr)
    result = np.empty(n, dtype=object)
    for i in range(n):
        val = PyArray_GETITEM(arr, PyArray_ITER_DATA(it))
        result[i] = f(val)
        PyArray_ITER_NEXT(it)

    return maybe_convert_objects(result)

#----------------------------------------------------------------------
# datetime / io related

cdef int _EPOCH_ORD = 719163

from datetime import date as pydate

cdef inline int64_t gmtime(object date):
    cdef int y, m, d, h, mn, s, days

    y = PyDateTime_GET_YEAR(date)
    m = PyDateTime_GET_MONTH(date)
    d = PyDateTime_GET_DAY(date)
    h = PyDateTime_DATE_GET_HOUR(date)
    mn = PyDateTime_DATE_GET_MINUTE(date)
    s = PyDateTime_DATE_GET_SECOND(date)

    days = pydate(y, m, 1).toordinal() - _EPOCH_ORD + d - 1
    return ((<int64_t> (((days * 24 + h) * 60 + mn))) * 60 + s) * 1000

cpdef object to_datetime(int64_t timestamp):
    return pydatetime.utcfromtimestamp(timestamp / 1000.0)

cpdef object to_timestamp(object dt):
    return gmtime(dt)

def array_to_timestamp(ndarray[object, ndim=1] arr):
    cdef int i, n
    cdef ndarray[int64_t, ndim=1] result

    n = len(arr)
    result = np.empty(n, dtype=np.int64)

    for i from 0 <= i < n:
        result[i] = gmtime(arr[i])

    return result

def array_to_datetime(ndarray[int64_t, ndim=1] arr):
    cdef int i, n
    cdef ndarray[object, ndim=1] result

    n = len(arr)
    result = np.empty(n, dtype=object)

    for i from 0 <= i < n:
        result[i] = to_datetime(arr[i])

    return result

#----------------------------------------------------------------------
# isnull / notnull related

cdef double INF = <double> np.inf
cdef double NEGINF = -INF

cdef inline _checknull(object val):
    return val is None or val != val

cpdef checknull(object val):
    if isinstance(val, (float, np.floating)):
        return val != val or val == INF or val == NEGINF
    else:
        return _checknull(val)

def isnullobj(ndarray[object] arr):
    cdef Py_ssize_t i, n
    cdef object val
    cdef ndarray[uint8_t] result

    n = len(arr)
    result = np.zeros(n, dtype=np.uint8)
    for i from 0 <= i < n:
        val = arr[i]
        if _checknull(val):
            result[i] = 1
    return result.view(np.bool_)

def list_to_object_array(list obj):
    '''
    Convert list to object ndarray. Seriously can't believe I had to write this
    function
    '''
    cdef:
        Py_ssize_t i, n
        ndarray[object] arr

    n = len(obj)
    arr = np.empty(n, dtype=object)

    for i from 0 <= i < n:
        arr[i] = obj[i]

    return arr


@cython.wraparound(False)
@cython.boundscheck(False)
def fast_unique(ndarray[object] values):
    cdef:
        Py_ssize_t i, n = len(values)
        list uniques = []
        dict table = {}
        object val, stub = 0

    for i from 0 <= i < n:
        val = values[i]
        if val not in table:
            table[val] = stub
            uniques.append(val)
    try:
        uniques.sort()
    except Exception:
        pass

    return uniques

@cython.wraparound(False)
@cython.boundscheck(False)
def fast_unique_multiple(list arrays):
    cdef:
        ndarray[object] buf
        Py_ssize_t k = len(arrays)
        Py_ssize_t i, j, n
        list uniques = []
        dict table = {}
        object val, stub = 0

    for i from 0 <= i < k:
        buf = arrays[i]
        n = len(buf)
        for j from 0 <= j < n:
            val = buf[j]
            if val not in table:
                table[val] = stub
                uniques.append(val)
    try:
        uniques.sort()
    except Exception:
        pass

    return uniques

@cython.wraparound(False)
@cython.boundscheck(False)
def fast_unique_multiple_list(list lists):
    cdef:
        list buf
        Py_ssize_t k = len(lists)
        Py_ssize_t i, j, n
        list uniques = []
        dict table = {}
        object val, stub = 0

    for i from 0 <= i < k:
        buf = lists[i]
        n = len(buf)
        for j from 0 <= j < n:
            val = buf[j]
            if val not in table:
                table[val] = stub
                uniques.append(val)
    try:
        uniques.sort()
    except Exception:
        pass

    return uniques

def fast_zip(list ndarrays):
    '''
    For zipping multiple ndarrays into an ndarray of tuples
    '''
    cdef:
        Py_ssize_t i, j, k, n
        ndarray[object] result
        flatiter it
        object val, tup

    k = len(ndarrays)
    n = len(ndarrays[0])

    result = np.empty(n, dtype=object)

    # initialize tuples on first pass
    arr = ndarrays[0]
    it = <flatiter> PyArray_IterNew(arr)
    for i in range(n):
        val = PyArray_GETITEM(arr, PyArray_ITER_DATA(it))
        tup = PyTuple_New(k)

        PyTuple_SET_ITEM(tup, 0, val)
        Py_INCREF(val)
        result[i] = tup
        PyArray_ITER_NEXT(it)

    for j in range(1, k):
        arr = ndarrays[j]
        it = <flatiter> PyArray_IterNew(arr)
        if len(arr) != n:
            raise ValueError('all arrays but be same length')

        for i in range(n):
            val = PyArray_GETITEM(arr, PyArray_ITER_DATA(it))
            PyTuple_SET_ITEM(result[i], j, val)
            Py_INCREF(val)
            PyArray_ITER_NEXT(it)

    return result

cdef class cache_readonly(object):

    cdef readonly:
        object fget, name

    def __init__(self, func):
        self.fget = func
        self.name = func.__name__

    def __get__(self, obj, type):
        if obj is None:
            return self.fget

        # Get the cache or set a default one if needed

        cache = getattr(obj, '_cache', None)
        if cache is None:
            cache = obj._cache = {}

        if PyDict_Contains(cache, self.name):
            # not necessary to Py_INCREF
            val = <object> PyDict_GetItem(cache, self.name)
            return val
        else:
            val = self.fget(obj)
            PyDict_SetItem(cache, self.name, val)
            return val

cpdef is_array(object o):
    return np.PyArray_Check(o)


include "skiplist.pyx"
include "groupby.pyx"
include "moments.pyx"
include "reindex.pyx"
include "generated.pyx"
include "parsing.pyx"
include "reduce.pyx"
include "stats.pyx"
