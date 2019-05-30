from .trajectory import Interpretation
from .helpers import LimitedSet, AutoIncrementId, Timer
from .memory import Memory
from .storithm import ActionAtom, StateAtom, Condition, ConditionalStatement
from .storithm import Atom, Loop, Procedure
from .prediction import Estimator, Predictor
from functools import partial
from numpy import exp
from numpy.random import choice
from copy import deepcopy


class RLAgent:
    def __init__(
        self,
        observation_shape,
        external_actions,
        target_return=0,
        antitarget_return=0,
        return_discount_factor=0.5,
        horizon=1,
        impact_discount_factor=0.5,
        time_importance_factor=1.1,
        create_storithm_types=None,
        max_predictors_count=5000,
        memory_tapes_count=2,
        memory_tapes_length=5000,
        internal_actions=None,
        starting_points=None,
        softmax_temperature=1
    ):
        self._observation_shape = observation_shape
        self._external_actions = external_actions
        self.target_return = target_return
        self.antitarget_return = antitarget_return
        self._return_discount_factor = return_discount_factor
        self._horizon = horizon
        self.impact_discount_factor = impact_discount_factor
        self.time_importance_factor = time_importance_factor
        self.create_storithm_types = self._prepare_create_storithm_types(
            create_storithm_types
        )
        self._create_storithm_types_left = []
        self.max_predictors_count = max_predictors_count
        self._internal_actions = self._prepare_internal_actions(
            internal_actions,
            observation_shape,
            starting_points
        )
        self._interpretation = Interpretation(
            (
                (StateAtom,),
                (Condition,),
                (ActionAtom, Loop, Procedure),
                (ActionAtom, ConditionalStatement, Loop, Procedure)
            )
        )
        self._predictors = LimitedSet(max_predictors_count)
        self._rewards = []
        self._returns = []
        self._current_external_tour = 0
        self._current_internal_tour = 0
        self._importance_for_distance_cache = []
        self._memory = Memory(  # better set memory as an optional parameter
            observation_shape,
            memory_tapes_length,
            memory_tapes_count
        )
        self._storithms = {}
        self._atoms = {}
        self._sample_weight = 1
        self._interpretation_cache = {}
        self._external_actions_positions = []
        self._last_reward_multiplier = (
            self._return_discount_factor **
            self._horizon
        )
        self._softmax_temperature = softmax_temperature
        self._timer = Timer()

    def act(self, observation, reward):
        self._prepare_before_learn(reward)
        self._learn()
        self._prepare_after_learn(observation)

        self._prepare_before_act_internally()
        action = self._act_internally()
        self._prepare_after_act_internally(action)
        while not action.external:
            self._prepare_before_act_internally()
            action = self._act_internally()
            self._prepare_after_act_internally(action)

        return action

    @staticmethod
    def default_internal_actions(
        observation_dimensionality,
        memory_tapes_count=2,
        starting_points=None
    ):
        return RLAgent._convert_to_actions_dict(
            RLAgent._load_observation_actions() +
            RLAgent._set_value_actions(memory_tapes_count) +
            RLAgent._move_pointer_actions(
                observation_dimensionality,
                memory_tapes_count
            ) +
            RLAgent._go_to_starting_point_actions(
                observation_dimensionality,
                starting_points
            )
        )

    def _prepare_before_learn(self, reward):
        self._timer.start("prepare_before_learn")
        self._rewards.append(reward)

        previous_return = self._returns[-1] if self._returns else 0
        reward_before_horizon = (
            self._rewards[-self._horizon - 2]
            if self._current_external_tour > self._horizon
            else 0
        )
        return_ = (
            (
                (previous_return - reward_before_horizon) *
                self._return_discount_factor
            ) +
            reward * self._last_reward_multiplier
        )
        self._returns.append(return_)
        self._timer.stop()

    def _learn(self):
        self._create()
        self._fit()
        self._merge()

    def _create(self):
        if self._current_external_tour <= self._horizon:
            return None

        self._timer.start("create")
        # return_ = self._returns[-1]
        # max_new_predictors_count = self._max_new_predictors_count(return_)
        # new_predictors_count = 0

        storithm_type = self._storithm_type_to_create(first_in_tour=True)
        while storithm_type:
            occurrence = storithm_type.create(
                self._interpretation,
                self._sample_position
            )
            if not occurrence:
                storithm_type = self._storithm_type_to_create()
                continue

            self._add_predictor_to_storithm(occurrence)

            if occurrence.storithm in self._storithms:
                self._storithms[occurrence.storithm].merge(occurrence.storithm)
                occurrence.storithm = self._storithms[occurrence.storithm]
            else:
                self._add_storithm(occurrence.storithm)

            self._storithms[occurrence.storithm].connect_with_children()

            self._interpretation.add(occurrence)

            # new_predictors_count += 1
            # if new_predictors_count == max_new_predictors_count:
            #     break

            storithm_type = self._storithm_type_to_create()
        self._timer.stop()

    def _add_predictor_to_storithm(self, occurrence):
        # bug: it should be horizon of external tours, now it's internal
        margin_cell = len(self._interpretation) - self._horizon - 1
        distance = margin_cell - occurrence.end

        predictor = Predictor()
        predictor.storithm = occurrence.storithm
        predictor.distance = distance
        occurrence.storithm.predictors[distance] = predictor

    def _max_new_predictors_count(self, return_):
        importance = self._importance_for_return(return_)
        lowest_element = self._predictors.lowest_element()
        if not lowest_element or importance <= lowest_element.importance():
            return self._predictors.limit - len(self._predictors)
        return None

    def _add_storithm(self, storithm):
        storithm.generate_id()
        self._storithms[storithm] = storithm
        if isinstance(storithm, Atom):
            self._atoms[storithm] = storithm

    def _storithm_type_to_create(self, first_in_tour=False):
        if first_in_tour:
            self._create_storithm_types_left = deepcopy(
                self.create_storithm_types
            )
            self._create_storithm_types_left.reverse()

        if not self._create_storithm_types_left[-1]:
            self._create_storithm_types_left.pop()

        if not self._create_storithm_types_left:
            return None

        last_element_keys = self._create_storithm_types_left[-1].keys()
        storithm_type = choice(list(last_element_keys))
        self._create_storithm_types_left[-1][storithm_type] -= 1
        if self._create_storithm_types_left[-1][storithm_type] == 0:
            self._create_storithm_types_left[-1].pop(storithm_type)
        return storithm_type

    def _sample_position(self):
        distance = self._horizon + choice([0])  # hardcoded
        position = len(self._interpretation) - distance - 1
        while position < 0:
            distance = self._horizon + choice([0])
            position = len(self._interpretation) - distance - 1
        return position

    def _importance_for_return(self, return_):  # wrong!
        predictor = Predictor()
        Estimator.fit([predictor], return_, self._sample_weight, False)
        return predictor.importance()

    def _fit(self):
        if self._current_external_tour <= self._horizon + 1:
            return None
        self._timer.start("fit")
        start = self._external_actions_positions[-self._horizon - 2] + 1
        end = self._external_actions_positions[-self._horizon - 1]
        return_ = self._returns[-1]
        for tour in range(start, end + 1):
            predictors = self._interpretation.predictors_in(tour)
            Estimator.fit(predictors, return_, self._sample_weight)
            self._update(predictors)
        self._timer.stop()

    def _update(self, predictors):
        for predictor in predictors:
            removed_predictor = None
            if predictor in self._predictors:
                self._predictors.update(predictor)
            else:
                removed_predictor = self._predictors.add(predictor)
            if removed_predictor:
                storithm = removed_predictor.storithm
                storithm.predictors.pop(removed_predictor.distance, None)
                if not storithm.predictors and not storithm.parent_pointers:
                    self._remove_storithm(storithm)

    def _remove_storithm(self, storithm):
        if storithm in self._storithms:
            self._storithms.pop(storithm)
            storithm.disconnect_with_children()
            if isinstance(storithm, Atom):
                self._atoms.pop(storithm)

    def _merge(self):
        pass

    def _prepare_after_learn(self, observation):
        self._timer.start("prepare_after_learn")
        self._memory.external_observation = observation
        self._sample_weight *= self.time_importance_factor
        self._timer.stop()

    def _prepare_before_act_internally(self):
        self._timer.start("_prepare_before_act_internally")
        internal_observation = self._memory.internal_observation()
        self._interpretation.internal_trajectory.observations.append(
            internal_observation
        )
        self._interpretation.extend()  # this should be done by itself
        for atom in self._atoms:
            if isinstance(atom, StateAtom):
                if internal_observation[atom.tape_id] == atom.value:
                    self._interpretation.add_at_the_end(atom)
        self._timer.stop()

    def _act_internally(self):
        self._timer.start("predict")
        action_values = self._predict()
        self._timer.stop()
        self._timer.start("choose")
        action = self._choose(action_values)
        self._timer.stop()
        self._timer.start("action_execute")
        action.execute(None if action.external else self._memory)
        self._timer.stop()
        return action

    def _predict(self):
        actions = self._internal_actions + self._external_actions
        action_values = {}
        for action in actions:
            if ActionAtom(action) in self._atoms:
                action_atom = self._atoms[ActionAtom(action)]
                self._interpretation.add_at_the_end_temporarily(action_atom)
            self._interpretation.interpret_temporarily()
            self._interpretation_cache[action] = self._interpretation.\
                temporary_occurrences
            predictors = self._interpretation.predictors_at_the_end()
            action_values[action] = Estimator.predict(predictors)
            self._interpretation.clear_temporary()
        return action_values

    def _choose(self, action_values):
        actions = list(action_values.keys())
        values = list(action_values.values())
        probabilities = self._softmax(values)
        action = actions[choice(range(len(action_values)), p=probabilities)]
        return action

    def _softmax(self, logits):
        logits = [logit * self._softmax_temperature for logit in logits]
        max_ = max(logits)
        exponentials = [exp(logit - max_) for logit in logits]
        exponentials_sum = sum(exponentials)
        return [exponential / exponentials_sum for exponential in exponentials]

    def _prepare_after_act_internally(self, action):
        self._timer.start("prepare_after_act_internally")
        self._interpretation.internal_trajectory.actions.append(action)
        self._interpretation.add(self._interpretation_cache[action])

        if action.external:
            self._external_actions_positions.append(
                self._current_internal_tour
            )
            self._current_external_tour += 1
        self._current_internal_tour += 1
        self._timer.stop()

    @staticmethod
    def _load_observation_actions():
        return [
            Action("load_observation", Memory.load_observation, False),
        ]

    @staticmethod
    def _set_value_actions(memory_tapes_count):
        actions = []
        for i in range(2):
            action = Action(
                "set_value_observation_" + str(i),
                partial(Memory.set_value_observation, value=i),
                False
            )
            actions.append(action)
            for j in range(memory_tapes_count):
                action = Action(
                    "set_value_memory_" + str(i) + "_" + str(j),
                    partial(Memory.set_value_memory, value=i, tape_id=j),
                    False
                )
                actions.append(action)
        return actions

    @staticmethod
    def _move_pointer_actions(
        observation_dimensionality,
        memory_tapes_count
    ):
        actions = []
        for i in range(observation_dimensionality):
            increment_action = Action(
                "increment_pointer_observation_" + str(i),
                partial(Memory.increment_observation_pointer, axis=i),
                False
            )
            decrement_action = Action(
                "decrement_pointer_observation_" + str(i),
                partial(Memory.decrement_observation_pointer, axis=i),
                False
            )
            actions += [increment_action, decrement_action]
        for i in range(memory_tapes_count):
            increment_action = Action(
                "increment_pointer_memory_" + str(i),
                partial(Memory.increment_memory_pointer, tape_id=i),
                False
            )
            decrement_action = Action(
                "decrement_pointer_memory_" + str(i),
                partial(Memory.decrement_memory_pointer, tape_id=i),
                False
            )
            actions += [increment_action, decrement_action]
        return actions

    @staticmethod
    def _go_to_starting_point_actions(
        observation_dimensionality,
        starting_points=None
    ):
        actions = []
        starting_points = (
            starting_points or
            RLAgent._default_starting_points(observation_dimensionality)
        )
        for key, point in enumerate(starting_points):
            action = Action(
                "go_to_starting_point_" + str(key),
                partial(Memory.go_to_point, point=point),
                False
            )
            actions.append(action)
        return actions

    @staticmethod
    def _default_starting_points(observation_dimensionality):
        return [tuple([0 for _ in range(observation_dimensionality)])]

    @staticmethod
    def _convert_to_actions_dict(actions_list):
        return {action.id: action for action in actions_list}

    def _prepare_create_storithm_types(self, create_storithm_types):
        default_create_storithm_types = [
            {StateAtom: 30, ActionAtom: 3},
            {Procedure: 200}
        ]
        return create_storithm_types or default_create_storithm_types

    def _prepare_internal_actions(
            self, internal_actions,
            observation_shape,
            starting_points
    ):
        """Prepare internal actions.

        If internal actions are none, then take the standard internal
        actions. If the value is a dict, convert it to a list.
        """
        if internal_actions is None:
            internal_actions = RLAgent.default_internal_actions(
                len(observation_shape),
                2,
                starting_points
            )
        if isinstance(internal_actions, dict):
            internal_actions = list(internal_actions.values())
        return internal_actions


class Action:
    def __init__(self, id_=None, execution=None, external=True):
        self.id = AutoIncrementId.generate(id_)
        self.execution = execution
        self.external = external

    def execute(self, memory=None):
        if not self.execution:
            return None
        if self.external:  # better check if 'memory' parameter exists
            self.execution()
        else:
            self.execution(memory)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return str(self)
