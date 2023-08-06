# 32 bit version
"argpartsort auto-generated from template"
# Select smallest k elements code used for inner loop of argpartsort method:
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

def argpartsort(arr, n, axis=-1):
    """
    Return indices that would partially sort an array.

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
        The indices of the `n` smallest elements will appear in the first `n`
        elements of the output array along the given `axis`.
    axis : {int, None}, optional
        Axis along which the partial sort is performed. The default (axis=-1)
        is to sort along the last axis.

    Returns
    -------
    y : ndarray
        An array the same shape as the input array containing the indices
        that partially sort `arr` such that the `n` smallest elements will
        appear (unordered) in the first `n` elements.

    See Also
    --------
    bottleneck.partsort: Partial sorting of array elements along given axis.
    
    Notes
    -----
    Unexpected results may occur if the input array contains NaN.

    Examples
    --------
    Create a numpy array:

    >>> a = np.array([1, 0, 3, 4, 2])
    
    Find the indices that partially sort that array so that the first 3
    elements are the smallest 3 elements:

    >>> index = bn.argpartsort(a, n=3)
    >>> index
    array([0, 1, 4, 3, 2])

    Let's use the indices to partially sort the array (note, as in this
    example, that the smallest 3 elements may not be in order):

    >>> a[index]
    array([1, 0, 2, 4, 3])
    
    """
    func, arr = argpartsort_selector(arr, axis)
    return func(arr, n)

