"""Multiply two sparse matrices in the database
   using dask.delayed and task parallelism.

   Pros: high control over tiles size, distribution
   Cons: larger memory usage in intermediate steps as
         tiles can't be mutated

.. moduleauthor:: Jonathan Dursi <jonathan@dursi.ca>

"""
import dask_sparse_mtx as dsm
import dask
import dask.delayed as delayed
import sparse


def dask_delayed_mult(dbname, a, b, tilesize):
    """Multiplies two sparse matrices from the matrix db
    using dask.delayed and task parallelism

    TODO: better reduction over intermediate terms

    :param dbname: Filename of the sparse matrix db
    :param a: Name of matrix A in the db
    :param b: Name of matrix B in the db
    :param tilesize: int - size of the (square) tiles
             read in to do the multiplication
    :rtype: dictionary of sparse.COO matrix tiles
             - eg c[(i,j)] is the i, jth tile of product
    """
    _, na, _, ma = dsm.mtxdb_matrix_shape(dbname, a)
    _, nb, _, mb = dsm.mtxdb_matrix_shape(dbname, b)

    if ma != nb:
        raise ValueError('Matrices '+a+' and '+b+' have inconsistent shapes')

    def delayed_tile(mname, i, j):
        r = (i*tilesize, (i+1)*tilesize)
        c = (j*tilesize, (j+1)*tilesize)
        return delayed(dsm.mtxdb_read_chunk)(dbname, mname, rows=r, cols=c)

    def ntiles(size, tilesize):
        return (size+tilesize-1)//tilesize

    amat = {(i, j): delayed_tile(a, i, j) for i in range(ntiles(na, tilesize))
            for j in range(ntiles(ma, tilesize))}
    bmat = {(i, j): delayed_tile(b, i, j) for i in range(ntiles(nb, tilesize))
            for j in range(ntiles(mb, tilesize))}

    # Here we're computing all partial products,
    # and then performing a linear summation over the k index.
    #
    # This is almost certainly suboptimal and a pairwise tree reduction would
    # be better, for memory use as well as compute time

    partialprod = {(i, j, k): delayed(sparse.tensordot)(amat[(i, k)],
                                                        bmat[(k, j)], axes=1)
                   for i in range(ntiles(na, tilesize))
                   for k in range(ntiles(ma, tilesize))
                   for j in range(ntiles(mb, tilesize))}

    c = [delayed(reduce)((lambda a, b: a + b),
                         [partialprod[(i, j, k)]
                          for k in range(ntiles(ma, tilesize))])
         for i in range(ntiles(na, tilesize))
         for j in range(ntiles(mb, tilesize))]

    res = dask.compute(c)[0]

    c = {}
    item = 0
    for i in range(ntiles(na, tilesize)):
        for j in range(ntiles(mb, tilesize)):
            c[(i, j)] = res[item]
            item += 1

    return c
