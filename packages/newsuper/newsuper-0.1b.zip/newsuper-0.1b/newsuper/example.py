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
