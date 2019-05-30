from alien.storithm import *
from alien.trajectory import Interpretation, StorithmOccurrence
from alien.prediction import Predictor
from alien.rl_agent import Action
from alien.helpers import same
from random import seed, choice


type_groups = (
    (StateAtom,),
    (Condition,),
    (ActionAtom, Loop, Procedure),
    (ActionAtom, ConditionalStatement, Loop, Procedure)
)


def test_state_atom_create():
    trial_count = 5000
    seed(500)

    interpretation = Interpretation(type_groups)
    interpretation.internal_trajectory.observations = [[0, 1], [1, 1]]
    interpretation.internal_trajectory.actions = [Action(0)]

    expected_proposal = StorithmOccurrence(StateAtom(0, 1), 1, 1)
    proposed = False
    for i in range(trial_count):
        proposal = StateAtom.create(interpretation, lambda: choice([0, 1]))
        if same(proposal, expected_proposal):
            proposed = True
            break
    assert proposed


def test_procedure_create():
    trial_count = 500
    seed(500)

    interpretation = Interpretation(type_groups)
    atoms = [
        ActionAtom(Action(0)),
        ActionAtom(Action(1)),
        ActionAtom(Action(2)),
        StateAtom(0, 0),
        StateAtom(0, 0)
    ]
    procedure = Procedure([[atoms[1], atoms[2]]])
    procedure_occurrence = StorithmOccurrence(procedure, 1, 2)
    for atom in atoms:
        interpretation.extend(atom)
    interpretation.add(procedure_occurrence)

    expected_children = [[atoms[0], procedure]]
    expected_storithm = Procedure(expected_children)
    expected_proposal = StorithmOccurrence(
        expected_storithm,
        0,
        2
    )
    proposed = False
    for i in range(trial_count):
        proposal = Procedure.create(interpretation, lambda: 1)
        if same(proposal, expected_proposal):
            proposed = True
            break
    assert proposed


def test_procedure_check_occurrence():
    interpretation = Interpretation(type_groups)
    atoms = [
        StateAtom(1, 1),
        StateAtom(0, 1),
        ActionAtom(Action()),
        StateAtom(0, 0)
    ]
    for atom in atoms:
        interpretation.extend(atom)
    procedure = Procedure([[atoms[1], atoms[2]]])
    procedure.connect_with_children()
    child_occurrence = StorithmOccurrence(atoms[2], 2, 2)

    expected_occurrence = StorithmOccurrence(procedure, 1, 2)
    occurrence = procedure.check_occurrence(
        interpretation,
        child_occurrence,
        (0, 1)
    )
    assert expected_occurrence == occurrence


def test_procedure_str():
    procedure = Procedure([[StateAtom(1, 1), ActionAtom(Action(0))]])
    assert "s_1_1 a_0" == str(procedure)


def test_procedure_merge():
    atoms = [StateAtom(1, 1), StateAtom(0, 1), ActionAtom(Action(0))]

    procedure1 = Procedure([atoms[0:2]], {2: Predictor(), 3: Predictor()})
    proposed_storithm = Procedure([atoms[0:2]], {2: Predictor()})
    procedure1.merge(proposed_storithm)
    assert [atoms[0:2]] == procedure1.children
    expected_predictors = {
        2: Predictor(storithm=procedure1, distance=2),
        3: Predictor(storithm=procedure1, distance=3)
    }
    assert same(expected_predictors, procedure1.predictors)

    proposed_storithm = Procedure([atoms[0:2]], {4: Predictor()})
    procedure1.merge(proposed_storithm)
    assert [atoms[0:2]] == procedure1.children
    expected_predictors = {
        2: Predictor(storithm=procedure1, distance=2),
        3: Predictor(storithm=procedure1, distance=3),
        4: Predictor(storithm=procedure1, distance=4)
    }
    assert same(expected_predictors, procedure1.predictors)

    procedure2 = Procedure([[procedure1, atoms[2]]], {2: Predictor()})
    procedure3 = Procedure([[atoms[1:3]]])
    proposed_storithm = Procedure([[atoms[0], procedure3]], {3: Predictor()})
    procedure2.merge(proposed_storithm)
    expected_children = [[procedure1, atoms[2]], [atoms[0], procedure3]]
    assert expected_children == procedure2.children
    expected_predictors = {
        2: Predictor(storithm=procedure2, distance=2),
        3: Predictor(storithm=procedure2, distance=3)
    }
    assert same(expected_predictors, procedure2.predictors)