def argpartsort_selector(arr, axis):
    """
    Return argpartsort function and array that matches `arr` and `axis`.
    
    Under the hood Bottleneck uses a separate Cython function for each
    combination of ndim, dtype, and axis. A lot of the overhead in
    bn.argpartsort() is in checking that `axis` is within range, converting
    `arr` into an array (if it is not already an array), and selecting the
    function to use to partially sort.

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
        The argpartsort function that matches the number of dimensions and
        dtype of the input array and the axis along which you wish to partially
        sort.
    a : ndarray
        If the input array `arr` is not a ndarray, then `a` will contain the
        result of converting `arr` into a ndarray.

    Examples
    --------
    Create a numpy array:

    >>> arr = np.array([1, 0, 3, 4, 2])
    
    Obtain the function needed to find the indices of a partial sort of `arr`
    along axis=0:

    >>> func, a = bn.func.argpartsort_selector(arr, axis=0)
    >>> func
    <function argpartsort_1d_int64_axis0>
    
    Use the returned function and array to find the indices of the partial
    sort:

    >>> func(a, n=3)
    array([0, 1, 4, 3, 2])

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
        func = argpartsort_dict[key]
    except KeyError:
        if (axis < 0) or (axis >= ndim):
            raise ValueError("axis(=%d) out of bounds" % axis)
        try:
            func = argpartsort_slow_dict[axis]
        except KeyError:
            tup = (str(ndim), str(a.dtype), str(axis))
            raise TypeError("Unsupported ndim/dtype/axis (%s/%s/%s)." % tup)
    return func, a

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_1d_int32_axis0(np.ndarray[np.int32_t, ndim=1] a, int n):
    "Partial sort of 1d array with dtype=int32 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.int32_t x, tmp
    cdef np.ndarray[np.int32_t, ndim=1] b = PyArray_Copy(a)
    cdef Py_ssize_t i0
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef np.npy_intp *dims = [n0]
    cdef np.ndarray[np.intp_t, ndim=1] y = PyArray_EMPTY(1, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        y[i0] = i0
    if n0 == 0:
        return y
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
                    itmp = y[i]
                    y[i] = y[j]
                    y[j] = itmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_1d_int64_axis0(np.ndarray[np.int64_t, ndim=1] a, int n):
    "Partial sort of 1d array with dtype=int64 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.int64_t x, tmp
    cdef np.ndarray[np.int64_t, ndim=1] b = PyArray_Copy(a)
    cdef Py_ssize_t i0
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef np.npy_intp *dims = [n0]
    cdef np.ndarray[np.intp_t, ndim=1] y = PyArray_EMPTY(1, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        y[i0] = i0
    if n0 == 0:
        return y
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
                    itmp = y[i]
                    y[i] = y[j]
                    y[j] = itmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_2d_int32_axis0(np.ndarray[np.int32_t, ndim=2] a, int n):
    "Partial sort of 2d array with dtype=int32 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.int32_t x, tmp
    cdef np.ndarray[np.int32_t, ndim=2] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef np.npy_intp *dims = [n0, n1]
    cdef np.ndarray[np.intp_t, ndim=2] y = PyArray_EMPTY(2, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            y[i0, i1] = i0
    if n0 == 0:
        return y
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
                    itmp = y[i, i1]
                    y[i, i1] = y[j, i1]
                    y[j, i1] = itmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_2d_int32_axis1(np.ndarray[np.int32_t, ndim=2] a, int n):
    "Partial sort of 2d array with dtype=int32 along axis=1."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.int32_t x, tmp
    cdef np.ndarray[np.int32_t, ndim=2] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef np.npy_intp *dims = [n0, n1]
    cdef np.ndarray[np.intp_t, ndim=2] y = PyArray_EMPTY(2, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            y[i0, i1] = i1
    if n1 == 0:
        return y
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
                    itmp = y[i0, i]
                    y[i0, i] = y[i0, j]
                    y[i0, j] = itmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_2d_int64_axis0(np.ndarray[np.int64_t, ndim=2] a, int n):
    "Partial sort of 2d array with dtype=int64 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.int64_t x, tmp
    cdef np.ndarray[np.int64_t, ndim=2] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef np.npy_intp *dims = [n0, n1]
    cdef np.ndarray[np.intp_t, ndim=2] y = PyArray_EMPTY(2, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            y[i0, i1] = i0
    if n0 == 0:
        return y
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
                    itmp = y[i, i1]
                    y[i, i1] = y[j, i1]
                    y[j, i1] = itmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_2d_int64_axis1(np.ndarray[np.int64_t, ndim=2] a, int n):
    "Partial sort of 2d array with dtype=int64 along axis=1."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.int64_t x, tmp
    cdef np.ndarray[np.int64_t, ndim=2] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef np.npy_intp *dims = [n0, n1]
    cdef np.ndarray[np.intp_t, ndim=2] y = PyArray_EMPTY(2, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            y[i0, i1] = i1
    if n1 == 0:
        return y
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
                    itmp = y[i0, i]
                    y[i0, i] = y[i0, j]
                    y[i0, j] = itmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_3d_int32_axis0(np.ndarray[np.int32_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=int32 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.int32_t x, tmp
    cdef np.ndarray[np.int32_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.intp_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            for i2 in range(n2):
                y[i0, i1, i2] = i0
    if n0 == 0:
        return y
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
                        itmp = y[i, i1, i2]
                        y[i, i1, i2] = y[j, i1, i2]
                        y[j, i1, i2] = itmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_3d_int32_axis1(np.ndarray[np.int32_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=int32 along axis=1."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.int32_t x, tmp
    cdef np.ndarray[np.int32_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.intp_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            for i2 in range(n2):
                y[i0, i1, i2] = i1
    if n1 == 0:
        return y
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
                        itmp = y[i0, i, i2]
                        y[i0, i, i2] = y[i0, j, i2]
                        y[i0, j, i2] = itmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_3d_int32_axis2(np.ndarray[np.int32_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=int32 along axis=2."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.int32_t x, tmp
    cdef np.ndarray[np.int32_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.intp_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            for i2 in range(n2):
                y[i0, i1, i2] = i2
    if n2 == 0:
        return y
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
                        itmp = y[i0, i1, i]
                        y[i0, i1, i] = y[i0, i1, j]
                        y[i0, i1, j] = itmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_3d_int64_axis0(np.ndarray[np.int64_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=int64 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.int64_t x, tmp
    cdef np.ndarray[np.int64_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.intp_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            for i2 in range(n2):
                y[i0, i1, i2] = i0
    if n0 == 0:
        return y
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
                        itmp = y[i, i1, i2]
                        y[i, i1, i2] = y[j, i1, i2]
                        y[j, i1, i2] = itmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_3d_int64_axis1(np.ndarray[np.int64_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=int64 along axis=1."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.int64_t x, tmp
    cdef np.ndarray[np.int64_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.intp_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            for i2 in range(n2):
                y[i0, i1, i2] = i1
    if n1 == 0:
        return y
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
                        itmp = y[i0, i, i2]
                        y[i0, i, i2] = y[i0, j, i2]
                        y[i0, j, i2] = itmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_3d_int64_axis2(np.ndarray[np.int64_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=int64 along axis=2."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.int64_t x, tmp
    cdef np.ndarray[np.int64_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.intp_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            for i2 in range(n2):
                y[i0, i1, i2] = i2
    if n2 == 0:
        return y
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
                        itmp = y[i0, i1, i]
                        y[i0, i1, i] = y[i0, i1, j]
                        y[i0, i1, j] = itmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_1d_float32_axis0(np.ndarray[np.float32_t, ndim=1] a, int n):
    "Partial sort of 1d array with dtype=float32 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.float32_t x, tmp
    cdef np.ndarray[np.float32_t, ndim=1] b = PyArray_Copy(a)
    cdef Py_ssize_t i0
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef np.npy_intp *dims = [n0]
    cdef np.ndarray[np.intp_t, ndim=1] y = PyArray_EMPTY(1, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        y[i0] = i0
    if n0 == 0:
        return y
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
                    itmp = y[i]
                    y[i] = y[j]
                    y[j] = itmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_1d_float64_axis0(np.ndarray[np.float64_t, ndim=1] a, int n):
    "Partial sort of 1d array with dtype=float64 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.float64_t x, tmp
    cdef np.ndarray[np.float64_t, ndim=1] b = PyArray_Copy(a)
    cdef Py_ssize_t i0
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef np.npy_intp *dims = [n0]
    cdef np.ndarray[np.intp_t, ndim=1] y = PyArray_EMPTY(1, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        y[i0] = i0
    if n0 == 0:
        return y
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
                    itmp = y[i]
                    y[i] = y[j]
                    y[j] = itmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_2d_float32_axis0(np.ndarray[np.float32_t, ndim=2] a, int n):
    "Partial sort of 2d array with dtype=float32 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.float32_t x, tmp
    cdef np.ndarray[np.float32_t, ndim=2] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef np.npy_intp *dims = [n0, n1]
    cdef np.ndarray[np.intp_t, ndim=2] y = PyArray_EMPTY(2, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            y[i0, i1] = i0
    if n0 == 0:
        return y
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
                    itmp = y[i, i1]
                    y[i, i1] = y[j, i1]
                    y[j, i1] = itmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_2d_float32_axis1(np.ndarray[np.float32_t, ndim=2] a, int n):
    "Partial sort of 2d array with dtype=float32 along axis=1."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.float32_t x, tmp
    cdef np.ndarray[np.float32_t, ndim=2] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef np.npy_intp *dims = [n0, n1]
    cdef np.ndarray[np.intp_t, ndim=2] y = PyArray_EMPTY(2, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            y[i0, i1] = i1
    if n1 == 0:
        return y
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
                    itmp = y[i0, i]
                    y[i0, i] = y[i0, j]
                    y[i0, j] = itmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_2d_float64_axis0(np.ndarray[np.float64_t, ndim=2] a, int n):
    "Partial sort of 2d array with dtype=float64 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.float64_t x, tmp
    cdef np.ndarray[np.float64_t, ndim=2] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef np.npy_intp *dims = [n0, n1]
    cdef np.ndarray[np.intp_t, ndim=2] y = PyArray_EMPTY(2, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            y[i0, i1] = i0
    if n0 == 0:
        return y
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
                    itmp = y[i, i1]
                    y[i, i1] = y[j, i1]
                    y[j, i1] = itmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_2d_float64_axis1(np.ndarray[np.float64_t, ndim=2] a, int n):
    "Partial sort of 2d array with dtype=float64 along axis=1."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.float64_t x, tmp
    cdef np.ndarray[np.float64_t, ndim=2] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef np.npy_intp *dims = [n0, n1]
    cdef np.ndarray[np.intp_t, ndim=2] y = PyArray_EMPTY(2, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            y[i0, i1] = i1
    if n1 == 0:
        return y
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
                    itmp = y[i0, i]
                    y[i0, i] = y[i0, j]
                    y[i0, j] = itmp
                    i += 1
                    j -= 1
                if i > j: break
            if j < k: l = i
            if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_3d_float32_axis0(np.ndarray[np.float32_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=float32 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.float32_t x, tmp
    cdef np.ndarray[np.float32_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.intp_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            for i2 in range(n2):
                y[i0, i1, i2] = i0
    if n0 == 0:
        return y
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
                        itmp = y[i, i1, i2]
                        y[i, i1, i2] = y[j, i1, i2]
                        y[j, i1, i2] = itmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_3d_float32_axis1(np.ndarray[np.float32_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=float32 along axis=1."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.float32_t x, tmp
    cdef np.ndarray[np.float32_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.intp_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            for i2 in range(n2):
                y[i0, i1, i2] = i1
    if n1 == 0:
        return y
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
                        itmp = y[i0, i, i2]
                        y[i0, i, i2] = y[i0, j, i2]
                        y[i0, j, i2] = itmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_3d_float32_axis2(np.ndarray[np.float32_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=float32 along axis=2."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.float32_t x, tmp
    cdef np.ndarray[np.float32_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.intp_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            for i2 in range(n2):
                y[i0, i1, i2] = i2
    if n2 == 0:
        return y
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
                        itmp = y[i0, i1, i]
                        y[i0, i1, i] = y[i0, i1, j]
                        y[i0, i1, j] = itmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_3d_float64_axis0(np.ndarray[np.float64_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=float64 along axis=0."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.float64_t x, tmp
    cdef np.ndarray[np.float64_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.intp_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            for i2 in range(n2):
                y[i0, i1, i2] = i0
    if n0 == 0:
        return y
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
                        itmp = y[i, i1, i2]
                        y[i, i1, i2] = y[j, i1, i2]
                        y[j, i1, i2] = itmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_3d_float64_axis1(np.ndarray[np.float64_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=float64 along axis=1."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.float64_t x, tmp
    cdef np.ndarray[np.float64_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.intp_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            for i2 in range(n2):
                y[i0, i1, i2] = i1
    if n1 == 0:
        return y
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
                        itmp = y[i0, i, i2]
                        y[i0, i, i2] = y[i0, j, i2]
                        y[i0, j, i2] = itmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def argpartsort_3d_float64_axis2(np.ndarray[np.float64_t, ndim=3] a, int n):
    "Partial sort of 3d array with dtype=float64 along axis=2."
    cdef np.npy_intp i, j = 0, l, r, k = n-1, itmp 
    cdef np.float64_t x, tmp
    cdef np.ndarray[np.float64_t, ndim=3] b = PyArray_Copy(a)
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.intp_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_intp, 0)
    for i0 in range(n0):
        for i1 in range(n1):
            for i2 in range(n2):
                y[i0, i1, i2] = i2
    if n2 == 0:
        return y
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
                        itmp = y[i0, i1, i]
                        y[i0, i1, i] = y[i0, i1, j]
                        y[i0, i1, j] = itmp
                        i += 1
                        j -= 1
                    if i > j: break
                if j < k: l = i
                if k < i: r = j
    return y

cdef dict argpartsort_dict = {}
argpartsort_dict[(1, NPY_int32, 0)] = argpartsort_1d_int32_axis0
argpartsort_dict[(1, NPY_int64, 0)] = argpartsort_1d_int64_axis0
argpartsort_dict[(2, NPY_int32, 0)] = argpartsort_2d_int32_axis0
argpartsort_dict[(2, NPY_int32, 1)] = argpartsort_2d_int32_axis1
argpartsort_dict[(2, NPY_int64, 0)] = argpartsort_2d_int64_axis0
argpartsort_dict[(2, NPY_int64, 1)] = argpartsort_2d_int64_axis1
argpartsort_dict[(3, NPY_int32, 0)] = argpartsort_3d_int32_axis0
argpartsort_dict[(3, NPY_int32, 1)] = argpartsort_3d_int32_axis1
argpartsort_dict[(3, NPY_int32, 2)] = argpartsort_3d_int32_axis2
argpartsort_dict[(3, NPY_int64, 0)] = argpartsort_3d_int64_axis0
argpartsort_dict[(3, NPY_int64, 1)] = argpartsort_3d_int64_axis1
argpartsort_dict[(3, NPY_int64, 2)] = argpartsort_3d_int64_axis2
argpartsort_dict[(1, NPY_float32, 0)] = argpartsort_1d_float32_axis0
argpartsort_dict[(1, NPY_float64, 0)] = argpartsort_1d_float64_axis0
argpartsort_dict[(2, NPY_float32, 0)] = argpartsort_2d_float32_axis0
argpartsort_dict[(2, NPY_float32, 1)] = argpartsort_2d_float32_axis1
argpartsort_dict[(2, NPY_float64, 0)] = argpartsort_2d_float64_axis0
argpartsort_dict[(2, NPY_float64, 1)] = argpartsort_2d_float64_axis1
argpartsort_dict[(3, NPY_float32, 0)] = argpartsort_3d_float32_axis0
argpartsort_dict[(3, NPY_float32, 1)] = argpartsort_3d_float32_axis1
argpartsort_dict[(3, NPY_float32, 2)] = argpartsort_3d_float32_axis2
argpartsort_dict[(3, NPY_float64, 0)] = argpartsort_3d_float64_axis0
argpartsort_dict[(3, NPY_float64, 1)] = argpartsort_3d_float64_axis1
argpartsort_dict[(3, NPY_float64, 2)] = argpartsort_3d_float64_axis2

def argpartsort_slow_axis0(arr, n):
    "Unaccelerated (slow) argpartsort along axis 0."
    return bn.slow.argpartsort(arr, n, axis=0)

def argpartsort_slow_axis1(arr, n):
    "Unaccelerated (slow) argpartsort along axis 1."
    return bn.slow.argpartsort(arr, n, axis=1)

def argpartsort_slow_axis2(arr, n):
    "Unaccelerated (slow) argpartsort along axis 2."
    return bn.slow.argpartsort(arr, n, axis=2)

def argpartsort_slow_axis3(arr, n):
    "Unaccelerated (slow) argpartsort along axis 3."
    return bn.slow.argpartsort(arr, n, axis=3)

def argpartsort_slow_axis4(arr, n):
    "Unaccelerated (slow) argpartsort along axis 4."
    return bn.slow.argpartsort(arr, n, axis=4)

def argpartsort_slow_axis5(arr, n):
    "Unaccelerated (slow) argpartsort along axis 5."
    return bn.slow.argpartsort(arr, n, axis=5)

def argpartsort_slow_axis6(arr, n):
    "Unaccelerated (slow) argpartsort along axis 6."
    return bn.slow.argpartsort(arr, n, axis=6)

def argpartsort_slow_axis7(arr, n):
    "Unaccelerated (slow) argpartsort along axis 7."
    return bn.slow.argpartsort(arr, n, axis=7)

def argpartsort_slow_axis8(arr, n):
    "Unaccelerated (slow) argpartsort along axis 8."
    return bn.slow.argpartsort(arr, n, axis=8)

def argpartsort_slow_axis9(arr, n):
    "Unaccelerated (slow) argpartsort along axis 9."
    return bn.slow.argpartsort(arr, n, axis=9)

def argpartsort_slow_axis10(arr, n):
    "Unaccelerated (slow) argpartsort along axis 10."
    return bn.slow.argpartsort(arr, n, axis=10)

def argpartsort_slow_axis11(arr, n):
    "Unaccelerated (slow) argpartsort along axis 11."
    return bn.slow.argpartsort(arr, n, axis=11)

def argpartsort_slow_axis12(arr, n):
    "Unaccelerated (slow) argpartsort along axis 12."
    return bn.slow.argpartsort(arr, n, axis=12)

def argpartsort_slow_axis13(arr, n):
    "Unaccelerated (slow) argpartsort along axis 13."
    return bn.slow.argpartsort(arr, n, axis=13)

def argpartsort_slow_axis14(arr, n):
    "Unaccelerated (slow) argpartsort along axis 14."
    return bn.slow.argpartsort(arr, n, axis=14)

def argpartsort_slow_axis15(arr, n):
    "Unaccelerated (slow) argpartsort along axis 15."
    return bn.slow.argpartsort(arr, n, axis=15)

def argpartsort_slow_axis16(arr, n):
    "Unaccelerated (slow) argpartsort along axis 16."
    return bn.slow.argpartsort(arr, n, axis=16)

def argpartsort_slow_axis17(arr, n):
    "Unaccelerated (slow) argpartsort along axis 17."
    return bn.slow.argpartsort(arr, n, axis=17)

def argpartsort_slow_axis18(arr, n):
    "Unaccelerated (slow) argpartsort along axis 18."
    return bn.slow.argpartsort(arr, n, axis=18)

def argpartsort_slow_axis19(arr, n):
    "Unaccelerated (slow) argpartsort along axis 19."
    return bn.slow.argpartsort(arr, n, axis=19)

def argpartsort_slow_axis20(arr, n):
    "Unaccelerated (slow) argpartsort along axis 20."
    return bn.slow.argpartsort(arr, n, axis=20)

def argpartsort_slow_axis21(arr, n):
    "Unaccelerated (slow) argpartsort along axis 21."
    return bn.slow.argpartsort(arr, n, axis=21)

def argpartsort_slow_axis22(arr, n):
    "Unaccelerated (slow) argpartsort along axis 22."
    return bn.slow.argpartsort(arr, n, axis=22)

def argpartsort_slow_axis23(arr, n):
    "Unaccelerated (slow) argpartsort along axis 23."
    return bn.slow.argpartsort(arr, n, axis=23)

def argpartsort_slow_axis24(arr, n):
    "Unaccelerated (slow) argpartsort along axis 24."
    return bn.slow.argpartsort(arr, n, axis=24)

def argpartsort_slow_axis25(arr, n):
    "Unaccelerated (slow) argpartsort along axis 25."
    return bn.slow.argpartsort(arr, n, axis=25)

def argpartsort_slow_axis26(arr, n):
    "Unaccelerated (slow) argpartsort along axis 26."
    return bn.slow.argpartsort(arr, n, axis=26)

def argpartsort_slow_axis27(arr, n):
    "Unaccelerated (slow) argpartsort along axis 27."
    return bn.slow.argpartsort(arr, n, axis=27)

def argpartsort_slow_axis28(arr, n):
    "Unaccelerated (slow) argpartsort along axis 28."
    return bn.slow.argpartsort(arr, n, axis=28)

def argpartsort_slow_axis29(arr, n):
    "Unaccelerated (slow) argpartsort along axis 29."
    return bn.slow.argpartsort(arr, n, axis=29)

def argpartsort_slow_axis30(arr, n):
    "Unaccelerated (slow) argpartsort along axis 30."
    return bn.slow.argpartsort(arr, n, axis=30)

def argpartsort_slow_axis31(arr, n):
    "Unaccelerated (slow) argpartsort along axis 31."
    return bn.slow.argpartsort(arr, n, axis=31)

def argpartsort_slow_axis32(arr, n):
    "Unaccelerated (slow) argpartsort along axis 32."
    return bn.slow.argpartsort(arr, n, axis=32)

def argpartsort_slow_axisNone(arr, n):
    "Unaccelerated (slow) argpartsort along axis None."
    return bn.slow.argpartsort(arr, n, axis=None)


cdef dict argpartsort_slow_dict = {}
argpartsort_slow_dict[0] = argpartsort_slow_axis0
argpartsort_slow_dict[1] = argpartsort_slow_axis1
argpartsort_slow_dict[2] = argpartsort_slow_axis2
argpartsort_slow_dict[3] = argpartsort_slow_axis3
argpartsort_slow_dict[4] = argpartsort_slow_axis4
argpartsort_slow_dict[5] = argpartsort_slow_axis5
argpartsort_slow_dict[6] = argpartsort_slow_axis6
argpartsort_slow_dict[7] = argpartsort_slow_axis7
argpartsort_slow_dict[8] = argpartsort_slow_axis8
argpartsort_slow_dict[9] = argpartsort_slow_axis9
argpartsort_slow_dict[10] = argpartsort_slow_axis10
argpartsort_slow_dict[11] = argpartsort_slow_axis11
argpartsort_slow_dict[12] = argpartsort_slow_axis12
argpartsort_slow_dict[13] = argpartsort_slow_axis13
argpartsort_slow_dict[14] = argpartsort_slow_axis14
argpartsort_slow_dict[15] = argpartsort_slow_axis15
argpartsort_slow_dict[16] = argpartsort_slow_axis16
argpartsort_slow_dict[17] = argpartsort_slow_axis17
argpartsort_slow_dict[18] = argpartsort_slow_axis18
argpartsort_slow_dict[19] = argpartsort_slow_axis19
argpartsort_slow_dict[20] = argpartsort_slow_axis20
argpartsort_slow_dict[21] = argpartsort_slow_axis21
argpartsort_slow_dict[22] = argpartsort_slow_axis22
argpartsort_slow_dict[23] = argpartsort_slow_axis23
argpartsort_slow_dict[24] = argpartsort_slow_axis24
argpartsort_slow_dict[25] = argpartsort_slow_axis25
argpartsort_slow_dict[26] = argpartsort_slow_axis26
argpartsort_slow_dict[27] = argpartsort_slow_axis27
argpartsort_slow_dict[28] = argpartsort_slow_axis28
argpartsort_slow_dict[29] = argpartsort_slow_axis29
argpartsort_slow_dict[30] = argpartsort_slow_axis30
argpartsort_slow_dict[31] = argpartsort_slow_axis31
argpartsort_slow_dict[32] = argpartsort_slow_axis32
argpartsort_slow_dict[None] = argpartsort_slow_axisNone