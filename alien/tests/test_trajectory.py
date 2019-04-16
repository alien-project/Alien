from trajectory import *
from storithm import StateAtom, ActionAtom, Procedure, Condition
from storithm import ConditionalStatement, Loop
from prediction import Predictor
from rl_agent import Action


def test_interpretation():
    interpretation = Interpretation(
        (
            (StateAtom,),
            (Condition,),
            (ActionAtom, ConditionalStatement, Loop, Procedure)
        )
    )
    atoms = [StateAtom(1, 1), StateAtom(0, 1), ActionAtom(Action())]
    predictor = Predictor()
    procedure = Procedure([[atoms[1], atoms[2]]], {2: predictor})
    occurrence = StorithmOccurrence(procedure, 1, 2)
    for atom in atoms:
        interpretation.extend(atom)
    interpretation.add(occurrence)

    assert occurrence == interpretation.find_storithm_occurrence_starting_in(
        procedure,
        1
    )
    assert occurrence == interpretation.find_storithm_occurrence_ending_in(
        procedure,
        2
    )
    assert {predictor} == interpretation.predictors_in(4)

    procedure2 = Procedure([[atoms[0], atoms[1]]], {1: predictor})
    occurrence = StorithmOccurrence(procedure2, 0, 1)
    interpretation.add(occurrence, True)

    result = interpretation.find_storithm_occurrence_starting_in(procedure2, 0)
    assert occurrence == result

    assert (
        [StorithmOccurrence(procedure2, 0, 1)] ==
        interpretation.temporary_occurrences
    )

    interpretation.clean_temporary()

    assert [] == interpretation.temporary_occurrences

    result = interpretation.find_storithm_occurrence_starting_in(procedure2, 0)
    assert result is None

    interpretation.add([occurrence])
    interpretation.clean_temporary()

    result = interpretation.find_storithm_occurrence_starting_in(procedure2, 0)
    assert occurrence == result


def test_interpretation_interpret():
    interpretation = Interpretation(
        (
            (StateAtom,),
            (Condition,),
            (ActionAtom, ConditionalStatement, Loop, Procedure)
        )
    )
    atoms = [StateAtom(1, 1), StateAtom(0, 1), ActionAtom(Action())]
    for atom in atoms:
        interpretation.extend(atom)
    procedure = Procedure([[atoms[1], atoms[2]]])
    procedure.connect_with_children()
    interpretation.interpret(True)

    occurrence = StorithmOccurrence(procedure, 1, 2)
    result = interpretation.find_storithm_occurrence_starting_in(procedure, 1)
    assert occurrence == result

    interpretation.clean_temporary()

    result = interpretation.find_storithm_occurrence_starting_in(procedure, 1)
    assert result is None

    interpretation.interpret()
    interpretation.clean_temporary()

    occurrence = StorithmOccurrence(procedure, 1, 2)
    result = interpretation.find_storithm_occurrence_starting_in(procedure, 1)
    assert occurrence == result


def test_interpretation_find_storithm_occurrence_starting_in():
    interpretation = Interpretation(
        (
            (StateAtom,),
            (Condition,),
            (ActionAtom, ConditionalStatement, Loop, Procedure)
        )
    )
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
    interpretation = Interpretation(
        (
            (StateAtom,),
            (Condition,),
            (ActionAtom, ConditionalStatement, Loop, Procedure)
        )
    )
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
    interpretation = Interpretation(
        (
            (StateAtom,),
            (Condition,),
            (ActionAtom, ConditionalStatement, Loop, Procedure)
        )
    )
    atoms = [StateAtom(1, 1), StateAtom(0, 1)]
    condition = Condition(atoms)
    interpretation.add(StorithmOccurrence(atoms[0], 0, 0))
    interpretation.add(StorithmOccurrence(atoms[1], 0, 0))
    interpretation.add(StorithmOccurrence(condition, 0, 0))

    occurrences = interpretation.sample_storithm_occurrences_starting_in(
        0,
        (StateAtom,),
        2
    )
    expected_occurrences = [
        StorithmOccurrence(atoms[0], 0, 0),
        StorithmOccurrence(atoms[1], 0, 0)
    ]
    assert set(expected_occurrences) == set(occurrences)

    occurrences = interpretation.sample_storithm_occurrences_ending_in(
        0,
        (Condition,),
        1
    )
    assert [StorithmOccurrence(condition, 0, 0)] == occurrences
