from three_set_milp.ciphers.lblock import (
    LBLOCK_P,
    LBLOCK_SBOXES,
    active_indices_from_paper_pattern,
    encrypt,
    f_function,
    format_paper_parities,
    propagate_keyed_sbox_xor_local,
    propagate_public_sbox_xor_local,
    round_function,
)
from three_set_milp.core.oracle import (
    cube_multiset,
    exact_state_from_multiset,
    monomial_parity,
)
from three_set_milp.core.bdpt import Parity


def test_lblock_data_sboxes_and_permutation() -> None:
    assert len(LBLOCK_SBOXES) == 8
    assert all(sorted(sbox) == list(range(16)) for sbox in LBLOCK_SBOXES)
    assert LBLOCK_P == (2, 0, 3, 1, 6, 4, 7, 5)
    # 每个输入 nibble 的值 0 经 Sj 后写入 P(j)。
    expected = sum(sbox[0] << (4 * LBLOCK_P[index]) for index, sbox in enumerate(LBLOCK_SBOXES))
    assert f_function(0, 0) == expected


def test_lblock_round_uses_rotated_right_half() -> None:
    left, right = round_function(0, 0x00000001, 0)
    assert left == f_function(0, 0) ^ 0x00000100
    assert right == 0


def test_lblock_official_test_vectors() -> None:
    assert encrypt(0, 0) == 0xC218185308E75BCD
    assert encrypt(
        0x0123456789ABCDEF,
        0x0123456789ABCDEFFEDC,
    ) == 0x4B7179D8EBEE0C26


def test_lblock_keyed_local_core_is_sound_for_unknown_key_family() -> None:
    input_multiset = cube_multiset(
        width=8,
        active_indices={0, 4},
        constants={index: 0 for index in range(8) if index not in {0, 4}},
    )
    input_state = exact_state_from_multiset(input_multiset, width=8)
    propagated = propagate_keyed_sbox_xor_local(input_state, LBLOCK_SBOXES[0])

    output_family = []
    for key in range(16):
        output_multiset = []
        for value in input_multiset:
            x = value & 0xF
            y = value >> 4
            z = LBLOCK_SBOXES[0][x ^ key] ^ y
            output_multiset.append(x | (z << 4))
        output_family.append(tuple(output_multiset))
    for exponent in range(1 << 8):
        observed = {
            monomial_parity(multiset, exponent, 8)
            for multiset in output_family
        }
        predicted = propagated.parity(exponent)
        if predicted is Parity.ZERO:
            assert observed == {0}
        elif predicted is Parity.ONE:
            assert observed == {1}
    assert propagated.k


def test_lblock_public_local_core_matches_fixed_key_multiset() -> None:
    input_multiset = cube_multiset(
        width=8,
        active_indices={0, 4},
        constants={index: 0 for index in range(8) if index not in {0, 4}},
    )
    input_state = exact_state_from_multiset(input_multiset, width=8)
    propagated = propagate_public_sbox_xor_local(input_state, LBLOCK_SBOXES[0])
    output_multiset = []
    for value in input_multiset:
        x = value & 0xF
        y = value >> 4
        output_multiset.append(x | ((LBLOCK_SBOXES[0][x] ^ y) << 4))
    assert propagated == exact_state_from_multiset(output_multiset, width=8)


def test_lblock_paper_pattern_keeps_x_half_first() -> None:
    active = active_indices_from_paper_pattern("a" + "c" * 31 + "," + "c" * 31 + "a")
    assert active == frozenset({31, 32})
    assert format_paper_parities({31: "b", 32: "?"}) == (
        "b" + "-" * 31 + "," + "-" * 31 + "?"
    )
