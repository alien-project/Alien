from .trajectory import StorithmOccurrence
from .helpers import AutoIncrementId
from random import uniform, randint


class Storithm:
    def __init__(self, children, predictors=None):
        self.children = children
        self.parent_pointers = set()
        self.predictors = self._prepare_predictors(predictors)
        self.connected_with_children = False
        self.id = None
        self._hash_cache = None
        # self.importance = 0
        # self.predictors_importance = 0
        # self.parents_importance = 0
        # self.parents_sampling_base = []

    def generate_id(self):
        self.id = AutoIncrementId.generate()

    def add_parent(self, parent, position):
        self.parent_pointers.add(ParentPointer(parent, position))

    def remove_parent(self, parent, position):
        self.parent_pointers.remove(ParentPointer(parent, position))

    def merge(self, proposed_storithm):
        for key in proposed_storithm.predictors:
            if key not in self.predictors:
                self.predictors[key] = proposed_storithm.predictors[key]
                self.predictors[key].storithm = self

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

    def _prepare_predictors(self, predictors):
        if not predictors:
            return {}
        for key in predictors:
            predictors[key].storithm = self
            predictors[key].distance = key
        return predictors

    def __repr__(self):
        return str(self)

    def __str__(self):
        children_str = [str(child) for child in self.children]
        return " ".join(children_str)

    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        if not self._hash_cache:
            self._hash_cache = hash(str(self))
        return self._hash_cache


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

    def __hash__(self):
        return hash((self.parent, self.position))


class StorithmRepository:
    def __init__(self):
        self.storithms = {}
        self.atoms = {}

    def add(self, storithm):
        storithm.generate_id()
        self.storithms[storithm] = storithm
        if isinstance(storithm, Atom):
            self.atoms[storithm] = storithm

    def remove(self, storithm):
        if storithm in self.storithms:
            self.storithms.pop(storithm)
            storithm.disconnect_with_children()
            if isinstance(storithm, Atom):
                self.atoms.pop(storithm)

    def find(self, storithm):
        return None

    def __contains__(self, storithm):
        return storithm in self.storithms


class Atom(Storithm):
    def __init__(self, predictors=None):
        super().__init__([], predictors)

    def check_occurrence(self, interpretation, child_occurrence, position):
        raise RuntimeError("Atom should not be a parent.")

    def __str__(self):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        return super().__hash__()


class ActionAtom(Atom):
    def __init__(self, action, predictors=None):
        self.action = action
        super().__init__(predictors)

    @staticmethod
    def create(interpretation, sample_position):
        position = sample_position()
        if len(interpretation.internal_trajectory.actions) <= position:
            a = 5
        if position < 0:
            a = 5
        try:
            action = interpretation.internal_trajectory.actions[position]
        except IndexError:
            a = 5
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

    def __hash__(self):
        return super().__hash__()


class StateAtom(Atom):
    def __init__(self, tape_id, value, predictors=None):
        self.tape_id = tape_id
        self.value = value
        super().__init__(predictors)

    @staticmethod
    def create(interpretation, sample_position):
        position = sample_position()
        try:
            observation = interpretation.internal_trajectory.observations[
                position
            ]
        except IndexError:
            a = 5
        tape_id = randint(0, len(observation) - 1)
        value = int(observation[tape_id])
        atom = StateAtom(tape_id, value)
        return StorithmOccurrence(atom, position, position)

    def __str__(self):
        return "s_" + str(self.tape_id) + "_" + str(int(self.value))

    def __eq__(self, other):
        if self.id is None or other.id is None:
            return (
                self.__class__ == other.__class__ and
                self.tape_id == other.tape_id and
                self.value == other.value
            )
        return self.id == other.id

    def __hash__(self):
        return super().__hash__()


class Procedure(Storithm):
    def __init__(self, children, predictors=None):
        self._unconnected_children = {0: children[0]}
        super().__init__(children, predictors)

    @staticmethod
    def create(interpretation, sample_position):
        position = sample_position()
        type_group = (ActionAtom, ConditionalStatement, Loop, Procedure)
        first_child_occurrence = interpretation.\
            sample_storithm_occurrence_ending_in(position - 1, type_group)
        second_child_occurrence = interpretation.\
            sample_storithm_occurrence_starting_in(position, type_group)
        if not first_child_occurrence or not second_child_occurrence:
            return None
        children = [
            [first_child_occurrence.storithm, second_child_occurrence.storithm]
        ]
        return StorithmOccurrence(
            Procedure(children),
            first_child_occurrence.start,
            second_child_occurrence.end
        )

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
        unpacked_children = proposed_storithm.children[0]
        if unpacked_children in self.children:
            return None
        self.children += proposed_storithm.children
        self._unconnected_children[len(self.children) - 1] = unpacked_children
        self.connected_with_children = False

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

    def __hash__(self):
        return super().__hash__()


