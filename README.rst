Sparse Matrix Multiplication with Dask
======================================

.. image:: https://travis-ci.org/ljdursi/dask-sparse-mtx.svg?branch=master
    :target: https://travis-ci.org/ljdursi/dask-sparse-mtx

Toy example of performing large `sparse <https://github.com/mrocklin/sparse/>`_ matrix multiplication
with dask, with the data in an sqlite3 db.

This package can be installed as follows::

    # install into a venv
    virtualenv dsm
    cd dsm/
    source bin/activate

    # clone and install
    git clone https://github.com/ljdursi/dask-sparse-mtx
    cd dask-sparse-mtx/
    pip install -r requirements.txt
    python setup.py install

    # run tests
    python -m unittest discover

A sample program follows:)::

    import os
    import dask.multiprocessing
    import dask_sparse_mtx as dsm

    dask.set_options(get=dask.multiprocessing.get)

    filename = "test.db"
    size = 20000

    # create file
    dsm.mtxdb_init(filename)

    # create matrices and write them; their product
    # will be the identity matrix
    a = dsm.mtx_permutation(size)
    b = dsm.mtx_transpose(a)
    dsm.mtxdb_add_matrix_from_dict(filename, 'A', a)
    dsm.mtxdb_add_matrix_from_dict(filename, 'B', b)

    # smaller tilesize == more parallelism, but more
    # overhead from task management
    tilesize = 2000
    c = dsm.dask_array_mult(filename, 'A', 'B', tilesize)

    print c[:10, :10]

    if dsm.mtx_is_identity(c):
        print "Success!"

    os.remove(filename)

Note one can use dask distributed, which offers a more sophisticated
scheduler as well as the possibility to run over multiple nodes, as
well: to run it on one host, one can ``pip install distributed`` and
then in place of the ``dask.set_options`` line above one can use::

    from dask.distributed import Client
    client = Client()
    dask.set_options(get=client.get)
