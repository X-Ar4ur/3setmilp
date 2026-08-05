import pytest

from three_set_milp.ciphers.present import (
    PRESENT,
    PRESENT_PAPER_PRINT_INDICES,
    PRESENT_SBOX,
    p_layer,
    sbox_layer,
)
from three_set_milp.ciphers.rectangle import (
    RECTANGLE,
    RECTANGLE_PAPER_PRINT_INDICES,
    RECTANGLE_SBOX,
    shift_row,
    sub_column,
)
from three_set_milp.ciphers.spn import (
    propagate_known_key_and_permutation,
    propagate_public_permutation,
)
from three_set_milp.core.bdpt import BDPTState
from three_set_milp.core.bitvector import unit_vector
from three_set_milp.milp.spn import SPNBoundary
from three_set_milp.search.spn import spn_k_bdpt_parts, spn_search_parts


def test_present_constants_and_sbox_bit_order() -> None:
    assert PRESENT_SBOX == (
        0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
        0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2,
    )
    assert sbox_layer(0) == int("C" * 16, 16)
    assert sbox_layer(0xF) & 0xF == 0x2


def test_present_permutation_follows_input_to_destination_definition() -> None:
    for input_index in range(64):
        destination = 16 * input_index % 63 if input_index < 63 else 63
        assert p_layer(1 << input_index) == 1 << destination


def test_rectangle_constants_and_column_bit_order() -> None:
    assert RECTANGLE_SBOX == (
        0x6, 0x5, 0xC, 0xA, 0x1, 0xE, 0x7, 0x9,
        0xB, 0x0, 0x3, 0xD, 0x8, 0xF, 0x4, 0x2,
    )
    # S(0)=0110，故全零状态的第 1、2 行变为全一。
    assert sub_column(0) == (0xFFFF << 16) | (0xFFFF << 32)
    # 第 0 列的 row0 是 S 盒输入最低位。
    assert sub_column(1) & ((1 << 0) | (1 << 16) | (1 << 32) | (1 << 48)) == (
        (1 << 0) | (1 << 32)
    )


def test_rectangle_shift_row_uses_specified_left_rotations() -> None:
    for row, distance in enumerate((0, 1, 12, 13)):
        for input_column in range(16):
            input_index = 16 * row + input_column
            output_column = (input_column + distance) % 16
            assert shift_row(1 << input_index) == 1 << (16 * row + output_column)


def test_public_permutation_matches_concrete_helpers() -> None:
    value = 0x0123456789ABCDEF
    present_state = BDPTState(width=64, l=frozenset({value}))
    rectangle_state = BDPTState(width=64, l=frozenset({value}))
    assert propagate_public_permutation(present_state, PRESENT).l == frozenset(
        {p_layer(value)}
    )
    assert propagate_public_permutation(rectangle_state, RECTANGLE).l == frozenset(
        {shift_row(value)}
    )


def test_table5_cipher_layouts_are_explicit() -> None:
    assert PRESENT_PAPER_PRINT_INDICES == tuple(reversed(range(64)))
    assert RECTANGLE_PAPER_PRINT_INDICES[:16] == tuple(reversed(range(16)))
    assert RECTANGLE_PAPER_PRINT_INDICES[16:32] == tuple(reversed(range(16, 32)))


@pytest.mark.parametrize(
    ("key_bit_order", "expected_indices"),
    [
        ("ascending", list(range(64))),
        ("descending", list(reversed(range(64)))),
    ],
)
def test_k_bdpt_splits_every_round_key_bit(
    key_bit_order: str,
    expected_indices: list[int],
) -> None:
    parts = spn_k_bdpt_parts(
        PRESENT,
        rounds=2,
        key_bit_order=key_bit_order,
    )

    round_width = 16 + 1 + 64
    assert len(parts) == 2 * round_width
    for round_index in range(2):
        offset = round_index * round_width
        assert parts[offset + 16].boundary == SPNBoundary(round_index, 16)
        key_parts = parts[offset + 17 : offset + round_width]
        assert [part.secret_key_index for part in key_parts] == expected_indices
        assert all(
            part.boundary == SPNBoundary(round_index + 1, 0)
            for part in key_parts
        )
        checked_parts = (
            (key_parts[0], expected_indices[0]),
            (key_parts[-1], expected_indices[-1]),
        )
        for part, index in checked_parts:
            output = part.propagate(BDPTState(width=64, l=frozenset({0})))
            assert output.k == frozenset({unit_vector(index, 64)})


def test_k_bdpt_rejects_unknown_key_bit_order() -> None:
    with pytest.raises(ValueError, match="轮密钥比特顺序"):
        spn_k_bdpt_parts(PRESENT, rounds=1, key_bit_order="middle")


def test_main_bdpt_key_treatment_switch_only_suppresses_rule4_k() -> None:
    input_state = BDPTState(width=64, l=frozenset({0}))
    paper_round_end = spn_search_parts(PRESENT, rounds=1)[-1]
    diagnostic_round_end = spn_search_parts(
        PRESENT,
        rounds=1,
        key_treatment="ignore-rule4",
    )[-1]

    paper_output = paper_round_end.propagate(input_state)
    diagnostic_output = diagnostic_round_end.propagate(input_state)

    assert paper_output.k == frozenset(unit_vector(index, 64) for index in range(64))
    assert paper_output.l == frozenset({0})
    assert diagnostic_output.k == frozenset()
    assert diagnostic_output.l == frozenset({0})


def test_main_bdpt_fixed_round_key_tracks_known_translation() -> None:
    input_state = BDPTState(width=64, l=frozenset({0}))
    zero_key_parts = spn_search_parts(
        PRESENT,
        rounds=1,
        key_treatment="fixed",
        round_keys=(0,),
    )
    one_key_parts = spn_search_parts(
        PRESENT,
        rounds=1,
        key_treatment="fixed",
        round_keys=(1,),
    )

    assert len(zero_key_parts) == 17
    assert len(one_key_parts) == 18
    assert zero_key_parts[-1].propagate(input_state) == input_state
    assert one_key_parts[-1].boundary == SPNBoundary(1, 0)
    assert one_key_parts[-1].propagate(input_state).k == frozenset()
    assert one_key_parts[-1].propagate(input_state).l == frozenset({0, 1})


def test_split_fixed_key_matches_combined_public_translation() -> None:
    input_state = BDPTState(width=64, l=frozenset({0, 1 << 9}))
    round_key = 0b101
    parts = spn_search_parts(
        PRESENT,
        rounds=1,
        key_treatment="fixed",
        round_keys=(round_key,),
    )
    split = input_state
    for part in parts[-3:]:
        split = part.propagate(split)

    assert split == propagate_known_key_and_permutation(
        input_state,
        PRESENT,
        round_key,
    )


def test_main_bdpt_fixed_round_keys_require_one_value_per_round() -> None:
    with pytest.raises(ValueError, match="每一轮"):
        spn_search_parts(
            PRESENT,
            rounds=2,
            key_treatment="fixed",
            round_keys=(0,),
        )


def test_main_bdpt_rejects_unknown_key_treatment() -> None:
    with pytest.raises(ValueError, match="密钥处理方式"):
        spn_search_parts(PRESENT, rounds=1, key_treatment="unknown")
