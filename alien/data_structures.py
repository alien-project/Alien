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

    def is_full(self):
        """Return if the list has reached the limit."""
        return False

    def last(self):
        """Return the last element of list."""
        return 0
