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
        StateAtom(0, 1, 1),
        StateAtom(0, 0, 1),
        ActionAtom(0, Action()),
        StateAtom(0, 0, 0),
        StateAtom(0, 0, 0)
    ]
    procedure = Procedure([atoms[1], atoms[2]])
    procedure_occurrence = StorithmOccurrence(procedure, 1, 2)
    for atom in atoms:
        interpretation.extend(atom)
    interpretation.add(procedure_occurrence)

    expected_children = expected_found_by = [atoms[0], procedure]
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


def test_storithm_connect_with_children():
    atoms = [StateAtom(0, 1, 1), StateAtom(0, 0, 1)]
    procedure = Procedure([atoms[0], atoms[1]])
    procedure.connect_with_children()

    assert storithm_has_parent(atoms[0], procedure)
    assert storithm_has_parent(atoms[1], procedure)


def storithm_has_parent(storithm, parent):
    for pointer in storithm.parent_pointers:
        if pointer.parent == parent:
            return True
    return False


def test_procedure_check_occurrence():
    interpretation = Interpretation()
    atoms = [
        StateAtom(0, 1, 1),
        StateAtom(0, 0, 1),
        ActionAtom(0, Action()),
        StateAtom(0, 0, 0)
    ]
    for atom in atoms:
        interpretation.extend(atom)
    procedure = Procedure([atoms[1], atoms[2]])
    procedure.connect_with_children()
    child_occurrence = StorithmOccurrence(atoms[2], 2, 2)

    expected_occurrence = StorithmOccurrence(procedure, 1, 2)
    occurrence = procedure.check_occurrence(
        interpretation,
        child_occurrence,
        1
    )
    assert expected_occurrence == occurrence
