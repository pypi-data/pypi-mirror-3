try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

__all__ = ['latex_table', 'Table', 'Cell']

def latex_table(L, newline=r'\\', lines=True, hline=None, header=True,
                   valign='c', align_arg=None):
    '''
    Given a list of lists that represents some table, this function returns a 
    string with the corresponding LaTeX code. 
    
    
    Parameters
    ----------
    L : list-like
        List of strings. L[i][j] is the data in the i-th row and j-th column.
    newline : str
        LaTeX command for newline. Default is \\\\.
    lines : bool
        If True, show the lines in the table.
    hline : str
        LaTeX command before beginning each row. Default is to use '\\hline'.
    header : bool
        If True, emphasize the first row in the table.
    valing : char
        Vertical aligmenet: can be (c)entralized, (l)eft or (r)ight.
    align_arg : str
        Manually override the second argument to the \\tabular environment. The 
        default behavior is to create this variable from 'valign' and 'lines'. 
        (e.g.: a table with 3 columns called with the default arguments will 
        have 'align_arg' set to "c|c|c")
    
    Notes
    -----
    
    For more complicated jobs involving tables, see the `Table` type in this 
    module.
     

    Examples
    --------
    
    >>> print(latex_table([['1.A', '1.B',   '2'], 
    ...                    [ None,  None, None ]], lines=False))
    \\begin{tabular}{ccc}
      1.A   & 1.B   & 2     \\\\
            &       &       \\\\
    \\end{tabular}
    '''

    # Get shape of table
    n_cols = max(map(len, L))

    # Normalize L filling empty values
    L_new = []
    for row in L:
        row_new = []
        L_new.append(row_new)
        for i in range(n_cols):
            try:
                value = row[i]
            except IndexError:
                value = None
            if value:
                value = unicode(value).ljust(5)
            else:
                value = u'     '
            row_new.append(value)

    # All data is to be appended to the following list
    out = ['\\begin{tabular}']

    # Get the align_arg for the table
    if align_arg is None:
        if valign in set('clr'):
            join_char = ('|' if lines else '')
            align_arg = join_char.join([valign] * n_cols)
        else:
            raise ValueError("'valign' must be one of 'c' (centered), 'l' (left) or 'r' (right)")
    out.append('{%s}\n' % align_arg)

    # Print content of each row
    if hline is None:
        hlines = '\\hline\n' if lines else ''
    out.append(hlines)
    for idx, row in enumerate(L_new):
        line = '  ' + ' & '.join(row)
        line += ' %s\n' % newline
        out.append(line)
        out.append(hlines)
        if idx == 0 and header:
            out.append(hlines)

    # Return table
    out.append('\\end{tabular}')
    return ''.join(out)

#===============================================================================
# Table and accessory classes
#===============================================================================
class Table(object):
    def __init__(self, nrows=1, ncols=1):
        '''
        Initializes a table with a given cell count and row count.
        
        Attributes
        ----------
        
        ncols, nrows : int
            Number of columns and rows.
            
        
        Examples
        --------
        
        
        '''
        # Number of rows and columns must be positive
        if ncols < 1:
            raise  ValueError("invalid value: ncols=%s" % ncols)
        if nrows < 1:
            raise  ValueError("invalid value: nrows=%s" % ncols)

        # Table used to store values
        self._table = table = []
        for _ in range(nrows):
            new_row = []
            table.append(new_row)
            for _ in range(ncols):
                new_row.append(Cell())

    #===========================================================================
    # Properties
    #===========================================================================
    @property
    def nrows(self):
        return len(self._table)

    @property
    def ncols(self):
        return len(self._table[0])

    #===========================================================================
    # API methods
    #===========================================================================
    def add_col(self, idx= -1, cells=None):
        '''
        Adds a new column to table at the given index.
        
        Arguments
        ---------
        
        idx : int
            Index at which column is added to table. If 'idx' is not given, the 
            new column will be added to the end of the table.
        cells : sequence
            A sequence of Cell objects or strings that will be added in the 
            new column. This sequence can be larger or smaller than the required
            cell count. In this case, it will be truncated or filled with empty
            cells accordingly. 
        '''
        cells = self._normalized_cell_seq(cells, self.nrows)
        idx = (len(self.ncols) if idx == -1 else idx)
        for col, cell in zip(self._table, cells):
            col.insert(idx, cell)

    def add_row(self, idx= -1):
        pass

    def del_col(self, idx= -1):
        pass

    def del_row(self, idx= -1):
        pass

    def split_row(self, idx):
        raise NotImplementedError

    def split_col(self, idx):
        raise NotImplementedError

    def split_cell(self, i, j):
        raise NotImplementedError

    def get_row(self, idx):
        raise NotImplementedError

    def get_col(self, idx):
        raise NotImplementedError

    def render(self, method='latex', *args, **kwds):
        '''
        Renders table using the given method (only 'latex', 'struct' and 
        'ascii' are currently supported).
        '''

        method_name = 'render_' + method
        try:
            delegate = getattr(self, method_name)
        except (AttributeError, NotImplementedError):
            raise ValueError("unsupported rendering method: '%s'" % method)
        return delegate(*args, **kwds)

    def render_struct(self):
        '''
        Display only the raw structure of the table. X's stands for non-empty
        cells.
        '''
        def draw_line():
            return '+' + '---+' * self.ncols + '\n'

        def draw_cell(cell):
            if cell.data:
                return ' X '
            else:
                return '   '

        out = StringIO()
        out.write(draw_line())
        for row in self._table:
            out.write(':')
            out.write(':'.join(map(draw_cell, row)))
            out.write(':\n')
            out.write(draw_line())
        return out.getvalue()

    def render_ascii(self):
        pass

    def render_latex(self):
        pass

    #===========================================================================
    # Magical methods
    #===========================================================================
    def __getitem__(self, (i, j)):
        return self._table[i][j]

    def __setitem__(self, (i, j), cell):
        cell = cell_or_string(cell)
        self._table[i][j] = cell

#===============================================================================
# Auxiliary classes
#===============================================================================
class Cell(object):
    def __init__(self, data=None, multicol=1):
        self.data = data

    def copy(self):
        pass

    def render(self):
        pass

class Null(object):
    def __init__(self, root, idx):
        pass

    def render(self):
        return ''

#===============================================================================
# Utility functions
#===============================================================================
def normalized_cell_seq(self, cells, size):
    '''
    Generates a sequence of Cell objects of a given size. The 'cells' parameter
    can be None (to generate a list of empty cells) or a sequence of strings
    and Cell/Empty objects.  
    '''
    cells = iter([] if cells is None else cells)

    # Consumes all cells...
    for idx in range(size):
        try:
            yield cell_or_string(cells.next())
        except StopIteration:
            break

    #... and returns empty cells afterwards
    while idx < size:
        yield Cell()

def cell_or_string(obj):
    '''
    Returns 'obj' if it is a Cell or a Null object and Cell(obj) if obj is a 
    string. Raises TypeError otherwise.
    '''
    if isinstance(obj, (Cell, Null)):
        return obj
    elif isinstance(obj, basestring):
        return Cell(obj)
    else:
        raise TypeError

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
