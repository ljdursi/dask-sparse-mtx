import dask_sparse_mtx as dsm
import dask
import dask.multiprocessing
import dask.dot
import dask.delayed as delayed
import sparse

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

# compute manually using dask distributed

a = {}
b = {}


def get_matrix_chunk(fname, mname, size, chunksize, i, j):
    rows = (i*chunksize, (i+1)*chunksize)
    cols = (j*chunksize, (j+1)*chunksize)

    return dsm.mtxdb_read_chunk(fname, mname, rows=rows, cols=cols)


for i in range(nchunks):
    for j in range(nchunks):
        a[(i, j)] = delayed(get_matrix_chunk)(dbfile, 'A', size, chunksize, i, j)
        b[(i, j)] = delayed(get_matrix_chunk)(dbfile, 'B', size, chunksize, i, j)

partialprod = {}

for i in range(nchunks):
    for j in range(nchunks):
        for k in range(nchunks):
            partialprod[(i, j, k)] = delayed(sparse.tensordot)(a[(i, k)], b[(k, j)], axes=1)

c = {}
for i in range(nchunks):
    for j in range(nchunks):
        c[(i, j)] = delayed(reduce)((lambda a, b: a + b), [partialprod[(i, j, k)] for k in range(nchunks)])

res = dask.compute([c[(i, j)] for i in range(nchunks) for j in range(nchunks)])[0]

item = 0
for i in range(nchunks):
    for j in range(nchunks):
        c[(i, j)] = res[item]
        item += 1

print(c)
for i, j, v in zip(c[(1, 2)].coords[0], c[(1, 2)].coords[1], c[(1, 2)].data):
    print i, j, v
