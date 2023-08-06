def maple2py(expr):
    '''
    Convert a Maple sequence of expressions into an equivalent Python/Sympy one.
    Useful for copy/paste code from a Maple worksheet into a python script.
    '''

    # Asignment
    expr = expr.replace(':=', '=')
    expr = expr.replace('*', ' * ').replace('+', ' + ').replace('-', ' - ').replace('^', '**').replace('/', ' * One / ')
    expr = expr.replace('Pi', 'pi')
    return expr

if __name__ == '__main__':
    print maple2py('''''')