class Condition(Storithm):
    ADDING_PROBABILITY = 0.3

    def __init__(self, children, predictors=None):
        children.sort(key=lambda x: (x.tape_id, x.value))
        super().__init__(children, predictors)

    @staticmethod
    def create(interpretation, sample_position):
        position = sample_position()
        count = 1
        while uniform(0, 1) < Condition.ADDING_PROBABILITY:
            count += 1
        occurrences = interpretation.sample_storithm_occurrences_ending_in(
            position,
            (StateAtom,),
            count
        )  # bug: there are storithms that have two the same state atoms,
        #  why doesn't it sample without replacement?
        #  because it samples storithm occurrence, not storithm!!
        #  although it's on the same position so it should be equal
        #  probably something wrong with storithm ids, it calculates
        #  hash based on storithm id, if storithm ids are different
        #  then hash is different
        if not occurrences:
            return None
        children = [occurrence.storithm for occurrence in occurrences]
        return StorithmOccurrence(Condition(children), position, position)

    def check_occurrence(self, interpretation, child_occurrence, position):
        position_in_interpretation = child_occurrence.start
        for key, child in enumerate(self.children):
            if key == position:
                continue
            child_occurs = interpretation.find_storithm_occurrence_ending_in(
                child,
                position_in_interpretation
            )
            if not child_occurs:
                return None
        return StorithmOccurrence(
            self,
            position_in_interpretation,
            position_in_interpretation
        )

    def __eq__(self, other):
        if self.id is None or other.id is None:
            return (
                self.__class__ == other.__class__ and
                self.children == other.children
            )
        return self.id == other.id

    def __hash__(self):
        return super().__hash__()


class ConditionalStatement(Storithm):
    POSITION_CONDITION = 0
    POSITION_BODY = 1

    def __init__(self, condition_child, body_child, predictors=None):
        super().__init__([condition_child, body_child], predictors)

    @staticmethod
    def create(interpretation, sample_position):
        position = sample_position()
        condition_occurrence = interpretation.\
            sample_storithm_occurrence_ending_in(
                position,
                (Condition,)
            )
        body_occurrence = interpretation.\
            sample_storithm_occurrence_starting_in(
                position,
                (ActionAtom, Loop, Procedure)
            )
        if not condition_occurrence or not body_occurrence:
            return None
        condition_child = condition_occurrence.storithm
        body_child = body_occurrence.storithm
        return StorithmOccurrence(
            ConditionalStatement(condition_child, body_child),
            position,
            body_occurrence.end
        )

    def check_occurrence(self, interpretation, child_occurrence, position):
        position_in_interpretation = child_occurrence.start
        if position == self.POSITION_CONDITION:
            body_occurrence = interpretation.\
                find_storithm_occurrence_starting_in(
                    self._body_child(),
                    position_in_interpretation
                )
            if body_occurrence:
                return StorithmOccurrence(
                    self,
                    position_in_interpretation,
                    body_occurrence.end
                )
        if position == self.POSITION_BODY:
            condition_occurrence = interpretation.\
                find_storithm_occurrence_ending_in(
                    self._condition_child(),
                    position_in_interpretation
                )
            if condition_occurrence:
                return StorithmOccurrence(
                    self,
                    position_in_interpretation,
                    child_occurrence.end
                )
        return None

    def _condition_child(self):
        return self.children[self.POSITION_CONDITION]

    def _body_child(self):
        return self.children[self.POSITION_BODY]

    def __eq__(self, other):
        if self.id is None or other.id is None:
            return (
                self.__class__ == other.__class__ and
                self.children == other.children
            )
        return self.id == other.id

    def __hash__(self):
        return super().__hash__()


class Loop(Storithm):
    def __init__(self, condition_child, body_child, predictors=None):
        super().__init__([condition_child, body_child], predictors)

    @staticmethod
    def create(interpretation, sample_position):
        position = sample_position()
        first_condition_occurrence = interpretation.\
            sample_storithm_occurrence_ending_in(position, (Condition,))
        first_body_occurrence = interpretation.\
            sample_storithm_occurrence_starting_in(
                position, (ActionAtom, ConditionalStatement, Loop, Procedure)
            )
        if not first_condition_occurrence or not first_body_occurrence:
            return None

        condition_child = first_condition_occurrence.storithm
        body_child = first_body_occurrence.storithm

        i = 0
        condition_occurrence = first_condition_occurrence
        body_occurrence = first_body_occurrence
        loop_end = position
        while condition_occurrence:
            i += 1
            if not body_occurrence:
                return None
            start = body_occurrence.end + 1
            loop_end = body_occurrence.end
            condition_occurrence = interpretation.\
                find_storithm_occurrence_starting_in(condition_child, start)
            body_occurrence = interpretation.\
                find_storithm_occurrence_starting_in(body_child, start)

        condition_occurrence = first_condition_occurrence
        body_occurrence = first_body_occurrence
        loop_start = position
        while condition_occurrence and body_occurrence:
            i += 1
            end = body_occurrence.start - 1
            loop_start = body_occurrence.start
            body_occurrence = interpretation.\
                find_storithm_occurrence_ending_in(body_child, end)
            if not body_occurrence:
                break
            condition_occurrence = interpretation.\
                find_storithm_occurrence_starting_in(
                    condition_child,
                    body_occurrence.start
                )

        if i == 2:
            return None

        loop = Loop(condition_child, body_child)
        return StorithmOccurrence(loop, loop_start, loop_end)

    def check_occurrence(self, interpretation, child_occurrence, position):
        return None  # to do (will return two occurrences)

    def __eq__(self, other):
        if self.id is None or other.id is None:
            return (
                self.__class__ == other.__class__ and
                self.children == other.children
            )
        return self.id == other.id

    def __hash__(self):
        return super().__hash__()


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

    def __hash__(self):
        return super().__hash__()
