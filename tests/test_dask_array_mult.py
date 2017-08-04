"""Tests a tiled sparse matrix multiplication using dask.array,
   of two matrices contained in an sqlite3 db.

   Multiplies a permutation matrix and its inverse and ensures result is
   identity matrix.
"""

import unittest
import os
import dask
import dask.multiprocessing
from .context import dask_sparse_mtx as dsm


class SparseMultDaskArray(unittest.TestCase):
    _size = 2000
    _dbfile = "permutation_mtx.db"

    def setUp(self):
	"""
        Creates two permutation matrices, A and B, with
        B being A's inverse
        """
        # create file
        dsm.mtxdb_init(self._dbfile)

        # create matrices to write
        a = dsm.mtx_permutation(self._size)
        b = dsm.mtx_transpose(a)
        dsm.mtxdb_add_matrix_from_dict(self._dbfile, 'A', a)
        dsm.mtxdb_add_matrix_from_dict(self._dbfile, 'B', b)

        # use the multiprocessing scheduler
        dask.set_options(get=dask.multiprocessing.get)

    def tearDown(self):
        """
        Delete file containing sqlite3 db
        """
        os.remove(self._dbfile)

    def test_multiply_dask_array_100tiles(self):
        "Make sure full matrix multiplication gives identity matrix"
        tilesize = (self._size+10-1)//10
        c = dsm.dask_array_mult(self._dbfile, 'A', 'B', tilesize)
        for i, j, v in zip(c.coords[0], c.coords[1], c.data):
            print i, j, v
        assert dsm.mtx_is_identity(c)

    def test_multiply_dask_array_1tile(self):
        "Make sure full matrix multiplication gives identity matrix"
        tilesize = self._size
        c = dsm.dask_array_mult(self._dbfile, 'A', 'B', tilesize)
        assert dsm.mtx_is_identity(c)


if __name__ == '__main__':
    unittest.main()
