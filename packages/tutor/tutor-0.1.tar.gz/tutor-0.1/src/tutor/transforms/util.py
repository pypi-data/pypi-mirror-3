def latex_table(L, newline=r'\\', lines=True, hline=None, header=True,
                   valign='c', align_arg=None):
    '''
    Given a list of lists that represents some table, this function returns a 
    string with the corresponding LaTeX code.  
    
    
    Arguments
    ---------
    
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

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
