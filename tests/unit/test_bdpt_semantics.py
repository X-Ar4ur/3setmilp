from three_set_milp.core.bdpt import BDPTState, Parity
from three_set_milp.core.bitvector import from_printed_bits


def test_original_paper_example_1_parity_table() -> None:
    state = BDPTState(
        width=4,
        k=frozenset(
            {
                from_printed_bits("0001"),
                from_printed_bits("0110"),
            }
        ),
        l=frozenset(
            {
                from_printed_bits("1000"),
                from_printed_bits("1010"),
                from_printed_bits("0010"),
                from_printed_bits("0011"),
            }
        ),
    )

    expected = "0?1?0???1?1?0???"
    actual = []
    symbols = {
        Parity.ZERO: "0",
        Parity.ONE: "1",
        Parity.UNKNOWN: "?",
    }
    for paper_hex in range(16):
        exponent = from_printed_bits(f"{paper_hex:04b}")
        actual.append(symbols[state.parity(exponent)])

    assert "".join(actual) == expected


def test_normalization_preserves_complete_parity_table() -> None:
    state = BDPTState(
        width=4,
        k=frozenset({0b0001, 0b0011, 0b0111}),
        l=frozenset({0b0010, 0b0011, 0b1010}),
    )
    normalized = state.normalized()

    assert normalized.k == frozenset({0b0001})
    assert normalized.l == frozenset({0b0010, 0b1010})
    assert normalized.parity_table() == state.parity_table()

