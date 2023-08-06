"""
This file shows how to use pyDatalog using facts stored in python objects.

It has 3 parts :
    1. define python class and business rules 
    2. create python objects for 2 employees
    3. Query the objects using the datalog engine
"""

import pyDatalog # or: from pyDatalog import pyDatalog

# Factorial
pyDatalog.clear()
@pyDatalog.program()
def factorial(): 
    (factorial[N] == F) <= (N < 2) & (F==1)
    (factorial[N] == F) <= ((N > 1) & (F == N*factorial[N-1]))
    assert ask((factorial[1] == F)) == set([(1, 1)])
    assert ask(factorial[4] == F) == set([(4, 24)])
