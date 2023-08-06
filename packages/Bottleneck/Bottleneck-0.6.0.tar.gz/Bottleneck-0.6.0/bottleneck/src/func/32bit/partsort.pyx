# 32 bit version
"partsort auto-generated from template"
# Select smallest k elements code used for inner loop of partsort method:
# http://projects.scipy.org/numpy/attachment/ticket/1213/quickselect.pyx
# (C) 2009 Sturla Molden
# SciPy license 
#
# From the original C function (code in public domain) in:
#   Fast median search: an ANSI C implementation
#   Nicolas Devillard - ndevilla AT free DOT fr
#   July 1998
# which, in turn, took the algorithm from
#   Wirth, Niklaus
#   Algorithms + data structures = programs, p. 366
#   Englewood Cliffs: Prentice-Hall, 1976
#
# Adapted and expanded for Bottleneck:
# (C) 2011 Keith Goodman

def partsort(arr, n, axis=-1):
    """
    Partial sorting of array elements along given axis.
    
    A partially sorted array is one in which the `n` smallest values appear
    (in any order) in the first `n` elements. The remaining largest elements
    are also unordered. Due to the algorithm used (Wirth's method), the nth
    smallest element is in its sorted position (at index `n-1`).

    Shuffling the input array may change the output. The only guarantee is
    that the first `n` elements will be the `n` smallest and the remaining
    element will appear in the remainder of the output.

    This functions is not protected against NaN. Therefore, you may get
    unexpected results if the input contains NaN.

    Parameters
    ----------
    arr : array_like
        Input array. If `arr` is not an array, a conversion is attempted.
    n : int    
        The `n` smallest elements will appear (unordered) in the first `n`
        elements of the output array.
    axis : {int, None}, optional
        Axis along which the partial sort is performed. The default (axis=-1)
        is to sort along the last axis.

    Returns
    -------
    y : ndarray
        A partially sorted copy of the input array where the `n` smallest
        elements will appear (unordered) in the first `n` elements.
        
    See Also
    --------
    bottleneck.argpartsort: Indices that would partially sort an array
    
    Notes
    -----
    Unexpected results may occur if the input array contains NaN.

    Examples
    --------
    Create a numpy array:

    >>> a = np.array([1, 0, 3, 4, 2])
    
    Partially sort array so that the first 3 elements are the smallest 3
    elements (note, as in this example, that the smallest 3 elements may not
    be sorted):

    >>> bn.partsort(a, n=3)
    array([1, 0, 2, 4, 3])
    
    """
    func, arr = partsort_selector(arr, axis)
    return func(arr, n)

