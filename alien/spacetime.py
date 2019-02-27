class Spacetime:
    def __init__(self, observations=None, actions=None):
        self.observations = observations if observations else []
        self.actions = actions if actions else []


class SpacetimeInterpretation:
    def __init__(self):
        self.storithm_occurrences = []
        self.storithm_occurrences_in_cells = []
        self.storithm_occurrences_starting_in_cells = []
        self.storithm_occurrences_ending_in_cells = []

    def add_storithm_occurrence(self, position):
        pass

    def create_new_storithms(
            self,
            new_procedures_count,
            impact_discount_factor,
            max_accepted_distance
    ):
        """Creates new storithms and predictors, returns them both."""
        for i in range(new_procedures_count):
            pass
        return [[], []]

    def interpret(self):
        pass


class StorithmOccurrence:
    def __init__(self, storithm, start, end):
        self.storithm = storithm
        self.start = start
        self.end = end
