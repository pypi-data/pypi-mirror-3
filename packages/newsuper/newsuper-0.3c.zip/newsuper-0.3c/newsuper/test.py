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

# Test working with decorators
def wrap(f):
    def g(*v, **k):
        return f(*v, **k)
    return g

class Baz(Bar):
    def __init__(self):
        super().__init__()
        self.baz = 1

    @classmethod
    def do_something_with_class(cls):
        # Compatible with old super(Baz, cls)
        return super(Baz, cls).do_something_with_class() + ['Baz']

    @staticmethod
    @wrap
    def do_something_static():
        # Yes, you can even super a staticmethod!
        return super().do_something_static() + ['Baz']
    
if __name__ == '__main__':
    assert Baz().foo == Baz().bar == Baz().baz == 1
    assert Baz.do_something_with_class() == [Baz, 'Foo', 'Baz']
    assert Baz.do_something_static() == ['Foo', 'Bar', 'Baz']
