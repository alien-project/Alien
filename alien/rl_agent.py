from spacetime import Spacetime, SpacetimeInterpretation
from data_structures import SortedLimitedList
from memory import Memory
from functools import partial


class RLAgent:
    def __init__(
        self,
        observation_shape,
        external_actions,
        target_return=0,
        antitarget_return=0,
        return_discount_factor=0.5,  # if changes, re-calc importance
        return_time=1,  # if changes, re-calc importance
        impact_discount_factor=0.5,
        new_procedures_count=5000,
        new_loops_count=5000,
        max_storithms_count=5000,
        max_predictors_count=5000,
        memory_tapes_count=2,
        memory_tapes_length=5000,
        internal_actions=None,
        starting_points=None
    ):
        self.observation_shape = observation_shape
        self.external_actions = external_actions
        self.target_return = target_return
        self.antitarget_return = antitarget_return
        self.return_discount_factor = return_discount_factor
        self.return_time = return_time
        self.impact_discount_factor = impact_discount_factor
        self.new_procedures_count = new_procedures_count
        self.new_loops_count = new_loops_count
        self.max_predictors_count = max_predictors_count
        self._internal_actions = self._prepare_internal_actions(
            internal_actions,
            observation_shape,
            starting_points
        )
        self._spacetime = Spacetime()
        self._interpretation = SpacetimeInterpretation()
        self._sorted_storithms = SortedLimitedList(max_storithms_count)
        self._sorted_predictors = SortedLimitedList(max_predictors_count)
        self._rewards = []
        self._current_moment = 0
        self._importance_for_distance_cache = []
        self.memory = Memory(  # better set memory as an optional parameter
            observation_shape,
            memory_tapes_length,
            memory_tapes_count
        )

    def act(self, observation, reward):
        self.memory.external_observation = observation
        action = self._act_internally(
            self.memory.internal_observation(),
            reward
        )
        while not action.external:
            self.memory.external_observation = observation
            action = self._act_internally(
                self.memory.internal_observation(),
                None
            )
        return action

    @staticmethod
    def default_internal_actions(
            observation_dimensionality,
            memory_tapes_count=2,
            starting_points=None  # this should be on the second place
    ):
        actions = [
            Action("load_observation", Memory.load_observation, False),
        ]
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
        return RLAgent._convert_to_actions_dict(actions)

    def _act_internally(self, internal_observation, reward):
        self._prepare_beginning(internal_observation)
        self._observe(reward)
        action = self._react()
        self._prepare_end(action)
        return action

    def _prepare_beginning(self, internal_observation):
        self._spacetime.observations.append(internal_observation)

    def _prepare_end(self, action):
        self._spacetime.actions.append(action)

    def _observe(self, reward):
        self._create_new_storithms(reward)
        self._fit(reward)
        self._merge()
        self._flush()

    def _create_new_storithms(self, reward):
        max_accepted_distance = self._max_accepted_distance(reward)
        new_storithms, new_predictors = self._interpretation.\
            create_new_storithms(
                self.new_procedures_count,
                self.impact_discount_factor,
                max_accepted_distance
            )
        self._sorted_predictors += new_predictors
        self._sorted_storithms += new_storithms

    def _max_accepted_distance(self, reward):
        """Max accepted distance for adding new predictors."""
        for i in range(self.return_time):
            importance = reward * self._importance_for_distance(i)
            if importance <= self._min_accepted_importance():
                return i
        return self.return_time  # to do: growing sample importance

    def _importance_for_distance(self, distance):
        # _importance_for_distance_cache needs to be dict, not list
        if len(self._importance_for_distance_cache) < distance:
            return self._importance_for_distance_cache[distance]
        if distance > self.return_time:
            return 0
        expression_bottom = 0
        for i in range(self.return_time):
            expression_bottom += self.return_discount_factor ** i
        expression_top = expression_bottom
        for i in range(self.return_time + 1):
            self._importance_for_distance_cache[i] = (
                expression_top / expression_bottom
            )
            expression_top -= self.return_discount_factor ** i
        return self._importance_for_distance_cache[distance]

    def _min_accepted_importance(self):
        return self._sorted_predictors.last().importance

    def _fit(self, reward):
        pass

    def _merge(self):
        pass

    def _flush(self):
        pass

    def _predict(self):
        pass

    def _react(self):
        return Action()

    @staticmethod
    def _default_starting_points(observation_dimensionality):
        return [tuple([0 for _ in range(observation_dimensionality)])]

    @staticmethod
    def _convert_to_actions_dict(actions_list):
        dict_ = {}
        for action in actions_list:
            dict_[action.id] = action
        return dict_

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


class Action:
    next_id = 0

    def __init__(self, id_=None, execution=None, external=True):
        self.id = self._auto_increment_id(id_)
        self.execution = execution
        self.external = external

    def execute(self, memory=None):
        if self.external:  # better check if 'memory' parameter exists
            self.execution()
        else:
            self.execution(memory)

    def _auto_increment_id(self, id_):
        if id_ is None:
            Action.next_id += 1
            return Action.next_id - 1
        if isinstance(id_, int):
            if id_ >= Action.next_id:
                Action.next_id = id_ + 1
                return id_
        return id_

    def __eq__(self, other):
        return self.id == other.id
