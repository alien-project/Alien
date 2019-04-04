class LimitedSet:
    """Set with a limit of how many elements it can have.

    If the limit is exceeded, the lowest value is removed. The elements
    have to be hashable (__eq__ and __hash__) and comparable (at least
    __lt__ has to be defined).

    This data structure is created with the purpose to be fast at
    adding an element, updating an element and removing the lowest
    element. It has time complexity O(log n) for all of these operations
    thanks to using heap internally.
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

    def __contains__(self, item):
        return item in self._positions

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
