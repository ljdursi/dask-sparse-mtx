"""Routines for simple COO matrices expressed as dicts
   {(row, col): value } for test problems

.. moduleauthor:: Jonathan Dursi <jonathan@dursi.ca>

"""
import random
import sparse


def mtx_permutation(size):
    """Returns a matrix in COO format as a dictionary
    describing a permutation matrix.

    :param size: size of (necessarily square) permutation matrix
    :rtype: dictionary of (row, col): val matrix entries
    """
    permutation = range(size)
    random.shuffle(permutation)
    return {(i, permutation[i]): 1.0 for i in range(size)}


def mtx_transpose(dictmtx):
    """Returns transposes of a matrix in COO format (expressed as a dict).

    :param dictmtx: dictionary containing COO matrix
    :rtype: dictionary of (row, col): val matrix entries
    """
    return {(j, i): dictmtx[(i, j)] for i, j in dictmtx.keys()}


def mtx_is_identity(mtx):
    """Returns True if matrix (dict or sparse.COO) is the identity matrix
    False otherwise

    :param mtx: sparse.COO or dict matrix
    :rtype: Bool: True if identity
    """
    if type(mtx) is dict:
        rows, cols = zip(*mtx.keys())
        n, m = max(rows), max(cols)
        vals = mtx.values()
    elif isinstance(mtx, sparse.COO):
        n, m = mtx.shape
        rows, cols = mtx.coords[0], mtx.coords[1]
        vals = mtx.data
    else:
        return False

    if n != m:
        return False
    remaining = set(range(n))
    for i, j, v in zip(rows, cols, vals):
        if i != j:
            return False
        if v != 1:
            return False
        remaining.remove(i)
    return len(remaining) == 0
