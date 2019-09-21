from alien.helpers import *


def test_limited_set_add_pop_lowest_element():
    limited_set = LimitedSet(3)
    removed = limited_set.add(3)
    assert removed is None
    limited_set.add(4)
    limited_set.add(2)
    removed = limited_set.add(5)
    assert 2 == removed
    assert 3 == limited_set.lowest_element()
    removed = limited_set.pop()
    assert 3 == removed
    assert 4 == limited_set.lowest_element()


def test_limited_set_update_lowest_element():
    class A:
        def __init__(self, value):
            self.value = value

        def __lt__(self, other):
            return self.value < other.value

    limited_set = LimitedSet(3)
    elements = [A(3), A(4), A(2), A(5)]
    for element in elements:
        limited_set.update(element)
    elements[1].value = 1
    removed = limited_set.update(elements[1])
    assert removed is None
    removed = limited_set.update(A(6))
    assert elements[1] == removed
    assert elements[0] == limited_set.lowest_element()


def test_auto_increment_id():
    assert 0 == AutoIncrementId.generate()
    assert 1 == AutoIncrementId.generate()
    assert 5 == AutoIncrementId.generate(5)
    assert 6 == AutoIncrementId.generate()
    assert "str" == AutoIncrementId.generate("str")
    assert 7 == AutoIncrementId.generate()


def test_same():
    class A:
        def __init__(self, a_, b_):
            self.a = a_
            self.b = b_

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


def test_custom_set_add_remove_sample():
    custom_set = CustomSet()
    custom_set.add(5)
    custom_set.add(4)
    custom_set.remove(4)
    custom_set.add(3)
    for i in range(30):
        a, b = custom_set.sample(2)
        assert a in {5, 3}
        assert b in {5, 3}
        assert a != b


def test_forgetting_list_append_get_item_set_item_len():
    forgetting_list = ForgettingList(5)
    for i in range(20):
        forgetting_list.append(i)
    forgetting_list[18] = 5
    forgetting_list[-3] = 8
    assert forgetting_list[17] == 8
    assert forgetting_list[18] == 5
    assert forgetting_list[19] == 19
    assert len(forgetting_list) == 20
