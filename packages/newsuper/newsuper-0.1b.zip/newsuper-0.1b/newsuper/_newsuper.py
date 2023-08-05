""" Python3k-alike style super() in Python2.x """

import types

class Super(object):
    def __init__(self, cls):
        self.__thisclass__ = cls
        
    def __getattribute__(self, name):
        if name == '__thisclass__':
            return object.__getattribute__(self, name)
            
        for cls in self.__thisclass__.__mro__[1:]:
            try:
                return getattr(cls, name)
            except AttributeError:
                pass
        raise AttributeError(name)

class MetaNewSuper(type):
    """ This metaclass injects a super() into methods' globals,
    so methods know which class they are defined in. """
 
    def __new__(cls, name, bases, attrs):
    
        def my_super():
            return Super(result_cls)
            
        def wrap(func):
            if func is None:
                return None
            # XXX: Use a dict proxy here in case some bad methods want to modify globals
            my_func_globals = dict(func.func_globals)
            my_func_globals['super'] = my_super
            return types.FunctionType(
                func.func_code,
                my_func_globals,
                func.func_name,
                func.func_defaults,
                func.func_closure,
            )

        for k, v in attrs.items():
            if isinstance(v, classmethod):
                attrs[k] = classmethod(wrap(v.__func__))
            elif isinstance(v, property):
                attrs[k] = property(wrap(v.fget), wrap(v.fset), wrap(v.fdel))
            elif isinstance(v, types.FunctionType):
                attrs[k] = wrap(v)
                    
        result_cls = type.__new__(cls, name, bases, attrs)
        return result_cls

class NewSuper(object):
    __metaclass__ = MetaNewSuper
