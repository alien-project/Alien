class SortedLimitedList:
    """A normal list but sorted and with size limit.

    If the size is exceeded, then the elements with the lowest values
    are automatically removed.
    """
    def __init__(self, limit, comparison=lambda a, b: a > b):
        self.limit = limit
        self.comparison = comparison

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __add__(self, other):
        pass

    def add(self, element, assume_value=None):
        """Add a new element.

        It adds a new elements and removes the last one if the size
        limit is exceeded. If assume_value is defined, it will use that
        value to compare the element to other elements in the list to
        find its position.
        """
        pass

    def update_position(self, element):
        """Updates position of an element in the list.

        Returns new position in the list, if the element is removed
        from the list because its value is too low, then it returns
        None.

        Element is required to have 'id' attribute and should have had
        this attribute when adding by add() method. If the element is
        not in the list yet, then it adds a new element.

        To do: you can use id() instead of 'id' attribute, but then you
        need to update dictionary with positions for ids when
        unpickling everything. Maybe __setstate__ or __getstate__ might
        be useful. Consider using hash()
        """

    def position(self, element):
        """Returns the position that the element would have.

        It doesn't add the element to the list, but returns what would
        be the position if you add the element.
        """

    def acceptable(self, element):
        """Return if element would be accepted to the list."""

    def is_full(self):
        """Return if the list has reached the limit."""
        return False

    def last(self):
        """Return the last element of list."""
        return 0


class AutoIncrementId:
    """Generates automatically incremented ids."""
    next_id = 0

    @staticmethod
    def generate(id_=None):
        if id_ is None:
            AutoIncrementId.next_id += 1
            return AutoIncrementId.next_id - 1
        if isinstance(id_, int):
            if id_ >= AutoIncrementId.next_id:
                AutoIncrementId.next_id = id_ + 1
        return id_


def same(a, b):
    if a.__class__ != b.__class__:
        return False

    same_method = getattr(a, 'same', None)
    if callable(same_method):  # to do: make sure that it has one parameter
        return same_method(b)

    if hasattr(a, '__dict__') and hasattr(b, '__dict__'):
        a = a.__dict__
        b = b.__dict__

    if isinstance(a, dict):
        for key in a:
            if key not in b or not same(a[key], b[key]):
                return False
        return True

    if isinstance(a, list) or isinstance(a, tuple) or isinstance(a, set):
        if len(a) != len(b):
            return False
        for key, value in enumerate(a):
            if not same(a[key], b[key]):
                return False
        return True

    return a == b
