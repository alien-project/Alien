from storithm import *
from trajectory import Interpretation, StorithmOccurrence
from prediction import Predictor
from rl_agent import Action
from helpers import same
from random import seed


def test_procedure_propose_new():
    trial_count = 5000
    seed(500)

    interpretation = Interpretation()
    atoms = [
        StateAtom(1, 1),
        StateAtom(0, 1),
        ActionAtom(Action()),
        StateAtom(0, 0),
        StateAtom(0, 0)
    ]
    procedure = Procedure([atoms[1], atoms[2]])
    procedure_occurrence = StorithmOccurrence(procedure, 1, 2)
    for atom in atoms:
        interpretation.extend(atom)
    interpretation.add(procedure_occurrence)

    expected_found_by = [atoms[0], procedure]
    expected_children = [[atoms[0], procedure]]
    expected_storithm = Procedure(expected_children, {1: Predictor()})
    expected_proposal = StorithmOccurrence(
        expected_storithm,
        0,
        2,
        expected_found_by
    )
    proposed = False
    for i in range(trial_count):
        proposal = Procedure.propose_new(interpretation, 1, 3)
        if same(proposal, expected_proposal):  # predictors ids are different
            proposed = True
            break
    assert proposed


# def test_storithm_connect_with_children():
#     atoms = [StateAtom(1, 1), StateAtom(0, 1)]
#     procedure = Procedure([atoms[0], atoms[1]])
#     procedure.connect_with_children()
#
#     assert storithm_has_parent(atoms[0], procedure)
#     assert storithm_has_parent(atoms[1], procedure)
#
#
# def storithm_has_parent(storithm, parent):
#     for pointer in storithm.parent_pointers:
#         if pointer.parent == parent:
#             return True
#     return False


# def test_procedure_check_occurrence():
#     interpretation = Interpretation()
#     atoms = [
#         StateAtom(1, 1),
#         StateAtom(0, 1),
#         ActionAtom(Action()),
#         StateAtom(0, 0)
#     ]
#     for atom in atoms:
#         interpretation.extend(atom)
#     procedure = Procedure([atoms[1], atoms[2]])
#     procedure.connect_with_children()
#     child_occurrence = StorithmOccurrence(atoms[2], 2, 2)
#
#     expected_occurrence = StorithmOccurrence(procedure, 1, 2)
#     occurrence = procedure.check_occurrence(
#         interpretation,
#         child_occurrence,
#         1
#     )
#     assert expected_occurrence == occurrence


def test_procedure_str():
    procedure = Procedure([[StateAtom(1, 1), ActionAtom(Action(0))]])
    assert "s_1_1 a_0" == str(procedure)


def test_procedure_merge():
    atoms = [StateAtom(1, 1), StateAtom(0, 1), ActionAtom(Action(0))]

    procedure1 = Procedure([atoms[0:2]], {2: Predictor(), 3: Predictor()})
    proposed_storithm = Procedure([atoms[0:2]], {2: Predictor()})
    procedure1.merge(proposed_storithm)
    assert [atoms[0:2]] == procedure1.children
    assert same({2: Predictor(), 3: Predictor()}, procedure1.predictors)

    proposed_storithm = Procedure([atoms[0:2]], {4: Predictor()})
    procedure1.merge(proposed_storithm)
    assert [atoms[0:2]] == procedure1.children
    expected_predictors = {2: Predictor(), 3: Predictor(), 4: Predictor()}
    assert same(expected_predictors, procedure1.predictors)

    procedure2 = Procedure([[procedure1, atoms[2]]], {2: Predictor()})
    procedure3 = Procedure([[atoms[1:3]]])
    proposed_storithm = Procedure([[atoms[0], procedure3]], {3: Predictor()})
    procedure2.merge(proposed_storithm)
    expected_children = [[procedure1, atoms[2]], [atoms[0], procedure3]]
    assert expected_children == procedure2.children
    assert same({2: Predictor(), 3: Predictor()}, procedure2.predictors)


def test_procedure_connect_with_children_disconnect_with_children():
    atoms = [StateAtom(1, 1), StateAtom(0, 1), ActionAtom(Action(0))]
    procedure1 = Procedure([atoms[0:2]])
    procedure1.connect_with_children()
    assert [ParentPointer(procedure1, (0, 0))] == atoms[0].parent_pointers
    assert [ParentPointer(procedure1, (0, 1))] == atoms[1].parent_pointers

    procedure2 = Procedure([[procedure1, atoms[2]]])
    procedure2.connect_with_children()
    assert [ParentPointer(procedure2, (0, 0))] == procedure1.parent_pointers
    assert [ParentPointer(procedure2, (0, 1))] == atoms[2].parent_pointers

    proposed_storithm = Procedure([[procedure1, atoms[2]]])
    procedure2.merge(proposed_storithm)
    procedure2.connect_with_children()
    assert [ParentPointer(procedure2, (0, 0))] == procedure1.parent_pointers
    assert [ParentPointer(procedure2, (0, 1))] == atoms[2].parent_pointers

    procedure3 = Procedure([atoms[1:3]])
    proposed_storithm = Procedure([[atoms[0], procedure3]])
    procedure2.merge(proposed_storithm)
    procedure2.connect_with_children()
    assert [ParentPointer(procedure2, (0, 0))] == procedure1.parent_pointers
    assert [ParentPointer(procedure2, (0, 1))] == atoms[2].parent_pointers
    expected_parent_pointers = [
        ParentPointer(procedure1, (0, 0)),
        ParentPointer(procedure2, (1, 0))
    ]
    assert expected_parent_pointers == atoms[0].parent_pointers
    assert [ParentPointer(procedure2, (1, 1))] == procedure3.parent_pointers

    procedure2.disconnect_with_children()
    assert [] == procedure1.parent_pointers
    assert [] == atoms[2].parent_pointers
    assert [ParentPointer(procedure1, (0, 0))] == atoms[0].parent_pointers
    assert [] == procedure3.parent_pointers
