from rl_agent import *
from random import randint
from memory import Memory
from storithm import ActionAtom
from numpy import array, array_equal


def test_rl_agent_act1():
    learning_trials_count = 1000  # 1000000000
    testing_trials_count = 10

    create_storithm_types = [{ActionAtom: 2}]
    rl_agent = RLAgent(
        (1,),
        [Action(0), Action(1)],
        1,
        0,
        0.5,
        0,
        time_importance_factor=1,
        create_storithm_types=create_storithm_types
    )

    reward = 0
    for _ in range(learning_trials_count):
        observation = array([randint(0, 1)])
        action = rl_agent.act(observation, reward)
        reward = action.id
    for _ in range(testing_trials_count):
        observation = array([randint(0, 1)])
        action = rl_agent.act(observation, reward)
        reward = action.id
        assert 1 == reward


def test_rl_agent_act2():
    learning_trials_count = 1000000000
    testing_trials_count = 10

    rl_agent = RLAgent((1,), [Action(0), Action(1)], 1, 0, 0.5, 2)

    reward = 0
    for _ in range(learning_trials_count):
        observation = array([randint(0, 1)])
        action = rl_agent.act(observation, reward)
        reward = 1 if observation[0] == action.id else 0
    for _ in range(testing_trials_count):
        observation = array([randint(0, 1)])
        action = rl_agent.act(observation, reward)
        reward = 1 if observation[0] == action.id else 0
        assert 1 == reward


def test_rl_agent_default_internal_actions_load_observation():
    observation_shape = (2, 3)
    actions = RLAgent.default_internal_actions(len(observation_shape))
    memory = Memory(observation_shape, 5)

    external_observation = array([[1, 0, 1], [1, 0, 1]])
    memory.external_observation = external_observation
    actions['load_observation'].execute(memory)
    assert array_equal(
        external_observation,
        memory.external_observation_tape.values
    )


def test_rl_agent_default_internal_actions_set_value_observation():
    observation_shape = (2, 3)
    actions = RLAgent.default_internal_actions(len(observation_shape))
    memory = Memory(observation_shape, 5)

    memory.external_observation_tape.values = array([[1, 0, 1], [1, 0, 1]])
    memory.external_observation_tape.pointer = (1, 0)
    actions['set_value_observation_0'].execute(memory)
    # func = lambda memory_: Memory.set_value_observation(memory_, 0)
    # func(memory)
    assert 0 == memory.external_observation_tape.values[1][0]


def test_rl_agent_default_internal_actions_set_value_memory():
    observation_shape = (2, 3)
    actions = RLAgent.default_internal_actions(len(observation_shape))
    memory = Memory(observation_shape, 5)

    memory.memory_tapes[1].values = array([1, 0, 1, 0, 1])
    memory.memory_tapes[1].pointer = 3
    actions['set_value_memory_1_1'].execute(memory)
    assert 1 == memory.memory_tapes[1].values[3]


def test_rl_agent_default_internal_actions_increment_pointer_observation():
    observation_shape = (2, 3)
    actions = RLAgent.default_internal_actions(len(observation_shape))
    memory = Memory(observation_shape, 5)

    memory.external_observation_tape.pointer = (1, 1)
    actions['increment_pointer_observation_1'].execute(memory)
    assert (1, 2) == memory.external_observation_tape.pointer

    actions['increment_pointer_observation_1'].execute(memory)
    assert (1, 0) == memory.external_observation_tape.pointer


def test_rl_agent_default_internal_actions_decrement_pointer_observation():
    observation_shape = (2, 3)
    actions = RLAgent.default_internal_actions(len(observation_shape))
    memory = Memory(observation_shape, 5)

    memory.external_observation_tape.pointer = (1, 1)
    actions['decrement_pointer_observation_1'].execute(memory)
    assert (1, 0) == memory.external_observation_tape.pointer

    actions['decrement_pointer_observation_1'].execute(memory)
    assert (1, 2) == memory.external_observation_tape.pointer


def test_rl_agent_default_internal_actions_decrement_pointer_memory():
    observation_shape = (2, 3)
    actions = RLAgent.default_internal_actions(len(observation_shape))
    memory = Memory(observation_shape, 5)

    memory.memory_tapes[0].pointer = 1
    actions['decrement_pointer_memory_0'].execute(memory)
    assert 0 == memory.memory_tapes[0].pointer

    actions['decrement_pointer_memory_0'].execute(memory)
    assert 4 == memory.memory_tapes[0].pointer


def test_rl_agent_default_internal_actions_increment_pointer_memory():
    observation_shape = (2, 3)
    actions = RLAgent.default_internal_actions(len(observation_shape))
    memory = Memory(observation_shape, 5)

    memory.memory_tapes[0].pointer = 3
    actions['increment_pointer_memory_0'].execute(memory)
    assert 4 == memory.memory_tapes[0].pointer

    actions['increment_pointer_memory_0'].execute(memory)
    assert 0 == memory.memory_tapes[0].pointer


def test_rl_agent_default_internal_actions_go_to_starting_point_default():
    observation_shape = (2, 3)
    actions = RLAgent.default_internal_actions(len(observation_shape))
    memory = Memory(observation_shape, 5)

    memory.external_observation_tape.pointer = (1, 1)
    actions['go_to_starting_point_0'].execute(memory)
    assert (0, 0) == memory.external_observation_tape.pointer


def test_rl_agent_default_internal_actions_go_to_starting_point_custom():
    observation_shape = (2, 3)
    actions = RLAgent.default_internal_actions(
        len(observation_shape),
        2,
        [(0, 0), (1, 1), (2, 2)]
    )
    memory = Memory(observation_shape, 5)

    memory.external_observation_tape.pointer = (1, 1)
    actions['go_to_starting_point_2'].execute(memory)
    assert (2, 2) == memory.external_observation_tape.pointer


def test_rl_agent_default_internal_actions_are_internal():
    actions = RLAgent.default_internal_actions(2)
    for _, action in actions.items():
        assert not action.external


def test_rl_agent_default_internal_actions_ids_are_same_as_keys():
    actions = RLAgent.default_internal_actions(2)
    for key, action in actions.items():
        assert key == action.id
