import pytest

from three_set_milp.core.bitvector import (
    from_index_bits,
    from_printed_bits,
    to_index_bits,
    to_printed_bits,
)
from three_set_milp.core.order import (
    dominates,
    reduce_k,
    reduce_l,
    strictly_dominates,
)


def test_index_bits_round_trip() -> None:
    value = from_index_bits([1, 0, 1, 1])
    assert value == 0b1101
    assert to_index_bits(value, 4) == (1, 0, 1, 1)
    assert to_printed_bits(value, 4) == "1011"


def test_printed_bits_are_not_interpreted_as_normal_binary() -> None:
    assert from_printed_bits("1000") == 0b0001
    assert from_printed_bits("0001") == 0b1000


def test_dominance_relation() -> None:
    assert dominates(0b1110, 0b0110)
    assert dominates(0b0110, 0b0110)
    assert not dominates(0b0010, 0b0110)
    assert strictly_dominates(0b1110, 0b0110)
    assert not strictly_dominates(0b0110, 0b0110)


def test_reduce_k_removes_larger_redundant_vectors() -> None:
    assert reduce_k({0b0001, 0b0011, 0b0111}, width=4) == frozenset(
        {0b0001}
    )


def test_reduce_l_removes_vectors_in_unknown_upper_closure() -> None:
    assert reduce_l({0b0001}, {0b0001, 0b0010, 0b0011}, width=4) == frozenset(
        {0b0010}
    )


@pytest.mark.parametrize("bits", ["", "10x1", "1021"])
def test_rejects_invalid_printed_bits(bits: str) -> None:
    with pytest.raises(ValueError):
        from_printed_bits(bits)

