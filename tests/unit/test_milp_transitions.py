from itertools import product

from three_set_milp.core.bitvector import from_index_bits, to_index_bits
from three_set_milp.milp.transitions import (
    and_transition_is_valid,
    copy_transition_is_valid,
    invalid_sbox_assignments,
    valid_sbox_transitions,
    xor_transition_is_valid,
)


def test_copy_transition_relation() -> None:
    valid = {
        (input_bit, output_bits)
        for input_bit in (0, 1)
        for output_bits in product((0, 1), repeat=2)
        if copy_transition_is_valid(input_bit, output_bits)
    }
    assert valid == {(0, (0, 0)), (1, (1, 0)), (1, (0, 1))}


def test_xor_transition_relation() -> None:
    valid = {
        (input_bits, output_bit)
        for input_bits in product((0, 1), repeat=2)
        for output_bit in (0, 1)
        if xor_transition_is_valid(input_bits, output_bit)
    }
    assert valid == {((0, 0), 0), ((1, 0), 1), ((0, 1), 1)}


def test_and_transition_relation_matches_paper_inequalities() -> None:
    valid = {
        (input_bits, output_bit)
        for input_bits in product((0, 1), repeat=2)
        for output_bit in (0, 1)
        if and_transition_is_valid(input_bits, output_bit)
    }
    assert valid == {
        ((0, 0), 0),
        ((0, 0), 1),
        ((1, 0), 1),
        ((0, 1), 1),
        ((1, 1), 1),
    }


def test_sbox_transition_and_invalid_assignments_partition_space() -> None:
    truth_table = []
    for value in range(4):
        x0, x1 = to_index_bits(value, 2)
        truth_table.append(from_index_bits([x0, (x0 & x1) ^ x1]))

    valid = valid_sbox_transitions(truth_table, 2, 2)
    invalid = invalid_sbox_assignments(truth_table, 2, 2)

    invalid_pairs = set()
    for assignment in invalid:
        input_value = from_index_bits(assignment[:2])
        output_value = from_index_bits(assignment[2:])
        invalid_pairs.add((input_value, output_value))

    all_pairs = set(product(range(4), repeat=2))
    assert valid.isdisjoint(invalid_pairs)
    assert set(valid) | invalid_pairs == all_pairs

