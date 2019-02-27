class Storithm:
    def __init__(self):
        self.parent_pointers = []
        self.parents_sampling_base = []
        self.predictors = []
        self.importance = 0


class ParentPointer:
    def __init__(self, parent, position):
        self.parent = parent
        self.position = position


class Procedure(Storithm):
    def __init__(self, children):
        self.children = children
        super().__init__()


class Loop(Storithm):
    def __init__(self, condition_child, body_child):
        self.condition_child = condition_child
        self.body_child = body_child
        super().__init__()


class Fusion(Storithm):
    def __init__(self, children):
        self.children = children
        super().__init__()
