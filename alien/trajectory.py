from collections import deque
from .helpers import CustomSet, ForgettingList


class Interpretation:
    """Represent interpretation of internal trajectory."""
    def __init__(
        self,
        type_groups,
        forgetting_lists_limit = 1000
    ):
        self.type_groups = type_groups
        self.internal_trajectory = InternalTrajectory()
        self._storithm_occurrences_starting = ForgettingList(
            forgetting_lists_limit
        )
        self._storithm_occurrences_ending = ForgettingList(
            forgetting_lists_limit
        )
        self._storithm_occurrences_starting_by_type = ForgettingList(
            forgetting_lists_limit
        )
        self._storithm_occurrences_ending_by_type = ForgettingList(
            forgetting_lists_limit
        )
        self._predictor_occurrences = ForgettingList(forgetting_lists_limit)
        self.temporary_occurrences = []
        self._temporary_predictor_pointers = []

    def extend(self, atom=None):
        starting = {}
        ending = {}
        starting_by_type = {group: CustomSet() for group in self.type_groups}
        ending_by_type = {group: CustomSet() for group in self.type_groups}
        self._storithm_occurrences_starting.append(starting)
        self._storithm_occurrences_ending.append(ending)
        self._storithm_occurrences_starting_by_type.append(starting_by_type)
        self._storithm_occurrences_ending_by_type.append(ending_by_type)
        if atom:
            self.add_at_the_end(atom)

    def add(self, occurrence, temporarily=False):
        if isinstance(occurrence, list):
            occurrences = occurrence
            for occurrence in occurrences:
                self.add(occurrence, temporarily)
            return None

        if occurrence.end >= len(self):
            to_extend = len(self) - occurrence.end + 1
            for _ in range(to_extend):
                self.extend()

        try:
            starting_cell = self._storithm_occurrences_starting[occurrence.start]
        except IndexError:
            # raise IndexError("Forgetting list limit is too low")
            return None
        starting_cell[occurrence.storithm] = occurrence
        ending_cell = self._storithm_occurrences_ending[occurrence.end]
        ending_cell[occurrence.storithm] = occurrence

        for group in self.type_groups:
            storithm_in_group = self._is_storithm_in_group(
                occurrence.storithm,
                group
            )
            if not storithm_in_group:
                continue
            starting_cell = self._storithm_occurrences_starting_by_type[
                occurrence.start
            ]
            starting_cell[group].add(occurrence)
            ending_cell = self._storithm_occurrences_ending_by_type[
                occurrence.end
            ]
            ending_cell[group].add(occurrence)

        if temporarily:
            self.temporary_occurrences.append(occurrence)

        for distance, predictor in occurrence.storithm.predictors.items():
            position = occurrence.end + distance
            if position >= len(self._predictor_occurrences):
                start = len(self._predictor_occurrences)
                for _ in range(start, position + 1):
                    self._predictor_occurrences.append(set())
            self._predictor_occurrences[position].add(predictor)

            if temporarily:
                pointer = (position, predictor)
                self._temporary_predictor_pointers.append(pointer)

    def add_temporarily(self, occurrence):
        self.add(occurrence, True)

    def clear_temporary(self):
        for temporary_occurrence in self.temporary_occurrences:
            starting_cell = self._storithm_occurrences_starting[
                temporary_occurrence.start
            ]
            if temporary_occurrence.storithm in starting_cell:
                starting_cell.pop(temporary_occurrence.storithm)
            ending_cell = self._storithm_occurrences_ending[
                temporary_occurrence.end
            ]
            if temporary_occurrence.storithm in ending_cell:
                ending_cell.pop(temporary_occurrence.storithm)
            for group in self.type_groups:
                storithm_in_group = self._is_storithm_in_group(
                    temporary_occurrence.storithm,
                    group
                )
                if not storithm_in_group:
                    continue
                starting_cell = self._storithm_occurrences_starting_by_type\
                    [temporary_occurrence.start]
                if temporary_occurrence in starting_cell[group]:
                    starting_cell[group].remove(
                        temporary_occurrence
                    )
                ending_cell = self._storithm_occurrences_ending_by_type\
                    [temporary_occurrence.end]
                if temporary_occurrence in ending_cell[group]:
                    ending_cell[group].remove(
                        temporary_occurrence
                    )

        for pointer in self._temporary_predictor_pointers:
            if pointer[1] in self._predictor_occurrences[pointer[0]]:
                self._predictor_occurrences[pointer[0]].remove(pointer[1])

        self.temporary_occurrences = []
        self._temporary_predictor_pointers = []

    def add_at_the_end(self, storithm, occurrence_length=1, temporarily=False):
        start = len(self) - occurrence_length
        end = len(self) - 1
        self.add(StorithmOccurrence(storithm, start, end), temporarily)

    def add_at_the_end_temporarily(self, storithm, occurrence_length=1):
        self.add_at_the_end(storithm, occurrence_length, True)

    def interpret(self, temporarily=False):
        if len(self) < 1:
            return None

        queue = deque()
        occurrences_at_the_end = self._storithm_occurrences_ending[-1].values()
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
                    self.add(parent_occurrence, temporarily)
                    queue.append(parent_occurrence)

    def interpret_temporarily(self):
        self.interpret(True)

    def find_storithm_occurrence_starting_in(
        self,
        storithm,
        starting_in
    ):
        return (
            self._storithm_occurrences_starting[starting_in][storithm]
            if (
                0 <= starting_in < len(self) and
                storithm in self._storithm_occurrences_starting[starting_in]
            )
            else None
        )

    def find_storithm_occurrence_ending_in(
        self,
        storithm,
        ending_in
    ):
        return (
            self._storithm_occurrences_ending[ending_in][storithm]
            if (
                0 <= ending_in < len(self) and
                storithm in self._storithm_occurrences_ending[ending_in]
            )
            else None
        )

    def sample_storithm_occurrences_starting_in(
        self,
        starting_in,
        type_group,
        count
    ):
        if starting_in >= len(self):
            return None
        starting_cell = self._storithm_occurrences_starting_by_type[starting_in]
        return starting_cell[type_group].sample(count)

    def sample_storithm_occurrences_ending_in(
        self,
        ending_in,
        type_group,
        count
    ):
        if len(self) > len(self._storithm_occurrences_ending_by_type):
            a = 0
        if ending_in < 0:  # it can happen in procedure that it samples from -1 and it's ok
            a = 0
        if ending_in >= len(self):
            return None
        ending_cell = self._storithm_occurrences_ending_by_type[ending_in]
        return ending_cell[type_group].sample(count)

    def sample_storithm_occurrence_starting_in(
        self,
        starting_in,
        type_group
    ):
        occurrences = self.sample_storithm_occurrences_starting_in(
            starting_in,
            type_group,
            1
        )
        return occurrences[0] if occurrences else None

    def sample_storithm_occurrence_ending_in(
        self,
        ending_in,
        type_group
    ):
        occurrences = self.sample_storithm_occurrences_ending_in(
            ending_in,
            type_group,
            1
        )
        return occurrences[0] if occurrences else None

    def predictors_in(self, position):
        return (
            self._predictor_occurrences[position]
            if position < len(self._predictor_occurrences)
            else set()
        )

    def predictors_at_the_end(self):
        return self.predictors_in(len(self) - 1)

    def _is_storithm_in_group(self, storithm, group):
        for type_ in group:
            if isinstance(storithm, type_):
                return True
        return False

    def __len__(self):
        return len(self._storithm_occurrences_starting)


class InternalTrajectory:
    def __init__(self, observations=None, actions=None):
        self.observations = observations or []
        self.actions = actions or []


class StorithmOccurrence:
    def __init__(self, storithm, start, end):
        self.storithm = storithm
        self.start = start
        self.end = end
        self._hash_cache = None

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.storithm == other.storithm and
            self.start == other.start and
            self.end == other.end
        )

    def __hash__(self):  # is it needed at all
        if self._hash_cache:
            return self._hash_cache
        prefix = str(self.start) + str(self.end)
        storithm_part = str(
            self.storithm.id if self.storithm.id
            else hash(self.storithm)
        )
        self._hash_cache = hash(prefix + storithm_part)
        return self._hash_cache

    def __repr__(self):
        return (
            str(self.storithm) +
            " start: " +
            str(self.start) +
            " end: " +
            str(self.end)
        )
