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
        tile = delayed(dsm.mtxdb_read_chunk)(dbname, mname, rows=r, cols=c)
        return da.from_delayed(tile, (tilesize, tilesize), float)

    def ntiles(size):
        return (size+tilesize-1)//tilesize

    # construct the arrays with da.concatenate
    def tiled_dask_array(mname, n, m):
        rows = []
        for ti in range(ntiles(n)):
            cols = [da_delayed_tile(mname, ti, tj) for tj in range(ntiles(m))]
            rows.append(da.concatenate(cols, axis=1))
        return da.concatenate(rows, axis=0)

    amat = tiled_dask_array(a, na, ma)
    bmat = tiled_dask_array(b, nb, mb)

    # perform the multiplication
    return da.dot(amat, bmat).compute()
