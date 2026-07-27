from collections.abc import Callable

from three_set_milp.core.bdpt import BDPTState
from three_set_milp.core.bitvector import from_index_bits, to_index_bits
from three_set_milp.core.oracle import (
    cube_multiset,
    exact_state_from_multiset,
    state_from_multiset_family,
    state_matches_family,
)
from three_set_milp.core.propagation import (
    compress_and,
    compress_xor,
    copy_bit,
    xor_secret_key,
)


def _all_subsets(width: int) -> list[tuple[int, ...]]:
    """枚举状态空间的全部子集；多重度偶数部分不影响异或和。"""
    points = list(range(1 << width))
    return [
        tuple(point for point in points if subset_mask & (1 << point))
        for subset_mask in range(1 << len(points))
    ]


def _copy_point(value: int, width: int, index: int) -> int:
    bits = list(to_index_bits(value, width))
    return from_index_bits(bits[:index] + [bits[index], bits[index]] + bits[index + 1 :])


def _compress_point(
    value: int,
    width: int,
    first_index: int,
    second_index: int,
    operation: Callable[[int, int], int],
) -> int:
    lower = min(first_index, second_index)
    upper = max(first_index, second_index)
    bits = to_index_bits(value, width)
    merged = operation(bits[first_index], bits[second_index])
    output = []
    for index, bit in enumerate(bits):
        if index == lower:
            output.append(merged)
        elif index != upper:
            output.append(bit)
    return from_index_bits(output)


def test_copy_rule_matches_exhaustive_multiset_oracle() -> None:
    for multiset in _all_subsets(width=3):
        input_state = exact_state_from_multiset(multiset, width=3)
        propagated = copy_bit(input_state, index=1)
        output_multiset = tuple(_copy_point(value, 3, 1) for value in multiset)
        expected = exact_state_from_multiset(output_multiset, width=4)
        assert propagated == expected


def test_and_rule_matches_exhaustive_multiset_oracle() -> None:
    for multiset in _all_subsets(width=3):
        input_state = exact_state_from_multiset(multiset, width=3)
        propagated = compress_and(input_state, 0, 2)
        output_multiset = tuple(
            _compress_point(value, 3, 0, 2, lambda a, b: a & b)
            for value in multiset
        )
        expected = exact_state_from_multiset(output_multiset, width=2)
        assert propagated == expected


def test_xor_rule_matches_exhaustive_multiset_oracle() -> None:
    for multiset in _all_subsets(width=3):
        input_state = exact_state_from_multiset(multiset, width=3)
        propagated = compress_xor(input_state, 0, 2)
        output_multiset = tuple(
            _compress_point(value, 3, 0, 2, lambda a, b: a ^ b)
            for value in multiset
        )
        expected = exact_state_from_multiset(output_multiset, width=2)
        assert propagated == expected


def test_xor_rule_cancels_duplicate_l_outputs() -> None:
    state = BDPTState(
        width=2,
        l=frozenset(
            {
                from_index_bits([1, 0]),
                from_index_bits([0, 1]),
            }
        ),
    )
    assert compress_xor(state, 0, 1).l == frozenset()


def test_secret_key_rule_matches_unknown_key_family() -> None:
    input_multiset = cube_multiset(
        width=3,
        active_indices={1, 2},
        constants={0: 0},
    )
    input_state = exact_state_from_multiset(input_multiset, width=3)
    propagated = xor_secret_key(input_state, index=0)

    output_family = [
        tuple(value ^ key for value in input_multiset) for key in (0, 1)
    ]
    expected = state_from_multiset_family(output_family, width=3)

    assert propagated == expected
    assert state_matches_family(propagated, output_family)
    assert propagated.k == frozenset({0b111})
    assert propagated.l == frozenset({0b110})

