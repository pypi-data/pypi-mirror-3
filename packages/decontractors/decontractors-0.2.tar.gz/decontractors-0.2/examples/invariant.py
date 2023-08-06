# -*- coding: utf-8 -*-

from decontractors import *

# Example showing how to use an invariant in multiple functions.
# The invariant is checked both at the start and at the end of the function.

class ShoppingList(object):
    def __init__(self):
        self.total = 0
        self.limit = 10
        self.items = []

    # Define it once here, then use it as a decorator below
    costs_inv = Invariant(lambda: self.total < self.limit and self.total >= 0)

    @costs_inv
    def add(self, item, costs):
        self.total += costs
        self.items.append(item)

    @costs_inv
    def discount(self, costs):
        self.total -= costs


list = ShoppingList()
list.add('Bananas', 4.3)

# Try .add()ing something else here, so that the total cost exceeds the limit

# Try giving a discount that makes the total cost go below zero
list.discount(1)

# If you want to handle violations of the invariant expression, use this:
try:
    list.add('Milk', 7)
except DecontractorException, de:
    print 'add failed. content now:', list.total, 'with', list.items

