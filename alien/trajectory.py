from copy import deepcopy
from collections import deque


class Interpretation:
    """Represent interpretation of internal trajectory."""
    def __init__(self):
        self.storithm_occurrences = []
        # self.storithm_occurrences_in_cells = [] it seems that it's not needed
        self.storithm_occurrences_starting_in_cells = []
        self.storithm_occurrences_ending_in_cells = []
        self.predictors_in_cells = []

    def extend(self, atom=None):
        if atom:
            occurrence = StorithmOccurrence(atom, len(self), len(self))
            self.storithm_occurrences.append(occurrence)
            self.storithm_occurrences_starting_in_cells.append([occurrence])
            self.storithm_occurrences_ending_in_cells.append([occurrence])
        else:
            self.storithm_occurrences_starting_in_cells.append([])
            self.storithm_occurrences_ending_in_cells.append([])

    def add(self, occurrence):
        self.storithm_occurrences.append(occurrence)
        self.storithm_occurrences_starting_in_cells[occurrence.start].append(
            occurrence
        )
        self.storithm_occurrences_ending_in_cells[occurrence.end].append(
            occurrence
        )

    def add_at_the_end(self, storithm, occurrence_length=1):
        start = len(self) - occurrence_length
        end = len(self) - 1
        self.add(StorithmOccurrence(storithm, start, end))

    def interpret(self):
        if len(self) < 1:
            return None

        queue = deque()
        occurrences_at_the_end = self.storithm_occurrences_ending_in_cells[-1]
        for occurrence in occurrences_at_the_end:
            queue.append(occurrence)

        while queue:
            occurrence = queue.popleft()
            for parent_pointer in occurrence.storithm.parent_pointers:
                parent_occurrence = parent_pointer.check_parent_occurrence(
                    self,
                    occurrence
                )
                if parent_occurrence:
                    self.add(parent_occurrence)
                    queue.append(parent_occurrence)

    def find_storithm_occurrence_starting_in(self, storithm, position):
        occurrences = self.storithm_occurrences_starting_in_cells[position]
        for occurrence in occurrences:
            if occurrence.storithm == storithm:
                return occurrence
        return None

    def find_storithm_occurrence_ending_in(self, storithm, position):
        occurrences = self.storithm_occurrences_ending_in_cells[position]
        for occurrence in occurrences:
            if occurrence.storithm == storithm:
                return occurrence
        return None

    def predictors_at_the_end(self):
        return self.predictors_in_cells[len(self) - 1]

    def __deepcopy__(self, memo=None):
        memo = memo or {}
        new = type(self)()
        new.storithm_occurrences = deepcopy(self.storithm_occurrences, memo)
        new.storithm_occurrences_starting_in_cells = deepcopy(
            self.storithm_occurrences_starting_in_cells,
            memo
        )
        new.storithm_occurrences_ending_in_cells = deepcopy(
            self.storithm_occurrences_ending_in_cells,
            memo
        )
        return new

    def __len__(self):
        return len(self.storithm_occurrences_starting_in_cells)


class StorithmOccurrence:
    def __init__(self, storithm, start, end, found_by=None):
        self.storithm = storithm
        self.start = start
        self.end = end
        self.found_by = found_by or []

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.__dict__ == other.__dict__
        )


class PredictorOccurrence:
    def __init__(self, storithm_occurrence, predictor, distance):
        self.storithm_occurrence = storithm_occurrence
        self.predictor = predictor
        self.distance = distance

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.__dict__ == other.__dict__
        )
