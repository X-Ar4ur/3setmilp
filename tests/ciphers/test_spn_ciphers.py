from three_set_milp.ciphers.present import PRESENT, PRESENT_SBOX, p_layer, sbox_layer
from three_set_milp.ciphers.rectangle import (
    RECTANGLE,
    RECTANGLE_SBOX,
    shift_row,
    sub_column,
)
from three_set_milp.ciphers.spn import propagate_public_permutation
from three_set_milp.core.bdpt import BDPTState


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
