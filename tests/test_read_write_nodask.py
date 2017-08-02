"""Runs two non-dask tests based on multiplies chunks of two square sparse
   matrices contained in an sqlite3 db.

   First, multiplies the two and ensures result is the identity matrix.

   Second, multiplies subchunks of the two and makes sure the result has
   the correct shape.
"""

import unittest
import sparse
import os
from .context import dask_sparse_mtx as dsm


class ReadWriteTest(unittest.TestCase):
    _size = 100
    _dbfile = "small_permutation_mtx.db"

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

    def tearDown(self):
        """
        Delete file containing sqlite3 db
        """
        os.remove(self._dbfile)

    def test_multiply_full(self):
        "Make sure full matrix multiplication gives identity matrix"
        # ensure square
        a = dsm.mtxdb_read_chunk(self._dbfile, 'A')
        b = dsm.mtxdb_read_chunk(self._dbfile, 'B')
        c = sparse.tensordot(a, b, axes=1)
        n, m = c.shape
        assert n == m
        assert n == self._size

        # ensure all diagonal elements are present and have value 1
        remaining = set(range(n))
        for i, j, v in zip(c.coords[0], c.coords[1], c.data):
            assert v == 1.0
            assert i == j
            remaining.remove(i)
        assert len(remaining) == 0

    def test_multiply_chunks(self):
        """Extract chunks of matrix, ensure matrix multiplication results
           in correct shape."""
        a = dsm.mtxdb_read_chunk(self._dbfile, 'A',
                                 rows=(50, 100), cols=(0, 100))
        b = dsm.mtxdb_read_chunk(self._dbfile, 'B',
                                 rows=(0, 100), cols=(0, 50))
        c = sparse.tensordot(a, b, axes=1)
        assert c.shape == (50, 50)


if __name__ == '__main__':
    unittest.main()
