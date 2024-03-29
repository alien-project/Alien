from random import choice
from time import time


class LimitedSet:
    """Set with a limit of how many elements it can have.

    If the limit is exceeded, the lowest value is removed. The elements
    have to be hashable (__eq__ and __hash__) and comparable (at least
    __lt__ has to be defined).

    This data structure is created with the purpose to be fast at
    adding an element, updating an element and removing the lowest
    element. It has worst case time complexity O(log n) for all of
    these operations thanks to using heap (with dictionary / hash
    table to store positions in the heap) internally.
    """
    def __init__(self, limit):
        self.limit = limit
        self._heap = []
        self._positions = {}

    def add(self, element):
        if element in self._positions:
            return None
        limit_reached = (len(self._heap) == self.limit)
        lower_than_lowest = (
            self.lowest_element() and
            element < self.lowest_element()
        )
        if limit_reached and lower_than_lowest:
            return element

        self._heap.append(element)
        position = self._heapify_up(len(self._heap) - 1)
        self._positions[element] = position
        if len(self._heap) > self.limit:
            return self.pop()
        return None

    def pop(self):
        if len(self) == 0:
            return None
        returned = self._heap[0]
        self._swap(0, len(self._heap) - 1)
        self._positions.pop(self._heap[-1])
        self._heap.pop()
        self._heapify_down(0)
        return returned

    def update(self, element):
        if element not in self._positions:
            return self.add(element)
        self._heap[self._positions[element]] = element
        self._heapify(self._positions[element])
        return None

    def lowest_element(self):
        return self._heap[0] if self._heap else None

    def _heapify_up(self, element_position):
        if element_position == 0:
            return 0
        parent_position = (element_position - 1) // 2
        if self._heap[element_position] < self._heap[parent_position]:
            self._swap(element_position, parent_position)
            return self._heapify_up(parent_position)
        return element_position

    def _heapify_down(self, element_position):
        left = 2 * element_position + 1
        right = 2 * element_position + 2
        lowest = element_position
        if left < len(self._heap) and self._heap[left] < self._heap[lowest]:
            lowest = left
        if right < len(self._heap) and self._heap[right] < self._heap[lowest]:
            lowest = right
        if lowest != element_position:
            self._swap(element_position, lowest)
            return self._heapify_down(lowest)
        return element_position

    def _heapify(self, element_position):
        self._heapify_up(element_position)
        self._heapify_down(element_position)

    def _swap(self, i, j):
        self._positions[self._heap[i]] = j
        self._positions[self._heap[j]] = i
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]

    def __contains__(self, element):
        return element in self._positions

    def __len__(self):
        return len(self._heap)

    def __str__(self):
        if not len(self):
            return "Empty limited set"
        return (
            "Lowest: " +
            str(self.lowest_element()) +
            ", Count: " +
            str(len(self))
        )


class CustomSet:
    """My own implementation of set.

    This is needed because with default python implementation of set
    you can't sample an element in the most efficient way possible
    (random.sample() converts set to a tuple).
    """
    def __init__(self):
        self._dict = {}
        self._list = []

    def add(self, element):
        if element not in self._dict:
            self._list.append(element)
            self._dict[element] = len(self._list) - 1

    def remove(self, element):
        try:
            self._list[self._dict[element]] = None
            self._dict.pop(element)
        except KeyError:
            raise KeyError(
                "Trying to remove an element that is not in the set."
            )

    def sample(self, count=1):
        if count > len(self):
            return None
        selected = set()
        result = []
        for i in range(count):
            element = choice(self._list)
            while element is None or element in selected:
                element = choice(self._list)
            selected.add(element)
            result.append(element)
        return result

    def clean_up(self):
        """Makes sampling quicker.

        If there are many elements added to the set and then removed,
        sampling takes more time, so it's sometimes good to call this
        method to clear None values if there were really lot of values
        added to the set and then removed (this happens in Alien
        algorithm if action space is big because there are many
        elements added temporarily and then removed).
        """
        self._list = list(filter(lambda x: x is not None, self._list))
        self._dict = {element: key for key, element in enumerate(self._list)}

    def __contains__(self, element):
        return element in self._dict

    def __len__(self):
        return len(self._dict)

    def __str__(self):
        return str(set(self._list))

    def __repr__(self):
        return self.__str__()


class ForgettingList:
    """
    Normal list but remembers only last :limit elements.

    This data structure is useful when you store a lot of elements in a
    list but you always use only let's say last 20 elements. The point
    of this data structure is that you save memory, but at the same
    time you can use it in exactly the same way as normal list,
    supposing that you always use only last elements in the list.
    """
    def __init__(self, limit):
        self._limit = limit
        self._elements = [None] * limit
        self._count = 0

    def append(self, element):
        self._elements[self._convert_key(self._count)] = element
        self._count += 1

    def __getitem__(self, key):
        if not self._is_valid(key):
            raise IndexError("I don't remember that far.")
        return self._elements[self._convert_key(key)]

    def __setitem__(self, key, value):
        if not self._is_valid(key):
            raise IndexError("I don't remember that far.")
        self._elements[self._convert_key(key)] = value

    def _convert_key(self, key):
        if key < 0:
            return self._count % self._limit + key
        return self._count % self._limit - self._count + key

    def _is_valid(self, key):
        return (
            max(self._count - self._limit, 0) <= key <= self._count or
            -self._limit < key < 0
        )

    def __len__(self):
        return self._count


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


class Timer:
    def __init__(self):
        self.times = {}
        self.active = None
        self.start_time = None

    def start(self, name):
        self.active = name
        self.start_time = time()

    def stop(self):
        time_ = time() - self.start_time
        self.times[self.active] = (
            self.times[self.active] + time_ if self.active in self.times
            else time_
        )
        self.active = None


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
        if isinstance(a, set):
            a = list(a)
        for key, value in enumerate(a):
            if not same(a[key], b[key]):
                return False
        return True

    return a == b
