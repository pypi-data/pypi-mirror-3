#!/usr/bin/python

# Testing Hilton's claim on p.5 of:
#   "CPLS: Cropper's Question" by Bobga, Goldwasser, Hilton and Johnson.
#

# . . 7 3 5 . . 
# . . . . 6 1 5 
# . 6 . . . . 3
# 6 . . . . . .
# 4 . . . . . . 
# 2 . 1 . . . . 
# 3 4 2 . . . . 

import itertools
import ryser
import sys
import vizing

from itertools import islice

from ryser.examples import eg1, fail1
from ryser.hall import hall_inequality_on_cells

from vizing.utils import powerset

A = [6,7,11,15,18,19,20]

n = int(sys.argv[1])
m = int(sys.argv[2])

for X in islice(powerset(A), n, m):

    Y = fail1[0] + list(X) # a hack for testing supersets of fail1[0]
    result = hall_inequality_on_cells(eg1, Y)
    print Y, result

