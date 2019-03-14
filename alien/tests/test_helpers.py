from helpers import *


def test_same():
    class A:
        def __init__(self, a_, b):
            self.a = a_
            self.b = b

        def __eq__(self, other):
            return (self.a, self.b) == (other.a, other.b)

    class B:
        def __init__(self, c, d):
            self.c = c
            self.d = d

        def __eq__(self, other):
            return self.c == other.c

    class C:
        def __init__(self, c, d):
            self.c = c
            self.d = d

        def same(self, other):
            return self.c == other.c

    a = A(1, B(2, 3))
    b = A(1, B(2, 4))
    assert not same(a, b)

    a = A(1, C(2, 3))
    b = A(1, C(2, 4))
    assert same(a, b)

    a = A(1, {1: C(1, 1)})
    b = A(1, {1: C(1, 2)})
    assert same(a, b)

    a = A(1, [C(1, 1)])
    b = A(1, [C(1, 2)])
    assert same(a, b)

    a = A(1, (C(1, 1),))
    b = A(1, (C(1, 2),))
    assert same(a, b)

    assert same([2, 3], [2, 3])
