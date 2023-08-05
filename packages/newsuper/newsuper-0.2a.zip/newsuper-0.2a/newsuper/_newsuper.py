""" Python3k-alike style super() in Python2.x """

import types
import inspect
import __builtin__

old_super = super

class_of_code = {}

def my_super(*args):
    if args:
        return old_super(*args)
    stack = inspect.stack()[1]
    frame = stack[0]
    cls = class_of_code[frame.f_code]
    return old_super(cls, cls)

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

        return result_cls

class NewSuper(object):
    __metaclass__ = MetaNewSuper

class Object(NewSuper):
    pass
    
def monkey_patch():
    # XXX: Move this to module level after resolve metaclass conflict
    import __builtin__
    __builtin__.object = Object
