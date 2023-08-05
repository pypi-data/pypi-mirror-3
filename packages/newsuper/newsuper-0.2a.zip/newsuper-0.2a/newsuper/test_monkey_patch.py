import newsuper

newsuper.monkey_patch()

class Foo(object):
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
        
if __name__ == '__main__':
    assert Bar().foo == Bar().bar == 1
    assert Bar.do_something() == ['Foo', 'Bar']
