.. include globals.rst

Intro
========

`newsuper` provides you Python3k-alike super() for Python2.x

:: versionadded:: 0.3
    Now newsuper is 100% behaving like Python3k's super()

Why
=======

you must hate to write code like this::

    super(Foo, self).__init__()
    
and you might have written (WRONG) code like this::

    super(self.__class__, self).__init__()
    
Python3k's super() saves your ass a bit::

    super().__init__()
    
Example
=======

You can make your topest-level class subclassing `newsuper.Object` ::

    from newsuper import Object

    class Foo(Object):
        def __init__(self):
            self.foo = 1

        @classmethod
        def do_something_with_class(cls):
            return [cls, 'Foo']

        @staticmethod
        def do_something_static():
            return ['Foo']
            
    class Bar(Foo):
        def __init__(self):
            super().__init__()
            self.bar = 1

        @classmethod
        def do_something_static(cls):
            return super().do_something_static() + ['Bar']

    class Baz(Bar):
        def __init__(self):
            super().__init__()
            self.baz = 1

        @classmethod
        def do_something_with_class(cls):
            # Compatible with old super(Baz, cls)
            return super(Baz, cls).do_something_with_class() + ['Baz']

        @staticmethod
        def do_something_static():
            # Yes, you can even super a staticmethod!
            return super().do_something_static() + ['Baz']
        
    if __name__ == '__main__':
        assert Baz().foo == Baz().bar == Baz().baz == 1
        assert Baz.do_something_with_class() == [Baz, 'Foo', 'Baz']
        assert Baz.do_something_static() == ['Foo', 'Bar', 'Baz']

property is supported too.

Install
==========

Let's try it now

Use pip::

    pip install newsuper
    
or easy_install::

    easy_install newsuper
    
also, there is windows installer.
