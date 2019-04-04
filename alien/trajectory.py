from collections import deque


class Interpretation:
    """Represent interpretation of internal trajectory."""
    def __init__(self):
        self.internal_trajectory = InternalTrajectory()
        # self.storithm_occurrences = [] not needed
        # self.storithm_occurrences_in_cells = [] it seems that it's not needed
        self.storithm_occurrences_starting = []
        self.storithm_occurrences_ending = []
        self.predictor_occurrences = {}
        self.temporary_occurrences = []
        self._temporary_predictor_pointers = []

    def extend(self, atom=None):
        if atom:
            occurrence = StorithmOccurrence(atom, len(self), len(self))
            self.storithm_occurrences_starting.append({occurrence})
            self.storithm_occurrences_ending.append({occurrence})
        else:
            self.storithm_occurrences_starting.append(set())
            self.storithm_occurrences_ending.append(set())

    def add(self, occurrences, temporarily=False):
        if isinstance(occurrences, list):
            for occurrence in occurrences:
                self.add(occurrence, temporarily)
            return None

        occurrence = occurrences
        self.storithm_occurrences_starting[occurrence.start].add(occurrence)
        self.storithm_occurrences_ending[occurrence.end].add(occurrence)

        if temporarily:
            self.temporary_occurrences.append(occurrence)

        for distance, predictor in occurrence.storithm.predictors.items():
            position = occurrence.end + distance
            if position not in self.predictor_occurrences:
                self.predictor_occurrences[position] = set()
            self.predictor_occurrences[position].add(predictor)

            if temporarily:
                pointer = (position, predictor)
                self._temporary_predictor_pointers.append(pointer)

    def add_temporarily(self, occurrence):
        self.add(occurrence, True)

    def clean_temporary(self):
        for temporary_occurrence in self.temporary_occurrences:
            starting_cell = self.storithm_occurrences_starting[
                temporary_occurrence.start
            ]
            starting_cell.remove(temporary_occurrence)
            ending_cell = self.storithm_occurrences_ending[
                temporary_occurrence.end
            ]
            ending_cell.remove(temporary_occurrence)

        for pointer in self._temporary_predictor_pointers:
            if pointer[0] not in self.predictor_occurrences:
                a = 5
            if pointer[1] not in self.predictor_occurrences[pointer[0]]:
                b = 4
            self.predictor_occurrences[pointer[0]].remove(pointer[1])

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
        occurrences_at_the_end = self.storithm_occurrences_ending[-1]
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

    def find_storithm_occurrence_starting_in(self, storithm, position):
        if position not in self.storithm_occurrences_starting:
            return None
        occurrences = self.storithm_occurrences_starting[position]
        for occurrence in occurrences:
            if occurrence.storithm == storithm:
                return occurrence
        return None

    def find_storithm_occurrence_ending_in(self, storithm, position):
        if position not in self.storithm_occurrences_ending:
            return None
        occurrences = self.storithm_occurrences_ending[position]
        for occurrence in occurrences:
            if occurrence.storithm == storithm:
                return occurrence
        return None

    def predictors_in(self, position):
        return (
            self.predictor_occurrences[position]
            if position in self.predictor_occurrences
            else []
        )

    def predictors_at_the_end(self):
        return self.predictors_in(len(self) - 1)

    def __len__(self):
        return max(
            len(self.internal_trajectory.observations),
            len(self.internal_trajectory.actions),
            len(self.storithm_occurrences_starting)
        )


class InternalTrajectory:
    def __init__(self, observations=None, actions=None):
        self.observations = observations or []
        self.actions = actions or []


class StorithmOccurrence:
    def __init__(self, storithm, start, end, found_by=None):
        self.storithm = storithm
        self.start = start
        self.end = end
        self._hash_cache = None
        self.found_by = found_by or []

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.storithm == other.storithm and
            self.start == other.start and
            self.end == other.end
        )

    def __hash__(self):  # remove cache
        if self._hash_cache:
            return self._hash_cache
        prefix = str(self.start) + str(self.end)
        storithm_part = str(
            self.storithm.id if self.storithm.id
            else hash(self.storithm)
        )
        self._hash_cache = hash(prefix + storithm_part)
        return self._hash_cache


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
