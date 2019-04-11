from trajectory import *
from storithm import StateAtom, ActionAtom, Procedure, Condition
from prediction import Predictor
from rl_agent import Action


def test_interpretation_extend():
    StateAtom(1, 0).__hash__()

    interpretation = Interpretation()
    atoms = [StateAtom(1, 1), StateAtom(0, 1), ActionAtom(Action())]
    for atom in atoms:
        interpretation.extend(atom)
    interpretation.extend()

    expected_starting_in_cells = [
        {StorithmOccurrence(atoms[0], 0, 0)},
        {StorithmOccurrence(atoms[1], 1, 1)},
        {StorithmOccurrence(atoms[2], 2, 2)},
        set()
    ]
    assert (
        expected_starting_in_cells ==
        interpretation.storithm_occurrences_starting
    )

    expected_ending_in_cells = expected_starting_in_cells
    assert (
        expected_ending_in_cells ==
        interpretation.storithm_occurrences_ending
    )


def test_interpretation_add():
    interpretation = Interpretation()
    atoms = [StateAtom(1, 1), StateAtom(0, 1), ActionAtom(Action())]
    predictor = Predictor()
    procedure = Procedure([[atoms[1], atoms[2]]], {2: predictor})
    occurrence = StorithmOccurrence(procedure, 1, 2)
    for atom in atoms:
        interpretation.extend(atom)
    interpretation.add(occurrence)

    expected_starting_in_cells_1 = [
        {StorithmOccurrence(atoms[0], 0, 0)},
        {
            StorithmOccurrence(atoms[1], 1, 1),
            StorithmOccurrence(procedure, 1, 2)
        },
        {StorithmOccurrence(atoms[2], 2, 2)}
    ]
    assert (
        expected_starting_in_cells_1 ==
        interpretation.storithm_occurrences_starting
    )

    expected_ending_in_cells_1 = [
        {StorithmOccurrence(atoms[0], 0, 0)},
        {StorithmOccurrence(atoms[1], 1, 1)},
        {
            StorithmOccurrence(atoms[2], 2, 2),
            StorithmOccurrence(procedure, 1, 2)
        }
    ]
    assert (
        expected_ending_in_cells_1 ==
        interpretation.storithm_occurrences_ending
    )

    assert {predictor} == interpretation.predictors_in(4)

    procedure2 = Procedure([[atoms[0], atoms[1]]], {1: predictor})
    occurrence = StorithmOccurrence(procedure2, 0, 1)
    interpretation.add(occurrence, True)

    expected_starting_in_cells_2 = [
        {
            StorithmOccurrence(atoms[0], 0, 0),
            StorithmOccurrence(procedure2, 0, 1)
        },
        {
            StorithmOccurrence(atoms[1], 1, 1),
            StorithmOccurrence(procedure, 1, 2)
        },
        {StorithmOccurrence(atoms[2], 2, 2)}
    ]
    assert (
        expected_starting_in_cells_2 ==
        interpretation.storithm_occurrences_starting
    )

    expected_ending_in_cells_2 = [
        {StorithmOccurrence(atoms[0], 0, 0)},
        {
            StorithmOccurrence(atoms[1], 1, 1),
            StorithmOccurrence(procedure2, 0, 1)
        },
        {
            StorithmOccurrence(atoms[2], 2, 2),
            StorithmOccurrence(procedure, 1, 2)
        }
    ]
    assert (
        expected_ending_in_cells_2 ==
        interpretation.storithm_occurrences_ending
    )

    expected_temporary_occurrences = [StorithmOccurrence(procedure2, 0, 1)]
    assert (
        expected_temporary_occurrences ==
        interpretation.temporary_occurrences
    )

    interpretation.clean_temporary()

    assert [] == interpretation.temporary_occurrences
    assert (
        expected_starting_in_cells_1 ==
        interpretation.storithm_occurrences_starting
    )
    assert (
        expected_ending_in_cells_1 ==
        interpretation.storithm_occurrences_ending
    )

    interpretation.add([occurrence])
    interpretation.clean_temporary()

    assert (
        expected_starting_in_cells_2 ==
        interpretation.storithm_occurrences_starting
    )
    assert (
        expected_ending_in_cells_2 ==
        interpretation.storithm_occurrences_ending
    )


def test_interpretation_interpret():
    interpretation = Interpretation()
    atoms = [StateAtom(1, 1), StateAtom(0, 1), ActionAtom(Action())]
    for atom in atoms:
        interpretation.extend(atom)
    procedure = Procedure([[atoms[1], atoms[2]]])
    procedure.connect_with_children()
    interpretation.interpret(True)

    occurrence = StorithmOccurrence(Procedure([[atoms[1], atoms[2]]]), 1, 2)
    starting_cell = interpretation.storithm_occurrences_starting[1]
    assert occurrence in starting_cell
    ending_cell = interpretation.storithm_occurrences_ending[2]
    assert occurrence in ending_cell

    interpretation.clean_temporary()
    assert occurrence not in starting_cell
    assert occurrence not in ending_cell

    interpretation.interpret()
    interpretation.clean_temporary()
    assert occurrence in starting_cell
    assert occurrence in ending_cell


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


def test_interpretation_sample_storithm_occurrences():
    interpretation = Interpretation()
    atoms = [StateAtom(1, 1), StateAtom(0, 1)]
    condition = Condition(atoms)
    interpretation.add(StorithmOccurrence(atoms[0], 0, 0))
    interpretation.add(StorithmOccurrence(atoms[1], 0, 0))
    interpretation.add(StorithmOccurrence(condition, 0, 0))

    occurrences = interpretation.sample_storithm_occurrences(
        2,
        (StateAtom,),
        0
    )
    assert set(atoms) == occurrences
