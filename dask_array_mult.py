import dask_sparse_mtx as dsm
import dask
import dask.array as da
import dask.multiprocessing
import dask.dot
import dask.delayed as delayed

dask.set_options(get=dask.multiprocessing.get)

size = 100
chunksize = 10
nchunks = (size+chunksize-1)//chunksize

dbfile = "1000x1000.db"

a = dsm.mtx_permutation(size)
b = dsm.mtx_transpose(a)

dsm.mtxdb_init(dbfile)
dsm.mtxdb_add_matrix_from_dict(dbfile, 'A', a)
dsm.mtxdb_add_matrix_from_dict(dbfile, 'B', b)

del a
del b


def get_matrix_chunk(fname, mname, size, chunksize, i, j):
    rows = (i*chunksize, (i+1)*chunksize)
    cols = (j*chunksize, (j+1)*chunksize)

    return dsm.mtxdb_read_chunk(fname, mname, rows=rows, cols=cols)


# build dask arrays from delayed chunks

arows = []
brows = []
for i in range(nchunks):
    achunks = []
    bchunks = []
    for j in range(nchunks):
        achunks.append(da.from_delayed(delayed(get_matrix_chunk)(dbfile, 'A', size, chunksize, i, j), (chunksize, chunksize), float))
        bchunks.append(da.from_delayed(delayed(get_matrix_chunk)(dbfile, 'B', size, chunksize, i, j), (chunksize, chunksize), float))
    arows.append(da.concatenate(achunks, axis=1))
    brows.append(da.concatenate(bchunks, axis=1))
a = da.concatenate(arows, axis=0)
b = da.concatenate(brows, axis=0)

print("arows[0] = ", arows[0])
print("a = ", a)

print("a.sum() = ", a.sum().compute())
print("b.sum() = ", b.sum().compute())
c = da.tensordot(a, b, axes=1).compute()
for i, j, v in zip(c.coords[0], c.coords[1], c.data):
    print i, j, v
