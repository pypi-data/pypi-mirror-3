""" Python3k-alike style super() in Python2.x """

import types
import inspect
import __builtin__

old_super = super

class_of_code = {}
static_methods = set()

def my_super(*args):
    if args:
        return old_super(*args)
    stack = inspect.stack()[1]
    frame = stack[0]
    cls = class_of_code[frame.f_code]
    if frame.f_code in static_methods:
        return old_super(cls, cls)
    firstarg = frame.f_locals[frame.f_code.co_varnames[0]]
    return old_super(cls, firstarg)

__builtin__.super = my_super

class MetaNewSuper(type):
    """ This metaclass records a mapping of method's func_code to their class,
    so methods know which class they are defined in. """

    def __new__(cls, name, bases, attrs):
        result_cls = type.__new__(cls, name, bases, attrs)

        def record(func):
            if func is None:
                return
            class_of_code[func.func_code] = result_cls

        for k, v in attrs.items():
            if isinstance(v, classmethod):
                record(v.__func__)
            elif isinstance(v, property):
                record(v.fget)
                record(v.fset)
                record(v.fdel)
            elif isinstance(v, types.FunctionType):
                record(v)
            elif isinstance(v, staticmethod):
                record(v.__func__)
                static_methods.add(v.__func__.func_code)
                
        return result_cls

class Object(object):
    __metaclass__ = MetaNewSuper
