from tutor.scripts import *

with display_vars('Parameters'):
    intA = a = randint(1, 10)
    intB = b = randint(1, 10)
    sumAB = answer(a + b, clear=True)
    dis1 = answer(a - b)
    dis2 = answer(b - a)
    dis3 = answer(b * a)
    dis4 = distractor()
