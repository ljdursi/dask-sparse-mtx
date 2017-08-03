"""Tests a tiled sparse matrix multiplication, with tasks scheduled via dask,
   of two matrices contained in an sqlite3 db.

   Multiplies a permutation matrix and its inverse and ensures result is
   identity matrix.
"""

import unittest
import os
import dask
import dask.multiprocessing
from .context import dask_sparse_mtx as dsm


class SparseMultDaskDelayed(unittest.TestCase):
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

    def test_multiply_dask_delayed_100tiles(self):
        "Make sure full matrix multiplication gives identity matrix"
        tilesize = 200
        ntiles = self._size//tilesize
        c = dsm.dask_delayed_mult(self._dbfile, 'A', 'B', tilesize)

        for i in range(ntiles):
            for j in range(ntiles):
                if i == j:
                    assert dsm.mtx_is_identity(c[(i, i)])
                else:
                    assert c[(i, j)].nnz == 0

    def test_multiply_dask_delayed_1tile(self):
        "Make sure full matrix multiplication gives identity matrix"
        tilesize = 2000
        ntiles = self._size//tilesize
        c = dsm.dask_delayed_mult(self._dbfile, 'A', 'B', tilesize)

        for i in range(ntiles):
            for j in range(ntiles):
                if i == j:
                    assert dsm.mtx_is_identity(c[(i, i)])
                else:
                    assert c[(i, j)].nnz == 0


if __name__ == '__main__':
    unittest.main()
