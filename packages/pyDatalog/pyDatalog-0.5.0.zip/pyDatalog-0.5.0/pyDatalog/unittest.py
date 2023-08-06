"""
pyDatalog

Copyright (C) 2012 Pierre Carbonnelle

This library is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.

This library is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc.  51 Franklin St, Fifth Floor, Boston, MA 02110-1301
USA

"""
import cProfile
import math
import time

import pyDatalog

def test():

    # instantiate a pyDatalog engine
    datalog_engine = pyDatalog.Datalog_engine()
    
    print("Defining a datalog program in %s..." % pyDatalog.Engine)
        
    datalog_engine = pyDatalog.Datalog_engine()
    datalog_engine.load("""
        + even(0)
        even(N) <= (N > 0) & (N1==N-1) & odd(N1)
        odd(N) <= (N2==N+2) & ~ even(N) & (N2>0)
    """)
    assert datalog_engine.ask('odd(3)', _fast=True) == set([(3,)])
    assert datalog_engine.ask('odd(3)'             ) == set([(3,)])
    assert datalog_engine.ask('odd(5)', _fast=True) == set([(5,)])
    assert datalog_engine.ask('odd(5)'            ) == set([(5,)])
    assert datalog_engine.ask('even(5)', _fast=True) == None
    assert datalog_engine.ask('even(5)'            ) == None
    assert datalog_engine.ask('odd(10001)') == set([(10001,)])

    @pyDatalog.program(datalog_engine)
    def _():
        # literal cannot have a literal as argument
        _error = False
        try:
            ask('odd(X)')
        except: _error = True
        assert _error

    '''
    datalog_engine.load("""
        + p(0)
        p(X) <= ~ q(X)
        q(X) <= ~ p(X)
    """)
    assert datalog_engine.ask('p(5)') == set([(5,)])
    '''
    
    print("Done.")

if __name__ == "__main__":
    for pyDatalog.Engine in ('Lua', 'Python', ):    # 
        pyDatalog.default_datalog_engine = pyDatalog.Datalog_engine()
        test()
        #cProfile.runctx('test()', globals(), locals())