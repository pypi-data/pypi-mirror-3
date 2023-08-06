'''
Created on Jun 28, 2012

@author: pcarbonn
'''

from sqlalchemy.ext.declarative import DeclarativeMeta

Class_dict = {}

class metaMixin(type): 
    def __init__(cls, name, bases, dct):
        """when creating a subclass of Mixin, save the subclass in Class_dict. """
        super(metaMixin, cls).__init__(name, bases, dct)
        Class_dict[name]=cls
        cls.has_SQLAlchemy = False
        for base in bases:
            cls.has_SQLAlchemy = cls.has_SQLAlchemy or base.__module__ in ('sqlalchemy.ext.declarative',)
        pass
    def __getattr__(cls, method):
        """when access to an attribute of a subclass of Mixin fails, return a callable that queries pyEngine """
        #TODO call super ?
        print("%s.%s" % (cls.__name__, method))
        if cls in ('Mixin', 'metaMixin') or method in ('__mapper_cls__', '_decl_class_registry', '__sa_instrumentation_manager__'):
            raise AttributeError
        def my_callable(self, *args):
            predicate_name = "%s.%s" % (cls.__name__, method)
            
            terms = []
            # first term is self
            if self == []:
                terms.append( Symbol('X') )
            elif self.__class__ != cls:
                raise TypeError("Object is incompatible with the class that is queried.")
            else:
                terms.append( self ) 
            
            for i, arg in enumerate(args):
                terms.append( Symbol('X%i' % i) if arg == [] else arg)
                
            literal = Literal(predicate_name, terms)
            result = default_datalog_engine._ask_literal(literal)
            if result: 
                result = list(zip(*result)) # transpose result
                if self==[]:
                    self.extend(result[0])
                for i, arg in enumerate(args):
                    if arg==[]:
                        arg.extend(result[i+1])
            return result
        return my_callable

    

Mixin = metaMixin('Mixin', (object,), {})

class sqlMetaMixin(metaMixin, DeclarativeMeta): pass