def test_procedure_connect_with_children_disconnect_with_children():
    atoms = [StateAtom(1, 1), StateAtom(0, 1), ActionAtom(Action(0))]
    procedure1 = Procedure([atoms[0:2]])
    procedure1.connect_with_children()
    assert {ParentPointer(procedure1, (0, 0))} == atoms[0].parent_pointers
    assert {ParentPointer(procedure1, (0, 1))} == atoms[1].parent_pointers

    procedure2 = Procedure([[procedure1, atoms[2]]])
    procedure2.connect_with_children()
    assert {ParentPointer(procedure2, (0, 0))} == procedure1.parent_pointers
    assert {ParentPointer(procedure2, (0, 1))} == atoms[2].parent_pointers

    proposed_storithm = Procedure([[procedure1, atoms[2]]])
    procedure2.merge(proposed_storithm)
    procedure2.connect_with_children()
    assert {ParentPointer(procedure2, (0, 0))} == procedure1.parent_pointers
    assert {ParentPointer(procedure2, (0, 1))} == atoms[2].parent_pointers

    procedure3 = Procedure([atoms[1:3]])
    proposed_storithm = Procedure([[atoms[0], procedure3]])
    procedure2.merge(proposed_storithm)
    procedure2.connect_with_children()
    assert {ParentPointer(procedure2, (0, 0))} == procedure1.parent_pointers
    assert {ParentPointer(procedure2, (0, 1))} == atoms[2].parent_pointers
    expected_parent_pointers = {
        ParentPointer(procedure1, (0, 0)),
        ParentPointer(procedure2, (1, 0))
    }
    assert expected_parent_pointers == atoms[0].parent_pointers
    assert {ParentPointer(procedure2, (1, 1))} == procedure3.parent_pointers

    procedure2.disconnect_with_children()
    assert set() == procedure1.parent_pointers
    assert set() == atoms[2].parent_pointers
    assert {ParentPointer(procedure1, (0, 0))} == atoms[0].parent_pointers
    assert set() == procedure3.parent_pointers


def test_condition_create():
    trial_count = 500
    seed(500)

    interpretation = Interpretation(type_groups)
    atoms = [
        StateAtom(1, 1),
        StateAtom(0, 1),
        StateAtom(0, 0)
    ]
    interpretation.extend()
    for atom in atoms:
        interpretation.add_at_the_end(atom)

    expected_proposal = StorithmOccurrence(Condition(atoms[1:3]), 0, 0)

    proposed = False
    for i in range(trial_count):
        proposal = Condition.create(interpretation, lambda: 0)
        if same(proposal, expected_proposal):
            proposed = True
            break
    assert proposed


def test_condition_check_occurrence():
    interpretation = Interpretation(type_groups)
    atoms = [
        StateAtom(1, 1),
        StateAtom(0, 1),
        StateAtom(0, 0)
    ]
    interpretation.extend()
    for atom in atoms[0:2]:
        interpretation.add_at_the_end(atom)
    condition = Condition(atoms[1:3])
    condition.connect_with_children()
    child_occurrence = StorithmOccurrence(atoms[1], 0, 0)

    occurrence = condition.check_occurrence(
        interpretation,
        child_occurrence,
        (0, 1)
    )
    assert occurrence is None

    interpretation.add_at_the_end(atoms[2])
    occurrence = condition.check_occurrence(
        interpretation,
        child_occurrence,
        (0, 1)
    )
    expected_occurrence = StorithmOccurrence(condition, 0, 0)
    assert expected_occurrence == occurrence


def test_conditional_statement_create():
    trial_count = 5000
    seed(500)

    interpretation = Interpretation(type_groups)
    atoms = [
        StateAtom(1, 1),
        ActionAtom(Action(0))
    ]
    interpretation.extend()
    for atom in atoms:
        interpretation.add_at_the_end(atom)
    condition = Condition([atoms[0]])
    interpretation.add_at_the_end(condition)

    conditional_statement = ConditionalStatement(condition, atoms[1])
    expected_proposal = StorithmOccurrence(conditional_statement, 0, 0)

    proposed = False
    for i in range(trial_count):
        proposal = ConditionalStatement.create(interpretation, lambda: 0)
        if same(proposal, expected_proposal):
            proposed = True
            break
    assert proposed


def test_conditional_statement_check_occurrence():
    interpretation = Interpretation(type_groups)
    atoms = [
        StateAtom(1, 1),
        ActionAtom(Action(0))
    ]
    interpretation.extend()
    for atom in atoms:
        interpretation.add_at_the_end(atom)
    condition = Condition([atoms[0]])
    interpretation.add_at_the_end(condition)

    conditional_statement = ConditionalStatement(condition, atoms[1])
    conditional_statement.connect_with_children()

    occurrence = conditional_statement.check_occurrence(
        interpretation,
        StorithmOccurrence(condition, 0, 0),
        ConditionalStatement.POSITION_CONDITION
    )
    expected_occurrence = StorithmOccurrence(conditional_statement, 0, 0)
    assert expected_occurrence == occurrence


def test_loop_create():
    trial_count = 5000
    seed(500)

    atoms = [
        StateAtom(1, 1),
        ActionAtom(Action(0))
    ]
    condition = Condition([atoms[0]])
    interpretation = Interpretation(type_groups)
    for _ in range(5):
        interpretation.extend()
        interpretation.add_at_the_end(atoms[0])
        interpretation.add_at_the_end(atoms[1])
        interpretation.add_at_the_end(condition)

    loop = Loop(condition, atoms[1])
    expected_proposal = StorithmOccurrence(loop, 0, 4)
    proposed = False
    for i in range(trial_count):
        proposal = Loop.create(interpretation, lambda: 1)
        if same(proposal, expected_proposal):
            proposed = True
            break
    assert proposed


def test_loop_check_occurrence():
    pass


def test_storithm_repository_add_remove_contains():
    repository = StorithmRepository()
    atom = ActionAtom(Action())
    repository.add(atom)
    assert atom in repository
    repository.remove(atom)
    assert atom not in repository
