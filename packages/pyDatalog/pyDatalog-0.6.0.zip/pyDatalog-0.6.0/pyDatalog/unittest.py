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
import pyEngine

import pyDatalog
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base(cls=pyDatalog.Mixin, metaclass=pyDatalog.metaMixin)
print Base.__mro__

class Employee(Base): # --> Employee inherits pyDatalog capability to use logic clauses
    def __init__(self, name, manager, salary):
        super(Employee, self).__init__()
        self.name = name
        self.manager = manager # direct manager of the employee, or None
        self.salary = salary # monthly salary of the employee
    def __repr__(self): # specifies how to display the employee
        return 'name: '+ self.name

    @pyDatalog.program() # --> the following function contains pyDatalog clauses
    def _():
        pass
        # the salary class of employee X is computed as a function of his/her salary
        # (Employee.salary_class[X]==N) <= (Employee.salary[X]==N1) & (N==int(X/1000))

        # all the indirect managers of employee X are derived from his manager, recursively
        Employee.indirect_manager(X,Y) <= (Employee.manager(X,Y))
        #Employee.indirect_manager(X,Y) <= (Employee.manager[X]==Y)
        #Employee.indirect_manager(X,Y) <= (Employee.manager[X]==Z) & Employee.indirect_manager(Z,Y)

# create 2 employees
John = Employee('John', None, 6800)
Mary = Employee('Mary', John, 6300)

def test():
    datalog_engine = pyDatalog.default_datalog_engine

    print("Defining a datalog program in %s..." % pyDatalog.Engine)
    
    #datalog_engine.assert_fact('Employee.manager', Mary, John)
    X, Y = [], []
    Employee.indirect_manager(Mary, Y)
    print(Y)
    X, Y = [], []
    Employee.indirect_manager(X, John)
    print(X[0])
    
    X = []
    Employee.tartempion(X)
    
    @pyDatalog.program()
    def _():
        # literal cannot have a literal as argument
        _error = False
        try:
            Employee.manager(object(), John)
        except: _error = True
        assert _error
    
    print("Done.")

if __name__ == "__main__":
    for pyDatalog.Engine in ('Python', ):    # 'Lua', 
        #pyDatalog.default_datalog_engine.clear()
        test()
        #cProfile.runctx('test()', globals(), locals())