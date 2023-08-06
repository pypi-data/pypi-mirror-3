# -*- coding: utf-8 -*-

from decontractors import *

# This is a more elaborate example, showing how to define a contract
# for a given code block. In this case, we can use the Contract class
# from decontractors to specify three conditions which are checked in
# the local scope (because they are defined there) at the beginning,
# at the end and during the "with" block. To check the invariant, you
# have to manually call the object (see "contract()" below). In this
# case, you want to check the loop invariant before, during and after
# the loop.


def mean(a, b):
    print 'called: mean(%d, %d)' % (a, b)
    a0, b0 = a, b

    precondition = lambda: (b >= a) and ((a+b) % 2 == 0)
    invariant = lambda: (b >= a) and ((a + b) == (a0 + b0))
    postcondition = lambda: (a == b) and (a == (a0 + b0)/2)

    with Contract(precondition, invariant, postcondition) as contract:
        contract()
        while a != b:
            contract()
            a += 1
            b -= 1
            contract()
        contract()

    print 'mean calculated:', a, b


mean(2, 20)

try:
    mean(20, 2)
except DecontractorException, de:
    print 'exception:', de.__class__

try:
    mean(5, 15)
except DecontractorException, de:
    print 'exception:', de.__class__

try:
    mean(2, 7)
except DecontractorException, de:
    print 'exception:', de.__class__

