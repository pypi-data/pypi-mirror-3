from newsuper import Object

class Foo(Object):
    def __init__(self):
        self.foo = 1

    @classmethod
    def do_something(cls):
        return ['Foo']
        
class Bar(Foo):
    def __init__(self):
        super().__init__(self)
        self.bar = 1

    @classmethod
    def do_something(cls):
        return super().do_something() + ['Bar']

class Baz(Bar):
    def __init__(self):
        super().__init__(self)
        self.baz = 1

    @classmethod
    def do_something(cls):
        return super(Baz, cls).do_something() + ['Baz'] # Compatible with old super(Baz, cls)
        
if __name__ == '__main__':
    assert Baz().foo == Baz().bar == Baz().baz == 1
    assert Baz.do_something() == ['Foo', 'Bar', 'Baz']