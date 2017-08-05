dask_sparse_mtx
===============

.. automodule:: dask_sparse_mtx

Overview
--------

This is a simple demo showing how to use dask delayed and dask arrays
to multiply sparse matricies loaded in lazily into memory (here, from
an sqlite3 database).

Either approach uses ``dask.delayed`` to wrap reading tiles of the matrix
into tasks, and then either manually (using
:func:`dask_sparse_mtx.dask_delayed_mult`) or using the infrastructure
provided by ``dask.array`` (using :func:`dask_sparse_mtx.dask_array_mult`)
multiplies the two matrices in a tiled manner:

.. math:: 

    \left( \begin{array}{c|c|c|c} C_{1,1} & C_{1,2} & \dots & C_{1,M} \\ \hline C_{2,1} & C_{2,2} & \dots & C_{2,M} \\ \hline \dots & \dots & \dots & \dots \\ \hline C_{N,1} & C_{N,2} & \dots & C_{N,M} \\ \end{array} \right ) & = \left( \begin{array}{c|c|c|c} A_{1,1} & A_{1,2} & \dots & A_{1,K} \\ \hline A_{2,1} & A_{2,2} & \dots & A_{2,K} \\ \hline \dots & \dots & \dots & \dots \\ \hline A_{N,1} & A_{N,2} & \dots & A_{N,K} \\ \end{array} \right ) \left( \begin{array}{c|c|c|c} B_{1,1} & B_{1,2} & \dots & B_{1,M} \\ \hline B_{2,1} & B_{2,2} & \dots & B_{2,M} \\ \hline \dots & \dots & \dots & \dots \\ \hline B_{K,1} & B_{K,2} & \dots & B_{K,M} \\ \end{array} \right ) 

    C_{i,j} & = \sum_{k}^K A_{i,k} B_{k,j}

where the multiplication in the second line above is matrix multiplication.

The example can be run as follows (will take a few minutes):: 

    import os
    import dask.multiprocessing
    import dask_sparse_mtx as dsm

    dask.set_options(get=dask.multiprocessing.get)

    filename = "test.db"
    size = 200000

    # create file
    dsm.mtxdb_init(filename)

    # create matrices and write them; their product
    # will be the identity matrix
    a = dsm.mtx_permutation(size)
    b = dsm.mtx_transpose(a)
    dsm.mtxdb_add_matrix_from_dict(filename, 'A', a)
    dsm.mtxdb_add_matrix_from_dict(filename, 'B', b)

    # smaller tilesize - more parallelism, but more
    # overhead from task management
    tilesize = 20000
    c = dsm.dask_array_mult(filename, 'A', 'B', tilesize)

    print c[:10, :10]

    if dsm.mtx_is_identity(c):
        print "Success!"

    os.remove(filename)


Matrix Multiplication
---------------------

Matrix multiplication is performed by either :func:`dask_sparse_mtx.dask_delayed_mult`
or :func:`dask_sparse_mtx.dask_array_mult`:

.. automodule:: dask_sparse_mtx.dask_delayed_mult
    :members:
.. automodule:: dask_sparse_mtx.dask_array_mult
    :members:

Sparse Matrix DB
----------------

These rely on routines for reading/writing the sparse matrices (in COO format)
into the sqlite3 db:

.. automodule:: dask_sparse_mtx.mtxdb
    :members: mtxdb_init, mtxdb_add_matrix_from_dict, mtxdb_read_chunk, mtxdb_matrix_shape

Sparse Matrix Helper Methods
-----------------------------

And finally there are helper routines for creating simple permutation 
matricies useful for tests:

.. automodule:: dask_sparse_mtx.mtx
    :members: mtx_permutation, mtx_transpose, mtx_is_identity


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

