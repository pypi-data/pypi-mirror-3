from anyvc.util import cachedproperty
from itertools import count

def test_cached_property():
    # kinda stupid
    class test(object):
        def __init__(self):
            self.count = count()

        @cachedproperty
        def prop(self):
            return self.count.next()

    t = test()

    assert t.prop == 0
    assert t.prop == 0
    del t.prop
    assert t.prop == 1
