"""Reads/writes sparse matrices (in COO format) into
   sqlite3 db

.. moduleauthor:: Jonathan Dursi <jonathan@dursi.ca>

"""
import sqlite3
import sparse


def mtxdb_init(filename):
    """Initializes an sqlite3 db for writing sparse matrices.

    :param filename: name of sqlite3 db file to create
    """
    conn = sqlite3.connect(filename)
    c = conn.cursor()

    # Create table, indexed on rows and columns
    c.execute('''create table matrices
                 (matrix text not null, i integer not null,
                  j integer not null, value real not null)''')
    c.execute('''create index columns ON matrices (j)''')
    c.execute('''create index rows ON matrices (i)''')
    c.execute('''create index ms ON matrices (matrix)''')

    conn.commit()
    c.close()


def mtxdb_add_matrix_from_dict(filename, mtxname, mtxdict):
    """Writes a matrix in COO format to sqlite3 db 'filename'.

    :param filename: name of sqlite3 db in which to store the matrix
    :param mtxname: name of matrix (string)
    :param mtxdict: dict of form (row, col): value containing matrix
                    coordinates and data
    """
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    for key, val in mtxdict.items():
        row, col = key
        t = (mtxname, row, col, val,)
        c.execute("insert into matrices values (?, ?, ?, ?)", t)
    conn.commit()
    c.close()


def mtxdb_matrix_shape(filename, mtxname):
    """Returns the shape of a sparse matrix in the db.

    :param filename: name of the sqlite3 db in which the matrix is stored
    :param mtname: name of the matrix(string)
    :rtype: (rowmin, rowmax, colmin, colmax): min/max of rows and columns
    """
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    query = (mtxname,)

    c.execute("select min(i), max(i) from matrices where matrix = ?", query)
    result = c.fetchall()
    rowmin, rowmax = result[0]

    c.execute("select min(j), max(j) from matrices where matrix = ?", query)
    result = c.fetchall()
    colmin, colmax = result[0]
    c.close()

    return rowmin, rowmax, colmin, colmax


def mtxdb_read_chunk(filename, mtxname, rows=None, cols=None):
    """Reads a whole or partial matrix from a sqlite3 db into
       a mod:`sparse` COO matrix

    :param filename: name of sqlite3 db from which to read the matrix
    :param mtxname: name of matrix (string)
    :param rows: optional tuple containing the slice of rows to read in,
                 eg rows=(100,200) will read in rows 100..199.  If None,
                 will read all rows
    :param cols: as with rows, but for columns
    :rtype: mod:`sparse` COO matrix
    """
    rowmin, rowmax, colmin, colmax = mtxdb_matrix_shape(filename, mtxname)
    rowmax += 1
    colmax += 1

    # determine range of matrix we will be returning
    def range_from_option(option, lo, hi):
        if option is None:
            return lo, hi
        try:
            newlo, newhi = option[0], option[1]
        except:
            raise ValueError("Rows/Cols range must be tuple or iterable")
        return newlo, newhi

    minrows, maxrows = range_from_option(rows, rowmin, rowmax)
    mincols, maxcols = range_from_option(cols, colmin, colmax)
    nrows, ncols = maxrows-minrows, maxcols-mincols

    # get matrix chunk
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    query = (mtxname, minrows, maxrows, mincols, maxcols)
    c.execute("""select i, j, value from matrices
                 where matrix = ? and i >= ? and i < ?
                       and j >= ? and j < ?""", query)
    result = c.fetchall()
    c.close()

    result = sorted(result)
    coords = {(i-minrows, j-mincols): v for (i, j, v) in result}
    return sparse.COO(coords, shape=(nrows, ncols))
