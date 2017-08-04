.. dask_sparse_mtx documentation master file, created by
   sphinx-quickstart on Mon Jul 31 22:36:07 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

dask_sparse_mtx
===============

Overview
--------

This is a simple demo showing how to use dask delayed and dask arrays
to multiply sparse matricies loaded in lazily into memory (here, from
an sqlite3 database).



.. math:: \left( \begin{array}{c|c|c|c} C_{1,1} & C_{1,2} & \dots & C_{1,M} \\ \hline C_{2,1} & C_{2,2} & \dots & C_{2,M} \\ \hline \dots & \dots & \dots & \dots \\ \hline C_{N,1} & C_{N,2} & \dots & C_{N,M} \\ \end{array} \right ) = \left( \begin{array}{c|c|c|c} A_{1,1} & A_{1,2} & \dots & A_{1,K} \\ \hline A_{2,1} & A_{2,2} & \dots & A_{2,K} \\ \hline \dots & \dots & \dots & \dots \\ \hline A_{N,1} & A_{N,2} & \dots & A_{N,K} \\ \end{array} \right ) \left( \begin{array}{c|c|c|c} B_{1,1} & B_{1,2} & \dots & B_{1,M} \\ \hline B_{2,1} & B_{2,2} & \dots & B_{2,M} \\ \hline \dots & \dots & \dots & \dots \\ \hline B_{K,1} & B_{K,2} & \dots & B_{K,M} \\ \end{array} \right ) 

.. math:: C_{i,j} = \sum_{k}^K A_{i,k} B_{k,j}


Contents:

.. toctree::
   :maxdepth: 2

.. currentmodule:: dask_sparse_mtx

Matrix Multiplication
---------------------
.. automethod::
	dask_delayed_mult
	dask_array_mult

Sparse Matrix DB
----------------
.. automethod::
	mtxdb_init
	mtxdb_add_matrix_from_dict
	mtxdb_read_chunk
	mtxdb_matrix_shape

Sparse Matrix Helper Methods
-----------------------------
.. automethod::
	mtx_permutation
	mtx_transpose
	mtx_is_identity


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

