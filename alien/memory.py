from numpy import array, concatenate, zeros


class Memory:
    def __init__(
        self,
        external_observation_shape,
        memory_tapes_length,
        memory_tapes_count=2
    ):
        self.external_observation_tape = Tape(
            external_observation_shape,
            tuple([0 for _ in range(len(external_observation_shape))])
        )
        self.memory_tapes = [
            Tape((memory_tapes_length,), 0) for _ in range(memory_tapes_count)
        ]
        self.external_observation = self.external_observation_tape.values

    def internal_observation(self):
        observation_part = array([
            self.external_observation_tape.get_indicated_value()
        ])
        memory_part = zeros((len(self.memory_tapes),))
        for i in range(len(self.memory_tapes)):
            memory_part[i] = self.memory_tapes[i].get_indicated_value()
        return concatenate((observation_part, memory_part))

    def load_observation(self):
        self.external_observation_tape.values = self.external_observation

    def set_value_observation(self, value):
        self.external_observation_tape.set_indicated_value(value)

    def set_value_memory(self, tape_id, value):
        self.memory_tapes[tape_id].set_indicated_value(value)

    def increment_observation_pointer(self, axis):
        self.external_observation_tape.increment_pointer(axis)

    def decrement_observation_pointer(self, axis):
        self.external_observation_tape.decrement_pointer(axis)

    def increment_memory_pointer(self, tape_id):
        self.memory_tapes[tape_id].increment_pointer()

    def decrement_memory_pointer(self, tape_id):
        self.memory_tapes[tape_id].decrement_pointer()

    def go_to_point(self, point):
        self.external_observation_tape.go_to_point(point)


class Tape:
    def __init__(self, shape, pointer):
        self.values = zeros(shape)
        self.pointer = pointer

    def set_indicated_value(self, value):
        self.values[self.pointer] = value

    def get_indicated_value(self):
        return self.values[self.pointer]

    def increment_pointer(self, axis=None):
        if isinstance(self.pointer, tuple):
            pointer_list = list(self.pointer)
            pointer_list[axis] += 1
            if pointer_list[axis] >= self.values.shape[axis]:
                pointer_list[axis] = 0
            self.pointer = tuple(pointer_list)
        else:
            self.pointer += 1
            if self.pointer >= self.values.shape[0]:
                self.pointer = 0

    def decrement_pointer(self, axis=None):
        if isinstance(self.pointer, tuple):
            pointer_list = list(self.pointer)
            pointer_list[axis] -= 1
            if pointer_list[axis] < 0:
                pointer_list[axis] = self.values.shape[axis] - 1
            self.pointer = tuple(pointer_list)
        else:
            self.pointer -= 1
            if self.pointer < 0:
                self.pointer = self.values.shape[0] - 1

    def go_to_point(self, point):
        self.pointer = point
