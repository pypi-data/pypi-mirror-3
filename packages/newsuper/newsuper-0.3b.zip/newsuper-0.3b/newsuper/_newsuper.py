""" Python 3.x super() in 2.x """

import types
import inspect
import __builtin__

class_of_code = {}
static_methods = set()

__builtin__.__super__ = super

def super(*args):
    if args:
        return __super__(*args)
    stack = inspect.stack()[1]
    frame = stack[0]
    cls = class_of_code[frame.f_code]
    if frame.f_code in static_methods:
        return __super__(cls, cls)
    firstarg = frame.f_locals[frame.f_code.co_varnames[0]]
    return __super__(cls, firstarg)

__builtin__.super = super

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
