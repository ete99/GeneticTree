from tree.tree cimport Tree
import numpy as np
cimport numpy as np

ctypedef np.npy_float64 DOUBLE_t         # Type of y
ctypedef np.npy_intp SIZE_t              # Type for indices and counters

cdef class Forest:
    # Class containing all trees
    cdef Tree[:] trees
    cdef int best_tree_number

    cdef int n_trees
    cdef int current_trees
    cdef int max_trees

    # temporal data to use once in fit function
    cdef object X
    cdef np.ndarray y

    cpdef set_X_y(self, object X, np.ndarray y)
    cpdef remove_X_y(self)

    cpdef initialize_population(self, int depth)

    cpdef function_to_test_nogil(self)
