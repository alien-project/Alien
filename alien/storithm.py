from prediction import Predictor
from trajectory import StorithmOccurrence
from random import choice


class Storithm:
    def __init__(self, children, predictors=None):
        self.children = children
        self.parent_pointers = []
        self.parents_sampling_base = []
        self.predictors = predictors or {}
        self.importance = 0
        self.predictors_importance = 0
        self.parents_importance = 0

    def add_parent(self, parent, position):
        self.parent_pointers.append(ParentPointer(parent, position))

    def update_predictions_importance(self):
        # to do: test
        self.predictors_importance = 0
        for distance, predictor in self.predictors.items():
            self.predictors_importance += predictor.importance()

        self.importance = self.predictors_importance + self.parents_importance

        for child in self.children:
            child.update_parents_importance()

    def update_parents_importance(self):
        # to do: test
        self.parents_importance = 0
        for parent_pointer in self.parent_pointers:
            self.parents_importance += parent_pointer.parent.importance

        self.importance = self.predictors_importance + self.parents_importance

    def connect_with_children(self):
        for key, child in enumerate(self.children):
            child.add_parent(self, key)

    def check_occurrence(self, interpretation, child_occurrence, position):
        raise NotImplementedError

    def __str__(self):
        return str(self.children[0]).join(" ").join(str(self.children[1]))

    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        return hash(str(self))


class ParentPointer:
    def __init__(self, parent, position):
        self.parent = parent
        self.position = position

    def check_parent_occurrence(self, interpretation, child_occurrence):
        return self.parent.check_occurrence(
            interpretation,
            child_occurrence,
            self.position
        )


class Atom(Storithm):
    def __init__(self, predictors=None):
        super().__init__([], predictors)

    def check_occurrence(self, interpretation, child_occurrence, position):
        raise RuntimeError("Atom should not be a parent.")

    def __str__(self):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError


class ActionAtom(Atom):
    def __init__(self, action, predictors=None):
        self.action = action
        super().__init__(predictors)

    def __str__(self):
        return "a_" + self.action.id

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.action == other.action
        )


class StateAtom(Atom):
    def __init__(self, state_id, value, predictors=None):
        self.state_id = state_id
        self.value = value
        super().__init__(predictors)

    def __str__(self):
        return "s_" + self.state_id + "_" + self.value

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.state_id == other.state_id and
            self.value == other.value
        )


class Procedure(Storithm):
    @staticmethod
    def propose_new(interpretation, margin, impact_discount_factor):
        distance_sampling_base = Procedure._distance_sampling_base(
            impact_discount_factor
        )
        distance = margin + choice(distance_sampling_base)
        first_child_end = len(interpretation) - distance - 2
        second_child_start = first_child_end + 1
        joint_cells = [
            interpretation.storithm_occurrences_ending_in_cells[
                first_child_end
            ],
            interpretation.storithm_occurrences_starting_in_cells[
                second_child_start
            ]
        ]
        if joint_cells[0] == [] or joint_cells[1] == []:
            return None
        first_child_occurrence = choice(joint_cells[0])
        second_child_occurrence = choice(joint_cells[1])
        children = [
            first_child_occurrence.storithm,
            second_child_occurrence.storithm
        ]
        margin_cell = len(interpretation) - margin - 1
        distance = margin_cell - second_child_occurrence.end
        return StorithmOccurrence(
            Procedure(children, {distance: Predictor()}),
            first_child_occurrence.start,
            second_child_occurrence.end,
            children
        )

    def check_occurrence(self, interpretation, child_occurrence, position):
        if position == 0:
            start = child_occurrence.end + 1
            second_child_occurrence = interpretation.\
                find_storithm_occurrence_starting_in(self.children[1], start)
            if second_child_occurrence:
                return StorithmOccurrence(
                    self,
                    child_occurrence.start,
                    second_child_occurrence.end
                )

        if position == 1:
            end = child_occurrence.start - 1
            second_child_occurrence = interpretation.\
                find_storithm_occurrence_ending_in(self.children[0], end)
            if second_child_occurrence:
                return StorithmOccurrence(
                    self,
                    second_child_occurrence.start,
                    child_occurrence.end
                )

        return None

    @staticmethod
    def _distance_sampling_base(impact_discount_factor):
        return [0, 0, 0, 1, 1, 2, 2]  # for now, it's hardcoded

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.children == self.children
        )


class Loop(Storithm):
    def __init__(self, condition_child, body_child, predictors=None):
        super().__init__([condition_child, body_child], predictors)

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.children == other.children
        )

    def check_occurrence(self, interpretation, child_occurrence, position):
        return None


class Fusion(Storithm):
    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.children == other.children
        )

    def check_occurrence(self, interpretation, child_occurrence, position):
        return True
