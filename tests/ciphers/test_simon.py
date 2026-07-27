from three_set_milp.ciphers.simon import (
    SIMON32,
    core_indices,
    decode_state,
    encode_state,
    format_paper_state,
    parse_paper_state,
    propagate_core,
    propagate_key_and_swap,
    rotate_left,
    round_function,
)
from three_set_milp.core.bdpt import BDPTState
from three_set_milp.core.bitvector import extract_bits, replace_bits


def test_state_encoding_and_paper_format_round_trip() -> None:
    state = parse_paper_state(
        "1011111111111111" "0111111111111111",
        SIMON32,
    )
    assert format_paper_state(state, SIMON32) == (
        "1011111111111111" "0111111111111111"
    )
    assert decode_state(state, SIMON32) == (0xBFFF, 0x7FFF)


def test_core_indices_match_paper_q_1_15_example() -> None:
    ell_1 = parse_paper_state(
        "1011111111111111" "0111111111111111",
        SIMON32,
    )
    indices = core_indices(SIMON32, output_index=15)
    assert indices == (14, 7, 13, 31)
    assert extract_bits(ell_1, 32, indices) == 0b0110


def test_q_1_15_propagation_and_odd_cancellation_match_paper() -> None:
    ell_1 = parse_paper_state(
        "1011111111111111" "0111111111111111",
        SIMON32,
    )
    ell_2 = parse_paper_state(
        "1001111111111111" "1111111111111111",
        SIMON32,
    )
    state = BDPTState(width=32, l=frozenset({ell_1, ell_2}))

    output = propagate_core(state, SIMON32, output_index=15)

    ell_3 = ell_1
    ell_4 = parse_paper_state(
        "1011111111111111" "1111111111111111",
        SIMON32,
    )
    assert output.k == frozenset()
    assert output.l == frozenset({ell_3, ell_4})


def test_q_1_16_key_and_swap_match_paper() -> None:
    ell_3 = parse_paper_state(
        "1011111111111111" "0111111111111111",
        SIMON32,
    )
    ell_4 = parse_paper_state(
        "1011111111111111" "1111111111111111",
        SIMON32,
    )
    state = BDPTState(width=32, l=frozenset({ell_3, ell_4}))

    output = propagate_key_and_swap(state, SIMON32)

    expected_k = parse_paper_state(
        "1111111111111111" "1011111111111111",
        SIMON32,
    )
    expected_l = parse_paper_state(
        "0111111111111111" "1011111111111111",
        SIMON32,
    )
    assert output.k == frozenset({expected_k})
    assert output.l == frozenset({expected_l})


def test_concrete_round_equals_sequential_core_updates() -> None:
    left = 0x6565
    right = 0x6877
    key = 0x1918

    next_left, next_right = round_function(left, right, key, SIMON32)

    state = encode_state(left, right, SIMON32)
    indices_by_output = [core_indices(SIMON32, index) for index in range(16)]
    for indices in indices_by_output:
        a, b, c, d = (
            (state >> state_index) & 1 for state_index in indices
        )
        local_output = a | (b << 1) | (c << 2) | (((a & b) ^ c ^ d) << 3)
        state = replace_bits(state, 32, indices, local_output)

    core_left, core_right = decode_state(state, SIMON32)
    assert core_left == left
    assert core_right ^ key == next_left
    assert next_right == left
    assert rotate_left(left, 1, 16) & rotate_left(left, 8, 16) ^ rotate_left(
        left, 2, 16
    ) ^ right ^ key == next_left

