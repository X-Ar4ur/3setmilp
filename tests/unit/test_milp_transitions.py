from itertools import product

from three_set_milp.ciphers.present import PRESENT_SBOX
from three_set_milp.ciphers.rectangle import RECTANGLE_SBOX
from three_set_milp.core.bitvector import from_index_bits, to_index_bits
from three_set_milp.milp.transitions import (
    and_transition_is_valid,
    compact_sbox_inequalities,
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


def test_paper_sbox_division_trail_counts_after_reduce0() -> None:
    """核对 Xiang 等人附录 B 给出的 47/49 条约化 trail。"""
    present = valid_sbox_transitions(PRESENT_SBOX, 4, 4)
    rectangle = valid_sbox_transitions(RECTANGLE_SBOX, 4, 4)

    assert len(present) == 47
    assert len(rectangle) == 49
    assert {
        output for input_value, output in present if input_value == 0
    } == {0}
    assert {
        output for input_value, output in rectangle if input_value == 0
    } == {0}


def test_compact_paper_inequalities_exactly_describe_sbox_trails() -> None:
    """穷举验证附录 C 的不等式没有增加或遗漏二进制可行点。"""
    for truth_table in (PRESENT_SBOX, RECTANGLE_SBOX):
        inequalities = compact_sbox_inequalities(truth_table, 4, 4)
        assert inequalities is not None
        expected = valid_sbox_transitions(truth_table, 4, 4)
        modeled = {
            (input_value, output_value)
            for input_value, output_value in product(range(16), repeat=2)
            if all(
                sum(
                    coefficient * bit
                    for coefficient, bit in zip(
                        row[:-1],
                        tuple(reversed(to_index_bits(input_value, 4)))
                        + tuple(reversed(to_index_bits(output_value, 4))),
                        strict=True,
                    )
                )
                + row[-1]
                >= 0
                for row in inequalities
            )
        }
        assert modeled == expected
