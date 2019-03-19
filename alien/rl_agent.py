from trajectory import Interpretation
from helpers import SortedLimitedList, AutoIncrementId
from memory import Memory
from storithm import Procedure, ActionAtom, StateAtom
from prediction import BasePredictor, Prediction, Predictor
from functools import partial
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
        new_procedures_count=5000,
        new_loops_count=5000,
        max_storithms_count=5000,
        max_predictors_count=5000,
        memory_tapes_count=2,
        memory_tapes_length=5000,
        internal_actions=None,
        starting_points=None,
    ):
        self._observation_shape = observation_shape
        self._external_actions = external_actions
        self.target_return = target_return
        self.antitarget_return = antitarget_return
        self._return_discount_factor = return_discount_factor
        self._horizon = horizon
        self.impact_discount_factor = impact_discount_factor
        self.time_importance_factor = time_importance_factor
        self.new_procedures_count = new_procedures_count
        self.new_loops_count = new_loops_count
        self.max_predictors_count = max_predictors_count
        self._internal_actions = self._prepare_internal_actions(
            internal_actions,
            observation_shape,
            starting_points
        )
        self._interpretation = Interpretation()
        self._sorted_storithms = SortedLimitedList(
            max_storithms_count,
            lambda a, b: a.importance() > b.importance()
        )  # this is not used
        self._sorted_predictors = SortedLimitedList(
            max_predictors_count,
            RLAgent._compare_predictors
        )
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
        self._sample_weight = 1
        self._interpretation_cache = {}
        self._external_actions_positions = []

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
        self._rewards.append(reward)

        previous_return = self._returns[-1]
        reward_before_horizon = (
            self._rewards[-self._horizon - 2]
            if self._current_external_tour > self._horizon
            else 0
        )
        return_ = previous_return + reward - reward_before_horizon
        self._returns.append(return_)

    def _learn(self):
        self._create()
        self._fit()
        self._merge()

    def _create(self):
        if self._current_external_tour <= self._horizon:
            return None

        return_ = self._returns[-1]
        max_new_predictors_count = self._max_new_predictors_count(return_)
        new_predictors_count = 0
        for i in range(self.new_procedures_count):
            occurrence = Procedure.propose_new(
                self._interpretation,
                self._horizon,
                self.impact_discount_factor
            )
            if not occurrence:
                continue

            # margin_cell = len(self._interpretation) - self._horizon - 1
            # distance = margin_cell - occurrence.end
            # occurrence.storithm.predictors[distance] = Predictor()

            if occurrence.storithm in self._storithms:
                self._storithms[occurrence.storithm].merge(occurrence.storithm)
                occurrence.storithm = self._storithms[occurrence.storithm]
            else:
                occurrence.storithm.generate_id()
                self._storithms[occurrence.storithm] = occurrence.storithm
            self._storithms[occurrence.storithm].connect_with_children()

            self._interpretation.add(occurrence)

            new_predictors_count += 1
            if new_predictors_count >= max_new_predictors_count:
                break

    def _max_new_predictors_count(self, return_):
        importance = self._importance_for_reward(return_)
        limit = self._sorted_predictors.limit
        position = self._sorted_predictors.position(importance)
        return limit - position

    # def _proposed_predictor(self, proposal):
    #     predictors = proposal.storithm.predictors
    #     for key in predictors:
    #         return key, predictors[key]

    def _importance_for_reward(self, reward):
        predictor = Predictor()
        prediction = Prediction()
        prediction.predictors = [predictor]
        prediction.fit(reward, self._sample_weight)
        return predictor.importance()

    def _fit(self):
        if self._current_external_tour <= self._horizon:
            return None
        start = self._external_actions_positions[-self._horizon - 2]
        end = self._external_actions_positions[-self._horizon - 1] - 1
        return_ = sum(self._rewards[-self._horizon - 1:])
        for tour in range(start, end):
            prediction = Prediction()
            prediction.predictors = self._interpretation.predictors_in_cells[
                tour
            ]
            prediction.fit(return_, self._sample_weight)
            self._update_positions(prediction.predictors)

    def _update_positions(self, predictors):
        for predictor in predictors:
            position = self._sorted_predictors.update_position(predictor)
            if position is None:
                predictor.storithm.predictors.pop(predictor.distance, None)
                if not predictor.storithm.predictors:
                    self._storithms.pop(predictor.storithm)
                    predictor.storithm.disconnect_with_children()

        # prediction_occurrences = self._prediction_occurrences[
        #     self._current_tour - self._horizon
        # ]
        # for prediction_occurrence in prediction_occurrences:
        #     storithm = prediction_occurrence.storithm_occurrence.storithm
        #     storithm.update_predictions_importance()
        #     predictor = prediction_occurrence.predictor
        #     self._sorted_predictors.update_position(predictor)

    def _merge(self):
        pass

    def _prepare_after_learn(self, observation):
        self._memory.external_observation = observation
        self._sample_weight *= self.time_importance_factor

    def _prepare_before_act_internally(self):
        self._interpretation.extend()
        internal_observation = self._memory.internal_observation().tolist()
        for state_id, value in enumerate(internal_observation):
            self._interpretation.add_at_the_end(StateAtom(state_id, value))

    def _act_internally(self):
        action_values = self._predict()
        action = self._choose(action_values)
        action.execute(None if action.external else self._memory)
        return action

    def _predict(self):
        actions = self._internal_actions + self._external_actions
        action_values = {}
        for action in actions:
            simulation = deepcopy(self._interpretation)
            simulation.add_at_the_end(ActionAtom(action))
            simulation.interpret()
            self._interpretation_cache[action] = simulation
            prediction = Prediction()
            prediction.predictors = simulation.predictors_at_the_end()
            action_values[action] = prediction.predict()
        return action_values

    def _choose(self, action_values):
        return Action()

    def _prepare_after_act_internally(self, action):
        self._interpretation = self._interpretation_cache[action]
        self._interpretation_cache = {}
        if action.external:
            self._external_actions_positions.append(
                self._current_internal_tour
            )
            self._current_external_tour += 1
        self._current_internal_tour += 1

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

    def _prepare_internal_actions(
            self, internal_actions,
            observation_shape,
            starting_points
    ):
        """Prepare internal actions.

        If internal actions are none, then take the standard internal
        actions. If the value is a dict, convert it to a list.
        """
        if not internal_actions:
            internal_actions = RLAgent.default_internal_actions(
                len(observation_shape),
                2,
                starting_points
            )
        if isinstance(internal_actions, dict):
            internal_actions = list(internal_actions.values())
        return internal_actions

    @staticmethod
    def _compare_predictors(a, b):
        if isinstance(a, BasePredictor):
            a = a.importance()
        if isinstance(b, BasePredictor):
            b = b.importance()
        return a > b


class Action:
    def __init__(self, id_=None, execution=None, external=True):
        self.id = AutoIncrementId.generate(id_)
        self.execution = execution
        self.external = external

    def execute(self, memory=None):
        if self.external:  # better check if 'memory' parameter exists
            self.execution()
        else:
            self.execution(memory)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(str(self))
