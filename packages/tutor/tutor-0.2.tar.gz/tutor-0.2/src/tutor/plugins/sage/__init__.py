from sage.all import *
x, y, z, i, j, k, t = var('x,y,z,i,j,k,t')

if __name__ == '__main__':
    o = maple(1) / 2
    o2 = maple('int(x, x)')
    print(o, o2, type(o), type(o2))
    print(dir(o))
    print(latex(o2))
    print(latex(x ** 2 / 2))