def partsort_selector(arr, axis):
    """
    Return partsort function and array that matches `arr` and `axis`.
    
    Under the hood Bottleneck uses a separate Cython function for each
    combination of ndim, dtype, and axis. A lot of the overhead in
    bn.partsort() is in checking that `axis` is within range, converting `arr`
    into an array (if it is not already an array), and selecting the function
    to use to partially sort.

    You can get rid of the overhead by doing all this before you, for example,
    enter an inner loop, by using the this function.

    Parameters
    ----------
    arr : array_like
        Input array. If `arr` is not an array, a conversion is attempted.
    axis : {int, None}
        Axis along which to partially sort.
    
    Returns
    -------
    func : function
        The partsort function that matches the number of dimensions and dtype
        of the input array and the axis along which you wish to partially
        sort.
    a : ndarray
        If the input array `arr` is not a ndarray, then `a` will contain the
        result of converting `arr` into a ndarray.

    Examples
    --------
    Create a numpy array:

    >>> arr = np.array([1, 0, 3, 4, 2])
    
    Obtain the function needed to partially sort `arr` along axis=0:

    >>> func, a = bn.func.partsort_selector(arr, axis=0)
    >>> func
    <function partsort_1d_int64_axis0>
    
    Use the returned function and array to partially sort:

    >>> func(a, n=3)
    array([1, 0, 2, 4, 3])

    """
    cdef np.ndarray a
    if type(arr) is np.ndarray:
        a = arr
    else:    
        a = np.array(arr, copy=False)
    cdef tuple key
    cdef int ndim = PyArray_NDIM(a)
    cdef int dtype = PyArray_TYPE(a)
    if axis is not None:
        if axis < 0:
            axis += ndim
    else:
        a = PyArray_Ravel(a, NPY_CORDER)
        axis = 0
        ndim = 1
    key = (ndim, dtype, axis)
    try:
        func = partsort_dict[key]
    except KeyError:
        if (axis < 0) or (axis >= ndim):
            raise ValueError("axis(=%d) out of bounds" % axis)
        try:
            func = partsort_slow_dict[axis]
        except KeyError:
            tup = (str(ndim), str(a.dtype), str(axis))
            raise TypeError("Unsupported ndim/dtype/axis (%s/%s/%s)." % tup)
    return func, a

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_1d_int32_axis0(np.ndarray[np.int32_t, ndim=1] a, int n):
    "Partial sort of 1d array with dtype=int32 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.int32_t x, tmp
    cdef np.ndarray[np.int32_t, ndim=1] b = PyArray_Copy(a)
    cdef Py_ssize_t i0
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    if n0 == 0:
        return b
    if (n < 1) or (n > n0):
        raise ValueError(PARTSORT_ERR_MSG % (n, n0))
    l = 0
    r = n0 - 1
    with nogil:       
        while l < r:
            x = b[k]
            i = l
            j = r
            while 1:
                while b[i] < x: i += 1
                while x < b[j]: j -= 1
                if i <= j:
                    tmp = b[i]
                    b[i] = b[j]
                    b[j] = tmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_1d_int64_axis0(np.ndarray[np.int64_t, ndim=1] a, int n):
    "Partial sort of 1d array with dtype=int64 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.int64_t x, tmp
    cdef np.ndarray[np.int64_t, ndim=1] b = PyArray_Copy(a)
    cdef Py_ssize_t i0
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    if n0 == 0:
        return b
    if (n < 1) or (n > n0):
        raise ValueError(PARTSORT_ERR_MSG % (n, n0))
    l = 0
    r = n0 - 1
    with nogil:       
        while l < r:
            x = b[k]
            i = l
            j = r
            while 1:
                while b[i] < x: i += 1
                while x < b[j]: j -= 1
                if i <= j:
                    tmp = b[i]
                    b[i] = b[j]
                    b[j] = tmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_2d_int32_axis0(np.ndarray[np.int32_t, ndim=2] a, int n):
    "Partial sort of 2d array with dtype=int32 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.int32_t x, tmp
    cdef np.ndarray[np.int32_t, ndim=2] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    if n0 == 0:
        return b
    if (n < 1) or (n > n0):
        raise ValueError(PARTSORT_ERR_MSG % (n, n0))
    for i1 in range(n1): 
        l = 0
        r = n0 - 1
        while l < r:
            x = b[k, i1]
            i = l
            j = r
            while 1:
                while b[i, i1] < x: i += 1
                while x < b[j, i1]: j -= 1
                if i <= j:
                    tmp = b[i, i1]
                    b[i, i1] = b[j, i1]
                    b[j, i1] = tmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_2d_int32_axis1(np.ndarray[np.int32_t, ndim=2] a, int n):
    "Partial sort of 2d array with dtype=int32 along axis=1."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.int32_t x, tmp
    cdef np.ndarray[np.int32_t, ndim=2] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    if n1 == 0:
        return b
    if (n < 1) or (n > n1):
        raise ValueError(PARTSORT_ERR_MSG % (n, n1))
    for i0 in range(n0): 
        l = 0
        r = n1 - 1
        while l < r:
            x = b[i0, k]
            i = l
            j = r
            while 1:
                while b[i0, i] < x: i += 1
                while x < b[i0, j]: j -= 1
                if i <= j:
                    tmp = b[i0, i]
                    b[i0, i] = b[i0, j]
                    b[i0, j] = tmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_2d_int64_axis0(np.ndarray[np.int64_t, ndim=2] a, int n):
    "Partial sort of 2d array with dtype=int64 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.int64_t x, tmp
    cdef np.ndarray[np.int64_t, ndim=2] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    if n0 == 0:
        return b
    if (n < 1) or (n > n0):
        raise ValueError(PARTSORT_ERR_MSG % (n, n0))
    for i1 in range(n1): 
        l = 0
        r = n0 - 1
        while l < r:
            x = b[k, i1]
            i = l
            j = r
            while 1:
                while b[i, i1] < x: i += 1
                while x < b[j, i1]: j -= 1
                if i <= j:
                    tmp = b[i, i1]
                    b[i, i1] = b[j, i1]
                    b[j, i1] = tmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_2d_int64_axis1(np.ndarray[np.int64_t, ndim=2] a, int n):
    "Partial sort of 2d array with dtype=int64 along axis=1."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.int64_t x, tmp
    cdef np.ndarray[np.int64_t, ndim=2] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    if n1 == 0:
        return b
    if (n < 1) or (n > n1):
        raise ValueError(PARTSORT_ERR_MSG % (n, n1))
    for i0 in range(n0): 
        l = 0
        r = n1 - 1
        while l < r:
            x = b[i0, k]
            i = l
            j = r
            while 1:
                while b[i0, i] < x: i += 1
                while x < b[i0, j]: j -= 1
                if i <= j:
                    tmp = b[i0, i]
                    b[i0, i] = b[i0, j]
                    b[i0, j] = tmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_3d_int32_axis0(np.ndarray[np.int32_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=int32 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.int32_t x, tmp
    cdef np.ndarray[np.int32_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    if n0 == 0:
        return b
    if (n < 1) or (n > n0):
        raise ValueError(PARTSORT_ERR_MSG % (n, n0))
    for i1 in range(n1):
        for i2 in range(n2):
            l = 0
            r = n0 - 1
            while l < r:
                x = b[k, i1, i2]
                i = l
                j = r
                while 1:
                    while b[i, i1, i2] < x: i += 1
                    while x < b[j, i1, i2]: j -= 1
                    if i <= j:
                        tmp = b[i, i1, i2]
                        b[i, i1, i2] = b[j, i1, i2]
                        b[j, i1, i2] = tmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_3d_int32_axis1(np.ndarray[np.int32_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=int32 along axis=1."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.int32_t x, tmp
    cdef np.ndarray[np.int32_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    if n1 == 0:
        return b
    if (n < 1) or (n > n1):
        raise ValueError(PARTSORT_ERR_MSG % (n, n1))
    for i0 in range(n0):
        for i2 in range(n2):
            l = 0
            r = n1 - 1
            while l < r:
                x = b[i0, k, i2]
                i = l
                j = r
                while 1:
                    while b[i0, i, i2] < x: i += 1
                    while x < b[i0, j, i2]: j -= 1
                    if i <= j:
                        tmp = b[i0, i, i2]
                        b[i0, i, i2] = b[i0, j, i2]
                        b[i0, j, i2] = tmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_3d_int32_axis2(np.ndarray[np.int32_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=int32 along axis=2."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.int32_t x, tmp
    cdef np.ndarray[np.int32_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    if n2 == 0:
        return b
    if (n < 1) or (n > n2):
        raise ValueError(PARTSORT_ERR_MSG % (n, n2))
    for i0 in range(n0):
        for i1 in range(n1):
            l = 0
            r = n2 - 1
            while l < r:
                x = b[i0, i1, k]
                i = l
                j = r
                while 1:
                    while b[i0, i1, i] < x: i += 1
                    while x < b[i0, i1, j]: j -= 1
                    if i <= j:
                        tmp = b[i0, i1, i]
                        b[i0, i1, i] = b[i0, i1, j]
                        b[i0, i1, j] = tmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_3d_int64_axis0(np.ndarray[np.int64_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=int64 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.int64_t x, tmp
    cdef np.ndarray[np.int64_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    if n0 == 0:
        return b
    if (n < 1) or (n > n0):
        raise ValueError(PARTSORT_ERR_MSG % (n, n0))
    for i1 in range(n1):
        for i2 in range(n2):
            l = 0
            r = n0 - 1
            while l < r:
                x = b[k, i1, i2]
                i = l
                j = r
                while 1:
                    while b[i, i1, i2] < x: i += 1
                    while x < b[j, i1, i2]: j -= 1
                    if i <= j:
                        tmp = b[i, i1, i2]
                        b[i, i1, i2] = b[j, i1, i2]
                        b[j, i1, i2] = tmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_3d_int64_axis1(np.ndarray[np.int64_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=int64 along axis=1."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.int64_t x, tmp
    cdef np.ndarray[np.int64_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    if n1 == 0:
        return b
    if (n < 1) or (n > n1):
        raise ValueError(PARTSORT_ERR_MSG % (n, n1))
    for i0 in range(n0):
        for i2 in range(n2):
            l = 0
            r = n1 - 1
            while l < r:
                x = b[i0, k, i2]
                i = l
                j = r
                while 1:
                    while b[i0, i, i2] < x: i += 1
                    while x < b[i0, j, i2]: j -= 1
                    if i <= j:
                        tmp = b[i0, i, i2]
                        b[i0, i, i2] = b[i0, j, i2]
                        b[i0, j, i2] = tmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_3d_int64_axis2(np.ndarray[np.int64_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=int64 along axis=2."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.int64_t x, tmp
    cdef np.ndarray[np.int64_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    if n2 == 0:
        return b
    if (n < 1) or (n > n2):
        raise ValueError(PARTSORT_ERR_MSG % (n, n2))
    for i0 in range(n0):
        for i1 in range(n1):
            l = 0
            r = n2 - 1
            while l < r:
                x = b[i0, i1, k]
                i = l
                j = r
                while 1:
                    while b[i0, i1, i] < x: i += 1
                    while x < b[i0, i1, j]: j -= 1
                    if i <= j:
                        tmp = b[i0, i1, i]
                        b[i0, i1, i] = b[i0, i1, j]
                        b[i0, i1, j] = tmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_1d_float32_axis0(np.ndarray[np.float32_t, ndim=1] a, int n):
    "Partial sort of 1d array with dtype=float32 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.float32_t x, tmp
    cdef np.ndarray[np.float32_t, ndim=1] b = PyArray_Copy(a)
    cdef Py_ssize_t i0
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    if n0 == 0:
        return b
    if (n < 1) or (n > n0):
        raise ValueError(PARTSORT_ERR_MSG % (n, n0))
    l = 0
    r = n0 - 1
    with nogil:       
        while l < r:
            x = b[k]
            i = l
            j = r
            while 1:
                while b[i] < x: i += 1
                while x < b[j]: j -= 1
                if i <= j:
                    tmp = b[i]
                    b[i] = b[j]
                    b[j] = tmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_1d_float64_axis0(np.ndarray[np.float64_t, ndim=1] a, int n):
    "Partial sort of 1d array with dtype=float64 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.float64_t x, tmp
    cdef np.ndarray[np.float64_t, ndim=1] b = PyArray_Copy(a)
    cdef Py_ssize_t i0
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    if n0 == 0:
        return b
    if (n < 1) or (n > n0):
        raise ValueError(PARTSORT_ERR_MSG % (n, n0))
    l = 0
    r = n0 - 1
    with nogil:       
        while l < r:
            x = b[k]
            i = l
            j = r
            while 1:
                while b[i] < x: i += 1
                while x < b[j]: j -= 1
                if i <= j:
                    tmp = b[i]
                    b[i] = b[j]
                    b[j] = tmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_2d_float32_axis0(np.ndarray[np.float32_t, ndim=2] a, int n):
    "Partial sort of 2d array with dtype=float32 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.float32_t x, tmp
    cdef np.ndarray[np.float32_t, ndim=2] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    if n0 == 0:
        return b
    if (n < 1) or (n > n0):
        raise ValueError(PARTSORT_ERR_MSG % (n, n0))
    for i1 in range(n1): 
        l = 0
        r = n0 - 1
        while l < r:
            x = b[k, i1]
            i = l
            j = r
            while 1:
                while b[i, i1] < x: i += 1
                while x < b[j, i1]: j -= 1
                if i <= j:
                    tmp = b[i, i1]
                    b[i, i1] = b[j, i1]
                    b[j, i1] = tmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_2d_float32_axis1(np.ndarray[np.float32_t, ndim=2] a, int n):
    "Partial sort of 2d array with dtype=float32 along axis=1."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.float32_t x, tmp
    cdef np.ndarray[np.float32_t, ndim=2] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    if n1 == 0:
        return b
    if (n < 1) or (n > n1):
        raise ValueError(PARTSORT_ERR_MSG % (n, n1))
    for i0 in range(n0): 
        l = 0
        r = n1 - 1
        while l < r:
            x = b[i0, k]
            i = l
            j = r
            while 1:
                while b[i0, i] < x: i += 1
                while x < b[i0, j]: j -= 1
                if i <= j:
                    tmp = b[i0, i]
                    b[i0, i] = b[i0, j]
                    b[i0, j] = tmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_2d_float64_axis0(np.ndarray[np.float64_t, ndim=2] a, int n):
    "Partial sort of 2d array with dtype=float64 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.float64_t x, tmp
    cdef np.ndarray[np.float64_t, ndim=2] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    if n0 == 0:
        return b
    if (n < 1) or (n > n0):
        raise ValueError(PARTSORT_ERR_MSG % (n, n0))
    for i1 in range(n1): 
        l = 0
        r = n0 - 1
        while l < r:
            x = b[k, i1]
            i = l
            j = r
            while 1:
                while b[i, i1] < x: i += 1
                while x < b[j, i1]: j -= 1
                if i <= j:
                    tmp = b[i, i1]
                    b[i, i1] = b[j, i1]
                    b[j, i1] = tmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_2d_float64_axis1(np.ndarray[np.float64_t, ndim=2] a, int n):
    "Partial sort of 2d array with dtype=float64 along axis=1."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.float64_t x, tmp
    cdef np.ndarray[np.float64_t, ndim=2] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    if n1 == 0:
        return b
    if (n < 1) or (n > n1):
        raise ValueError(PARTSORT_ERR_MSG % (n, n1))
    for i0 in range(n0): 
        l = 0
        r = n1 - 1
        while l < r:
            x = b[i0, k]
            i = l
            j = r
            while 1:
                while b[i0, i] < x: i += 1
                while x < b[i0, j]: j -= 1
                if i <= j:
                    tmp = b[i0, i]
                    b[i0, i] = b[i0, j]
                    b[i0, j] = tmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_3d_float32_axis0(np.ndarray[np.float32_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=float32 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.float32_t x, tmp
    cdef np.ndarray[np.float32_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    if n0 == 0:
        return b
    if (n < 1) or (n > n0):
        raise ValueError(PARTSORT_ERR_MSG % (n, n0))
    for i1 in range(n1):
        for i2 in range(n2):
            l = 0
            r = n0 - 1
            while l < r:
                x = b[k, i1, i2]
                i = l
                j = r
                while 1:
                    while b[i, i1, i2] < x: i += 1
                    while x < b[j, i1, i2]: j -= 1
                    if i <= j:
                        tmp = b[i, i1, i2]
                        b[i, i1, i2] = b[j, i1, i2]
                        b[j, i1, i2] = tmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_3d_float32_axis1(np.ndarray[np.float32_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=float32 along axis=1."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.float32_t x, tmp
    cdef np.ndarray[np.float32_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    if n1 == 0:
        return b
    if (n < 1) or (n > n1):
        raise ValueError(PARTSORT_ERR_MSG % (n, n1))
    for i0 in range(n0):
        for i2 in range(n2):
            l = 0
            r = n1 - 1
            while l < r:
                x = b[i0, k, i2]
                i = l
                j = r
                while 1:
                    while b[i0, i, i2] < x: i += 1
                    while x < b[i0, j, i2]: j -= 1
                    if i <= j:
                        tmp = b[i0, i, i2]
                        b[i0, i, i2] = b[i0, j, i2]
                        b[i0, j, i2] = tmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_3d_float32_axis2(np.ndarray[np.float32_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=float32 along axis=2."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.float32_t x, tmp
    cdef np.ndarray[np.float32_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    if n2 == 0:
        return b
    if (n < 1) or (n > n2):
        raise ValueError(PARTSORT_ERR_MSG % (n, n2))
    for i0 in range(n0):
        for i1 in range(n1):
            l = 0
            r = n2 - 1
            while l < r:
                x = b[i0, i1, k]
                i = l
                j = r
                while 1:
                    while b[i0, i1, i] < x: i += 1
                    while x < b[i0, i1, j]: j -= 1
                    if i <= j:
                        tmp = b[i0, i1, i]
                        b[i0, i1, i] = b[i0, i1, j]
                        b[i0, i1, j] = tmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_3d_float64_axis0(np.ndarray[np.float64_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=float64 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.float64_t x, tmp
    cdef np.ndarray[np.float64_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    if n0 == 0:
        return b
    if (n < 1) or (n > n0):
        raise ValueError(PARTSORT_ERR_MSG % (n, n0))
    for i1 in range(n1):
        for i2 in range(n2):
            l = 0
            r = n0 - 1
            while l < r:
                x = b[k, i1, i2]
                i = l
                j = r
                while 1:
                    while b[i, i1, i2] < x: i += 1
                    while x < b[j, i1, i2]: j -= 1
                    if i <= j:
                        tmp = b[i, i1, i2]
                        b[i, i1, i2] = b[j, i1, i2]
                        b[j, i1, i2] = tmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_3d_float64_axis1(np.ndarray[np.float64_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=float64 along axis=1."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.float64_t x, tmp
    cdef np.ndarray[np.float64_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    if n1 == 0:
        return b
    if (n < 1) or (n > n1):
        raise ValueError(PARTSORT_ERR_MSG % (n, n1))
    for i0 in range(n0):
        for i2 in range(n2):
            l = 0
            r = n1 - 1
            while l < r:
                x = b[i0, k, i2]
                i = l
                j = r
                while 1:
                    while b[i0, i, i2] < x: i += 1
                    while x < b[i0, j, i2]: j -= 1
                    if i <= j:
                        tmp = b[i0, i, i2]
                        b[i0, i, i2] = b[i0, j, i2]
                        b[i0, j, i2] = tmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return b

@cython.boundscheck(False)
@cython.wraparound(False)
def partsort_3d_float64_axis2(np.ndarray[np.float64_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=float64 along axis=2."
    cdef np.npy_intp i, j = 0, l, r, k = n-1 
    cdef np.float64_t x, tmp
    cdef np.ndarray[np.float64_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    if n2 == 0:
        return b
    if (n < 1) or (n > n2):
        raise ValueError(PARTSORT_ERR_MSG % (n, n2))
    for i0 in range(n0):
        for i1 in range(n1):
            l = 0
            r = n2 - 1
            while l < r:
                x = b[i0, i1, k]
                i = l
                j = r
                while 1:
                    while b[i0, i1, i] < x: i += 1
                    while x < b[i0, i1, j]: j -= 1
                    if i <= j:
                        tmp = b[i0, i1, i]
                        b[i0, i1, i] = b[i0, i1, j]
                        b[i0, i1, j] = tmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return b

cdef dict partsort_dict = {}
partsort_dict[(1, NPY_int32, 0)] = partsort_1d_int32_axis0
partsort_dict[(1, NPY_int64, 0)] = partsort_1d_int64_axis0
partsort_dict[(2, NPY_int32, 0)] = partsort_2d_int32_axis0
partsort_dict[(2, NPY_int32, 1)] = partsort_2d_int32_axis1
partsort_dict[(2, NPY_int64, 0)] = partsort_2d_int64_axis0
partsort_dict[(2, NPY_int64, 1)] = partsort_2d_int64_axis1
partsort_dict[(3, NPY_int32, 0)] = partsort_3d_int32_axis0
partsort_dict[(3, NPY_int32, 1)] = partsort_3d_int32_axis1
partsort_dict[(3, NPY_int32, 2)] = partsort_3d_int32_axis2
partsort_dict[(3, NPY_int64, 0)] = partsort_3d_int64_axis0
partsort_dict[(3, NPY_int64, 1)] = partsort_3d_int64_axis1
partsort_dict[(3, NPY_int64, 2)] = partsort_3d_int64_axis2
partsort_dict[(1, NPY_float32, 0)] = partsort_1d_float32_axis0
partsort_dict[(1, NPY_float64, 0)] = partsort_1d_float64_axis0
partsort_dict[(2, NPY_float32, 0)] = partsort_2d_float32_axis0
partsort_dict[(2, NPY_float32, 1)] = partsort_2d_float32_axis1
partsort_dict[(2, NPY_float64, 0)] = partsort_2d_float64_axis0
partsort_dict[(2, NPY_float64, 1)] = partsort_2d_float64_axis1
partsort_dict[(3, NPY_float32, 0)] = partsort_3d_float32_axis0
partsort_dict[(3, NPY_float32, 1)] = partsort_3d_float32_axis1
partsort_dict[(3, NPY_float32, 2)] = partsort_3d_float32_axis2
partsort_dict[(3, NPY_float64, 0)] = partsort_3d_float64_axis0
partsort_dict[(3, NPY_float64, 1)] = partsort_3d_float64_axis1
partsort_dict[(3, NPY_float64, 2)] = partsort_3d_float64_axis2

def partsort_slow_axis0(arr, n):
    "Unaccelerated (slow) partsort along axis 0."
    return bn.slow.partsort(arr, n, axis=0)

def partsort_slow_axis1(arr, n):
    "Unaccelerated (slow) partsort along axis 1."
    return bn.slow.partsort(arr, n, axis=1)

def partsort_slow_axis2(arr, n):
    "Unaccelerated (slow) partsort along axis 2."
    return bn.slow.partsort(arr, n, axis=2)

def partsort_slow_axis3(arr, n):
    "Unaccelerated (slow) partsort along axis 3."
    return bn.slow.partsort(arr, n, axis=3)

def partsort_slow_axis4(arr, n):
    "Unaccelerated (slow) partsort along axis 4."
    return bn.slow.partsort(arr, n, axis=4)

def partsort_slow_axis5(arr, n):
    "Unaccelerated (slow) partsort along axis 5."
    return bn.slow.partsort(arr, n, axis=5)

def partsort_slow_axis6(arr, n):
    "Unaccelerated (slow) partsort along axis 6."
    return bn.slow.partsort(arr, n, axis=6)

def partsort_slow_axis7(arr, n):
    "Unaccelerated (slow) partsort along axis 7."
    return bn.slow.partsort(arr, n, axis=7)

def partsort_slow_axis8(arr, n):
    "Unaccelerated (slow) partsort along axis 8."
    return bn.slow.partsort(arr, n, axis=8)

def partsort_slow_axis9(arr, n):
    "Unaccelerated (slow) partsort along axis 9."
    return bn.slow.partsort(arr, n, axis=9)

def partsort_slow_axis10(arr, n):
    "Unaccelerated (slow) partsort along axis 10."
    return bn.slow.partsort(arr, n, axis=10)

def partsort_slow_axis11(arr, n):
    "Unaccelerated (slow) partsort along axis 11."
    return bn.slow.partsort(arr, n, axis=11)

def partsort_slow_axis12(arr, n):
    "Unaccelerated (slow) partsort along axis 12."
    return bn.slow.partsort(arr, n, axis=12)

def partsort_slow_axis13(arr, n):
    "Unaccelerated (slow) partsort along axis 13."
    return bn.slow.partsort(arr, n, axis=13)

def partsort_slow_axis14(arr, n):
    "Unaccelerated (slow) partsort along axis 14."
    return bn.slow.partsort(arr, n, axis=14)

def partsort_slow_axis15(arr, n):
    "Unaccelerated (slow) partsort along axis 15."
    return bn.slow.partsort(arr, n, axis=15)

def partsort_slow_axis16(arr, n):
    "Unaccelerated (slow) partsort along axis 16."
    return bn.slow.partsort(arr, n, axis=16)

def partsort_slow_axis17(arr, n):
    "Unaccelerated (slow) partsort along axis 17."
    return bn.slow.partsort(arr, n, axis=17)

def partsort_slow_axis18(arr, n):
    "Unaccelerated (slow) partsort along axis 18."
    return bn.slow.partsort(arr, n, axis=18)

def partsort_slow_axis19(arr, n):
    "Unaccelerated (slow) partsort along axis 19."
    return bn.slow.partsort(arr, n, axis=19)

def partsort_slow_axis20(arr, n):
    "Unaccelerated (slow) partsort along axis 20."
    return bn.slow.partsort(arr, n, axis=20)

def partsort_slow_axis21(arr, n):
    "Unaccelerated (slow) partsort along axis 21."
    return bn.slow.partsort(arr, n, axis=21)

def partsort_slow_axis22(arr, n):
    "Unaccelerated (slow) partsort along axis 22."
    return bn.slow.partsort(arr, n, axis=22)

def partsort_slow_axis23(arr, n):
    "Unaccelerated (slow) partsort along axis 23."
    return bn.slow.partsort(arr, n, axis=23)

def partsort_slow_axis24(arr, n):
    "Unaccelerated (slow) partsort along axis 24."
    return bn.slow.partsort(arr, n, axis=24)

def partsort_slow_axis25(arr, n):
    "Unaccelerated (slow) partsort along axis 25."
    return bn.slow.partsort(arr, n, axis=25)

def partsort_slow_axis26(arr, n):
    "Unaccelerated (slow) partsort along axis 26."
    return bn.slow.partsort(arr, n, axis=26)

def partsort_slow_axis27(arr, n):
    "Unaccelerated (slow) partsort along axis 27."
    return bn.slow.partsort(arr, n, axis=27)

def partsort_slow_axis28(arr, n):
    "Unaccelerated (slow) partsort along axis 28."
    return bn.slow.partsort(arr, n, axis=28)

def partsort_slow_axis29(arr, n):
    "Unaccelerated (slow) partsort along axis 29."
    return bn.slow.partsort(arr, n, axis=29)

def partsort_slow_axis30(arr, n):
    "Unaccelerated (slow) partsort along axis 30."
    return bn.slow.partsort(arr, n, axis=30)

def partsort_slow_axis31(arr, n):
    "Unaccelerated (slow) partsort along axis 31."
    return bn.slow.partsort(arr, n, axis=31)

def partsort_slow_axis32(arr, n):
    "Unaccelerated (slow) partsort along axis 32."
    return bn.slow.partsort(arr, n, axis=32)

def partsort_slow_axisNone(arr, n):
    "Unaccelerated (slow) partsort along axis None."
    return bn.slow.partsort(arr, n, axis=None)


cdef dict partsort_slow_dict = {}
partsort_slow_dict[0] = partsort_slow_axis0
partsort_slow_dict[1] = partsort_slow_axis1
partsort_slow_dict[2] = partsort_slow_axis2
partsort_slow_dict[3] = partsort_slow_axis3
partsort_slow_dict[4] = partsort_slow_axis4
partsort_slow_dict[5] = partsort_slow_axis5
partsort_slow_dict[6] = partsort_slow_axis6
partsort_slow_dict[7] = partsort_slow_axis7
partsort_slow_dict[8] = partsort_slow_axis8
partsort_slow_dict[9] = partsort_slow_axis9
partsort_slow_dict[10] = partsort_slow_axis10
partsort_slow_dict[11] = partsort_slow_axis11
partsort_slow_dict[12] = partsort_slow_axis12
partsort_slow_dict[13] = partsort_slow_axis13
partsort_slow_dict[14] = partsort_slow_axis14
partsort_slow_dict[15] = partsort_slow_axis15
partsort_slow_dict[16] = partsort_slow_axis16
partsort_slow_dict[17] = partsort_slow_axis17
partsort_slow_dict[18] = partsort_slow_axis18
partsort_slow_dict[19] = partsort_slow_axis19
partsort_slow_dict[20] = partsort_slow_axis20
partsort_slow_dict[21] = partsort_slow_axis21
partsort_slow_dict[22] = partsort_slow_axis22
partsort_slow_dict[23] = partsort_slow_axis23
partsort_slow_dict[24] = partsort_slow_axis24
partsort_slow_dict[25] = partsort_slow_axis25
partsort_slow_dict[26] = partsort_slow_axis26
partsort_slow_dict[27] = partsort_slow_axis27
partsort_slow_dict[28] = partsort_slow_axis28
partsort_slow_dict[29] = partsort_slow_axis29
partsort_slow_dict[30] = partsort_slow_axis30
partsort_slow_dict[31] = partsort_slow_axis31
partsort_slow_dict[32] = partsort_slow_axis32
partsort_slow_dict[None] = partsort_slow_axisNone