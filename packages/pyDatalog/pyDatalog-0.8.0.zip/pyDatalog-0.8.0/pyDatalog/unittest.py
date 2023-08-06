import pyDatalog

pyDatalog.load("""
    + parent(bill,'John Adams') # bill is the parent of John Adams
    ancestor(X,Y) <= parent(X,Y)
    ancestor(X,Y) <= parent(X,Z) & ancestor(Z,Y)
    ancestors[X]==concat(Y, key=Y, sep=',') <= ancestor(X,Y)
""")
print(pyDatalog.ask('ancestor(bill,X)'))
print(pyDatalog.ask('ancestors[bill]==X'))