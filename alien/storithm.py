from trajectory import StorithmOccurrence
from helpers import AutoIncrementId
from random import choice, randint


class Storithm:
    def __init__(self, children, predictors=None, id_=None):
        self.children = children
        self.parent_pointers = []
        self.predictors = predictors or {}
        self.connected_with_children = False
        self.id = id_
        # self.importance = 0
        # self.predictors_importance = 0
        # self.parents_importance = 0
        # self.parents_sampling_base = []

    def generate_id(self):
        self.id = AutoIncrementId.generate()

    def add_parent(self, parent, position):
        self.parent_pointers.append(ParentPointer(parent, position))

    def remove_parent(self, parent, position):
        self.parent_pointers.remove(ParentPointer(parent, position))

    def merge(self, proposed_storithm):
        for key in proposed_storithm.predictors:
            if key not in self.predictors:
                self.predictors[key] = proposed_storithm.predictors[key]

    def connect_with_children(self):
        for key, child in enumerate(self.children):
            child.add_parent(self, key)
        self.connected_with_children = True

    def disconnect_with_children(self):
        for key, child in enumerate(self.children):
            child.remove_parent(self, key)
        self.connected_with_children = False

    def check_occurrence(self, interpretation, child_occurrence, position):
        raise NotImplementedError

    # def update_predictions_importance(self):
    #     # to do: test
    #     self.predictors_importance = 0
    #     for distance, predictor in self.predictors.items():
    #         self.predictors_importance += predictor.importance()
    #
    #     self.importance = self.predictors_importance +
    # self.parents_importance
    #
    #     for child in self.children:
    #         child.update_parents_importance()
    #
    # def update_parents_importance(self):
    #     # to do: test
    #     self.parents_importance = 0
    #     for parent_pointer in self.parent_pointers:
    #         self.parents_importance += parent_pointer.parent.importance
    #
    #     self.importance = self.predictors_importance +
    # self.parents_importance

    def __repr__(self):
        return str(self)

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

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.__dict__ == other.__dict__
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

    @staticmethod
    def create(interpretation, sample_position):
        position = sample_position()
        action = interpretation.internal_trajectory.actions[position]
        return StorithmOccurrence(ActionAtom(action), position, position)

    def __str__(self):
        return "a_" + str(self.action.id)

    def __eq__(self, other):
        if self.id is None or other.id is None:
            return (
                self.__class__ == other.__class__ and
                self.action == other.action
            )
        return self.id == other.id


class StateAtom(Atom):
    def __init__(self, state_id, value, predictors=None):
        self.state_id = state_id
        self.value = value
        super().__init__(predictors)

    @staticmethod
    def create(interpretation, sample_position):
        position = sample_position()
        observation = interpretation.internal_trajectory.observations[position]
        state_id = randint(0, len(observation) - 1)
        value = observation[state_id]
        atom = StateAtom(state_id, value)
        return StorithmOccurrence(atom, position, position)

    def __str__(self):
        return "s_" + str(self.state_id) + "_" + str(self.value)

    def __eq__(self, other):
        if self.id is None or other.id is None:
            return (
                self.__class__ == other.__class__ and
                self.state_id == other.state_id and
                self.value == other.value
            )
        return self.id == other.id


class Procedure(Storithm):
    def __init__(self, children, predictors=None):
        self._unconnected_children = {0: children[0]}
        super().__init__(children, predictors)

    @staticmethod
    def create(interpretation, sample_position):
        position = sample_position()
        joint_cells = [
            interpretation.storithm_occurrences_ending_in_cells[position - 1],
            interpretation.storithm_occurrences_starting_in_cells[position]
        ]
        if joint_cells[0] == [] or joint_cells[1] == []:
            return None
        first_child_occurrence = choice(joint_cells[0])
        second_child_occurrence = choice(joint_cells[1])
        children = [
            [first_child_occurrence.storithm, second_child_occurrence.storithm]
        ]
        found_by = [
            first_child_occurrence.storithm,
            second_child_occurrence.storithm
        ]
        return StorithmOccurrence(
            Procedure(children),
            first_child_occurrence.start,
            second_child_occurrence.end,
            found_by
        )

    def connect_with_children(self):
        for i in self._unconnected_children:
            for j, child in enumerate(self._unconnected_children[i]):
                child.add_parent(self, (i, j))
        self._unconnected_children = {}
        self.connected_with_children = True

    def disconnect_with_children(self):
        for i, group in enumerate(self.children):
            for j, child in enumerate(group):
                child.remove_parent(self, (i, j))
        self._unconnected_children = dict(enumerate(self.children))
        self.connected_with_children = False
    
    def merge(self, proposed_storithm):  # test
        super().merge(proposed_storithm)
        # optimization to do: use binary search for children,
        # sorted by storithm id (change it to SortedSet and it's ok)
        unpacked_children = proposed_storithm.children[0]
        if unpacked_children in self.children:
            return None
        self.children += proposed_storithm.children
        self._unconnected_children[len(self.children) - 1] = unpacked_children
        self.connected_with_children = False

    def check_occurrence(self, interpretation, child_occurrence, position):
        if position[1] == 0:
            start = child_occurrence.end + 1
            second_child = self.children[position[0]][1]
            second_child_occurrence = interpretation.\
                find_storithm_occurrence_starting_in(second_child, start)
            if second_child_occurrence:
                return StorithmOccurrence(
                    self,
                    child_occurrence.start,
                    second_child_occurrence.end
                )

        if position[1] == 1:
            end = child_occurrence.start - 1
            second_child = self.children[position[0]][0]
            second_child_occurrence = interpretation.\
                find_storithm_occurrence_ending_in(second_child, end)
            if second_child_occurrence:
                return StorithmOccurrence(
                    self,
                    second_child_occurrence.start,
                    child_occurrence.end
                )

        return None

    def __str__(self):
        first_child = self.children[0][0]
        second_child = self.children[0][1]
        return " ".join([str(first_child), str(second_child)])

    def __eq__(self, other):
        if self.id is None or other.id is None:
            return (
                self.__class__ == other.__class__ and
                str(self) == str(other)
            )
        return self.id == other.id


class Condition(Storithm):
    def __init__(self, condition_child, body_child, predictors=None):
        super().__init__([condition_child, body_child], predictors)

    def check_occurrence(self, interpretation, child_occurrence, position):
        return None

    def __eq__(self, other):
        if self.id is None or other.id is None:
            return (
                self.__class__ == other.__class__ and
                self.children == other.children
            )
        return self.id == other.id


class Loop(Storithm):
    def __init__(self, condition_child, body_child, predictors=None):
        super().__init__([condition_child, body_child], predictors)

    def check_occurrence(self, interpretation, child_occurrence, position):
        return None

    def __eq__(self, other):
        if self.id is None or other.id is None:
            return (
                self.__class__ == other.__class__ and
                self.children == other.children
            )
        return self.id == other.id


class Fusion(Storithm):
    def check_occurrence(self, interpretation, child_occurrence, position):
        return True

    def __eq__(self, other):
        if self.id is None or other.id is None:
            return (
                self.__class__ == other.__class__ and
                self.children == other.children
            )
        return self.id == other.id
