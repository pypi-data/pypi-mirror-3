# This is a sample namespace script
from tutor.scripts import *

# Uncomment in order to enable symbolic computation with sympy or maple
# from tutor.plugins.sympy import * 
# from tutor.plugins.maple import *

# The variables defined in the script will be accessible from 
# templates
someVar = 'foo'

# You can also use the display_vars function to print values to the screen 
# and help with debugging:
with display_vars('Parameters'):
    A = randint(1, 10)
    B = randint(1, 10)
    sumAB = A + B
