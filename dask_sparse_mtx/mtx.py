"""Routines for simple COO matrices expressed as dicts
   {(row, col): value } for test problems

.. moduleauthor:: Jonathan Dursi <jonathan@dursi.ca>

"""
import random


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
