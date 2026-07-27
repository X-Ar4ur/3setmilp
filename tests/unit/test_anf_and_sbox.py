from three_set_milp.core.anf import (
    multiply_anf,
    output_monomial_anfs,
    truth_table_to_anf,
)
from three_set_milp.core.bdpt import BDPTState
from three_set_milp.core.bitvector import (
    from_index_bits,
    from_printed_bits,
    to_index_bits,
)
from three_set_milp.core.oracle import exact_state_from_multiset
from three_set_milp.core.propagation import propagate_sbox


def _all_subsets(width: int) -> list[tuple[int, ...]]:
    points = list(range(1 << width))
    return [
        tuple(point for point in points if subset_mask & (1 << point))
        for subset_mask in range(1 << len(points))
    ]


def test_truth_table_to_anf() -> None:
    # f(x0, x1) = 1 + x0 + x0*x1
    truth_table = (1, 0, 1, 1)
    assert truth_table_to_anf(truth_table) == frozenset(
        {0b00, 0b01, 0b11}
    )


def test_multiply_anf_uses_boolean_monomials_and_mod_two_coefficients() -> None:
    left = frozenset({0b01, 0b10})
    right = frozenset({0b01, 0b10})
    # (x0+x1)^2 = x0+x1，因为两个 x0*x1 项相消。
    assert multiply_anf(left, right) == frozenset({0b01, 0b10})


def test_sbox_propagation_matches_all_small_multisets() -> None:
    # F(x0,x1) = (x0, x0*x1 + x1)
    truth_table = []
    for value in range(4):
        x0, x1 = to_index_bits(value, 2)
        truth_table.append(from_index_bits([x0, (x0 & x1) ^ x1]))

    for multiset in _all_subsets(width=2):
        input_state = exact_state_from_multiset(multiset, width=2)
        propagated = propagate_sbox(input_state, truth_table, output_width=2)
        output_multiset = tuple(truth_table[value] for value in multiset)
        expected = exact_state_from_multiset(output_multiset, width=2)
        assert propagated == expected


def test_simon_core_matches_original_paper_table() -> None:
    # F(a,b,c,d) = (a,b,c,a*b+c+d)，对应论文 4-bit 核心操作。
    truth_table = []
    for value in range(16):
        a, b, c, d = to_index_bits(value, 4)
        truth_table.append(from_index_bits([a, b, c, (a & b) ^ c ^ d]))

    expected_rows = {
        "0000": {"0000"},
        "1000": {"1000"},
        "0100": {"0100"},
        "1100": {"1100", "0001", "1001", "0101", "1101"},
        "0010": {"0010", "0001", "0011"},
        "1010": {"1010", "1001", "1011"},
        "0110": {"0110", "0101", "0111"},
        "1110": {"1110", "0011", "1011", "0111", "1101"},
    }
    for prefix in range(8):
        bits = f"{prefix:03b}1"
        expected_rows[bits] = {bits}

    for input_bits, output_rows in expected_rows.items():
        state = BDPTState(
            width=4,
            l=frozenset({from_printed_bits(input_bits)}),
        )
        output = propagate_sbox(state, truth_table, output_width=4)
        expected = frozenset(from_printed_bits(bits) for bits in output_rows)
        assert output.k == frozenset()
        assert output.l == expected


def test_output_monomial_anfs_include_simon_nonlinear_terms() -> None:
    truth_table = []
    for value in range(16):
        a, b, c, d = to_index_bits(value, 4)
        truth_table.append(from_index_bits([a, b, c, (a & b) ^ c ^ d]))

    anfs = output_monomial_anfs(truth_table, 4, 4)
    assert anfs[from_printed_bits("0001")] == frozenset(
        {
            from_printed_bits("1100"),
            from_printed_bits("0010"),
            from_printed_bits("0001"),
        }
    )

