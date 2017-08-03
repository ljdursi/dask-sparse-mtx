"""Multiply two sparse matrices in the database
   by constructing a dask array from the tiles

   Pros: Makes better use of the scheduler, esp for large numbers of tiles
         Don't have to think about de-tiling final result
   Cons: Less control of tiling in intermediate and final stages

.. moduleauthor:: Jonathan Dursi <jonathan@dursi.ca>

"""
import dask_sparse_mtx as dsm
import dask.array as da
import dask.delayed as delayed


def dask_array_mult(dbname, a, b, tilesize):
    """Multiplies two sparse matrices from the matrix db
    using dask.arrays

    :param dbname: Filename of the sparse matrix db
    :param a: Name of matrix A in the db
    :param b: Name of matrix B in the db
    :param tilesize: int - size of the (square) tiles
             read in to do the multiplication
    :rtype: sparse.COO - single sparse matrix final result
    """
    _, na, _, ma = dsm.mtxdb_matrix_shape(dbname, a)
    _, nb, _, mb = dsm.mtxdb_matrix_shape(dbname, b)

    if ma != nb:
        raise ValueError('Matrices '+a+' and '+b+' have inconsistent shapes')

    def da_delayed_tile(mname, i, j):
        r = (i*tilesize, (i+1)*tilesize)
        c = (j*tilesize, (j+1)*tilesize)
        return da.from_delayed(delayed(dsm.mtxdb_read_chunk)
                               (dbname, mname, rows=r, cols=c),
                               (tilesize, tilesize), float)

    def ntiles(size, tilesize):
        return (size+tilesize-1)//tilesize

    # construct the arrays with da.concatenate
    arows = []
    for i in range(ntiles(na, tilesize)):
        acols = [da_delayed_tile(a, i, j) for j in range(ntiles(ma, tilesize))]
        arows.append(da.concatenate(acols, axis=1))
    a = da.concatenate(arows, axis=0)

    brows = []
    for i in range(ntiles(nb, tilesize)):
        bcols = [da_delayed_tile(a, i, j) for j in range(ntiles(mb, tilesize))]
        brows.append(da.concatenate(bcols, axis=1))
    b = da.concatenate(arows, axis=0)

    # perform the multiplication with da.tensordot
    return da.tensordot(a, b, axes=1).compute()
