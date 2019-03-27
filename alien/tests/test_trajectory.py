from trajectory import *
from storithm import StateAtom, ActionAtom, Procedure
from prediction import Predictor
from rl_agent import Action
from copy import deepcopy


def test_interpretation_extend():
    interpretation = Interpretation()
    atoms = [StateAtom(1, 1), StateAtom(0, 1), ActionAtom(Action())]
    for atom in atoms:
        interpretation.extend(atom)
    interpretation.extend()

    expected_occurrences = [
        StorithmOccurrence(atoms[0], 0, 0),
        StorithmOccurrence(atoms[1], 1, 1),
        StorithmOccurrence(atoms[2], 2, 2)
    ]
    assert expected_occurrences == interpretation.storithm_occurrences

    expected_starting_in_cells = [
        [expected_occurrences[0]],
        [expected_occurrences[1]],
        [expected_occurrences[2]],
        []
    ]
    assert (
        expected_starting_in_cells ==
        interpretation.storithm_occurrences_starting_in_cells
    )

    expected_ending_in_cells = expected_starting_in_cells
    assert (
        expected_ending_in_cells ==
        interpretation.storithm_occurrences_ending_in_cells
    )


def test_interpretation_add():
    interpretation = Interpretation()
    atoms = [StateAtom(1, 1), StateAtom(0, 1), ActionAtom(Action())]
    predictor = Predictor()
    procedure = Procedure([atoms[1], atoms[2]], {2: predictor})
    occurrence = StorithmOccurrence(procedure, 1, 2)
    for atom in atoms:
        interpretation.extend(atom)
    interpretation.add(occurrence)

    expected_occurrences = [
        StorithmOccurrence(atoms[0], 0, 0),
        StorithmOccurrence(atoms[1], 1, 1),
        StorithmOccurrence(atoms[2], 2, 2),
        occurrence
    ]
    assert expected_occurrences == interpretation.storithm_occurrences

    expected_starting_in_cells = [
        [expected_occurrences[0]],
        [expected_occurrences[1], occurrence],
        [expected_occurrences[2]]
    ]
    assert (
        expected_starting_in_cells ==
        interpretation.storithm_occurrences_starting_in_cells
    )

    expected_ending_in_cells = [
        [expected_occurrences[0]],
        [expected_occurrences[1]],
        [expected_occurrences[2], occurrence]
    ]
    assert (
        expected_ending_in_cells ==
        interpretation.storithm_occurrences_ending_in_cells
    )

    expected_predictors_in_cells = {4: [predictor]}
    assert expected_predictors_in_cells == interpretation.predictors_in_cells


def test_interpretation_deepcopy():
    interpretation = Interpretation()
    atoms = [StateAtom(1, 1), StateAtom(0, 1), ActionAtom(Action())]
    for atom in atoms:
        interpretation.extend(atom)
    copy = deepcopy(interpretation)

    occurrence = StorithmOccurrence(Procedure([atoms[1], atoms[2]]), 1, 2)
    copy.add(occurrence)
    assert 3 == len(interpretation.storithm_occurrences)


def test_interpretation_interpret():
    interpretation = Interpretation()
    atoms = [StateAtom(1, 1), StateAtom(0, 1), ActionAtom(Action())]
    for atom in atoms:
        interpretation.extend(atom)
    procedure = Procedure([[atoms[1], atoms[2]]])
    procedure.connect_with_children()
    interpretation.interpret()

    occurrence = StorithmOccurrence(Procedure([[atoms[1], atoms[2]]]), 1, 2)
    assert occurrence in interpretation.storithm_occurrences


def test_interpretation_find_storithm_occurrence_starting_in():
    interpretation = Interpretation()
    atoms = [StateAtom(1, 1), StateAtom(0, 1), ActionAtom(Action())]
    for atom in atoms:
        interpretation.extend(atom)
    procedure = Procedure([[atoms[1], atoms[2]]])
    procedure_occurrence = StorithmOccurrence(procedure, 1, 2)
    interpretation.add(procedure_occurrence)

    occurrence = interpretation.find_storithm_occurrence_starting_in(
        procedure,
        1
    )
    assert procedure_occurrence == occurrence


def test_interpretation_find_storithm_occurrence_ending_in():
    interpretation = Interpretation()
    atoms = [StateAtom(1, 1), StateAtom(0, 1), ActionAtom(Action())]
    for atom in atoms:
        interpretation.extend(atom)
    procedure = Procedure([[atoms[1], atoms[2]]])
    procedure_occurrence = StorithmOccurrence(procedure, 1, 2)
    interpretation.add(procedure_occurrence)

    occurrence = interpretation.find_storithm_occurrence_ending_in(
        procedure,
        2
    )
    assert procedure_occurrence == occurrence
