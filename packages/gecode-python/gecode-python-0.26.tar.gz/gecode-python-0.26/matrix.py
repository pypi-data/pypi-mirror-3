__all__ = ('Matrix',)

class MatrixBase(object):

    def __init__(self, nrows, ncols):
        super(MatrixBase, self).__init__()
        self.nrows = nrows
        self.ncols = ncols
        self.fmt1 = "{: >}"
        self.fmt2 = " {: >%s} "

    def __getitem__(self, key):
        i,j = key
        if i<0 or i>=self.nrows:
            raise IndexError("failed: %d <= i=%s < %d" % (0,i,self.nrows))
        if j<0 or j>=self.ncols:
            raise IndexError("failed: %d <= j=%s < %d" % (0,j,self.ncols))
        return self._getitem(i, j)

    def _getitem(self, i, j):
        raise NotImplemented()

    def __setitem__(self, key, val):
        i,j = key
        if i<0 or i>=self.nrows:
            raise IndexError()
        if j<0 or j>=self.ncols:
            raise IndexError()
        self._setitem(i, j, val)

    def _setitem(self, i, j, val):
        raise NotImplemented()

    def __len__(self):
        return self.nrows*self.ncols

    def __iter__(self):
        for i in range(self.nrows):
            for j in range(self.ncols):
                yield self[i,j]

    def row(self, i):
        return MatrixRow(self, i)

    def col(self, j):
        return MatrixCol(self, j)

    def slice(self, i1, j1, i2, j2):
        return MatrixSlice(self, i1, j1, i2, j2)

    @property
    def rows(self):
        for i in range(self.nrows):
            yield self.row(i)

    @property
    def cols(self):
        for j in range(self.ncols):
            yield self.col(j)

    def __str__(self):
        fmt = self.fmt1
        m = Matrix(self.nrows, self.ncols,
                   tuple(fmt.format(x) for x in self))
        w = tuple(max(len(x) for x in col) for col in m.cols)
        m = Matrix(self.nrows, self.ncols)
        for j in range(self.ncols):
            fmt = self.fmt2 % w[j]
            for i in range(self.nrows):
                m[i,j] = fmt.format(self[i,j])
        w = tuple(len(x) for x in m.row(1))
        sep = "+".join(tuple("-"*wd for wd in w))
        sep = "\n%s\n" % sep
        return sep.join(tuple("|".join(tuple(r)) for r in m.rows))


class Matrix(MatrixBase):

    def __init__(self, nrows, ncols, values=None):
        super(Matrix, self).__init__(nrows, ncols)
        if values is None:
            values = [None for k in range(nrows*ncols)]
        else:
            assert nrows*ncols == len(values)
        self.values = values

    def _getitem(self, i, j):
        return self.values[self.ncols*i+j]

    def _setitem(self, i, j, val):
        self.values[self.ncols*i+j] = val


class MatrixSlice(MatrixBase):

    def __init__(self, matrix, i1, j1, i2, j2):
        self.matrix = matrix
        self.i_offset = i1
        self.j_offset = j1
        w = i2-i1
        if w<0: w=0
        self.nrows = w
        w = j2-j1
        if w<0: w=0
        self.ncols = w

    def _getitem(self, i, j):
        return self.matrix[self.i_offset+i,self.j_offset+j]

    def _setitem(self, i, j, val):
        self.matrix[self.i_offset+i,self.j_offset+j] = val


class MatrixRow(MatrixSlice):

    def __init__(self, matrix, row):
        super(MatrixRow, self).__init__(matrix, row, 0, row+1, matrix.ncols)

    def __getitem__(self, j):
        return super(MatrixRow, self).__getitem__((0,j))

    def __setitem__(self, j, val):
        return super(MatrixRow, self).__setitem__((0,j), val)

    def __iter__(self):
        for j in range(self.ncols):
            yield self[j]


class MatrixCol(MatrixSlice):

    def __init__(self, matrix, col):
        super(MatrixCol, self).__init__(matrix, 0, col, matrix.nrows, col+1)

    def __getitem__(self, i):
        return super(MatrixCol, self).__getitem__((i,0))

    def __setitem__(self, i, val):
        return super(MatrixCol, self).__setitem__((i,0), val)

    def __iter__(self):
        for i in range(self.nrows):
            yield self[i]
