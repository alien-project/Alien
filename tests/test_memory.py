from alien.memory import *
from numpy import array, array_equal


def test_memory_internal_observation():
    memory = Memory((3, 4), 4)
    memory.external_observation_tape.values = array([
        [1, 0, 1, 0],
        [1, 0, 1, 0],
        [1, 0, 1, 0]
    ])
    memory.external_observation_tape.pointer = (1, 2)
    memory.memory_tapes[0].values = array([1, 0, 1, 0])
    memory.memory_tapes[0].pointer = 1
    memory.memory_tapes[1].values = array([1, 0, 1, 0])
    memory.memory_tapes[1].pointer = 3
    assert array_equal(array([1, 0, 0]), memory.internal_observation())


def test_tape_get_indicated_value():
    tape = Tape((3, 4), (1, 1))
    tape.values = array([
        [1, 0, 1, 0],
        [1, 5, 1, 0],
        [1, 0, 1, 0]
    ])
    assert 5 == tape.get_indicated_value()

    tape = Tape((3,), 1)
    tape.values = array([3, 2, 1])
    assert 2 == tape.get_indicated_value()


def test_tape_set_indicated_value():
    tape = Tape((3, 4), (1, 1))
    tape.values = array([
        [1, 0, 1, 0],
        [1, 5, 1, 0],
        [1, 0, 1, 0]
    ])
    tape.set_indicated_value(3)
    assert 3 == tape.values[1][1]

    tape = Tape((3,), 1)
    tape.values = array([3, 2, 1])
    tape.set_indicated_value(5)
    assert 5 == tape.values[1]


def test_tape_increment_pointer():
    tape = Tape((3, 4), (1, 2))
    tape.increment_pointer(1)
    assert (1, 3) == tape.pointer
    tape.increment_pointer(1)
    assert (1, 0) == tape.pointer

    tape = Tape((3,), 1)
    tape.increment_pointer()
    assert 2 == tape.pointer
    tape.increment_pointer()
    assert 0 == tape.pointer


def test_tape_decrement_pointer():
    tape = Tape((3, 4), (1, 1))
    tape.decrement_pointer(1)
    assert (1, 0) == tape.pointer
    tape.decrement_pointer(1)
    assert (1, 3) == tape.pointer

    tape = Tape((3,), 1)
    tape.decrement_pointer()
    assert 0 == tape.pointer
    tape.decrement_pointer()
    assert 2 == tape.pointer
