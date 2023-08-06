# -*- coding: utf-8 -*-

from decontractors import *

# Simple example on how you could use decontractors to specify
# properties of input values and properties of the return value

@Precondition(lambda: x > 0 and y > 0)
@Postcondition(lambda: __return__ == (x + y))
def positive_nonzero_addition(x, y):
    # Try changing the expression to return something else
    return x + y

# Try calling the function with one or both parameters set to zero or negative
print positive_nonzero_addition(4, 1)

