.. include globals.rst

Intro
========

`newsuper` provides you Python3k-alike super() for Python2.x,

Why
=======

you must hate to write code like this::

    super(Foo, self).__init__()
    
and you might have written (WRONG) code like this::

    super(self.__class__, self).__init__()
    
Python3k's super() saves your ass a bit::

    super().__init__()
    
but this looks evil, and confusing for classmethods

Example
=======

You can create an `Object` class subclassing NewSuper,

and make your topest-level class subclassing it.::

    from newsuper import NewSuper
    
    class Object(NewSuper):
        pass
    
    class Foo(Object):
        def __init__(self):
            self.foo = 1

        @classmethod
        def do_something(cls):
            return 'nothing'
            
    class Bar(Foo):
        def __init__(self):
            super().__init__(self)
            self.bar = 1

        @classmethod
        def do_something(cls):
            return [super().do_something(), 'another thing']
            
    if __name__ == '__main__':
        assert Bar().foo == Bar().bar == 1
        assert Bar.do_something() == ['nothing', 'another thing']

property is supported too.

.. warning::

    There is difference between `newsuper` and Python3k super()
    
    in Python3k super(), super().method() == super(Foo, self).method()
    
    In `newsuper`, super() always returns a proxy of class, not instance
    
    in other words, you must pass self by yourself!

Install
==========

Let's try it now

Use pip::

    pip install newsuper
    
or easy_install::

    easy_install newsuper
    
also, there is windows installer.
