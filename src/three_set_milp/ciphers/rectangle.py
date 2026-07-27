"""RECTANGLE 的 bitslice 状态布局、S 盒和行移位参数。"""

from three_set_milp.core.bitvector import validate_vector

from .spn import SPNParameters


RECTANGLE_SBOX = (0x6, 0x5, 0xC, 0xA, 0x1, 0xE, 0x7, 0x9,
                  0xB, 0x0, 0x3, 0xD, 0x8, 0xF, 0x4, 0x2)
RECTANGLE_ROTATIONS = (0, 1, 12, 13)


def _rectangle_source_permutation() -> tuple[int, ...]:
    """把每个 16-bit 行左旋转换为输出位到输入位的索引表。"""
    source: list[int] = []
    for row, distance in enumerate(RECTANGLE_ROTATIONS):
        for output_column in range(16):
            input_column = (output_column - distance) % 16
            source.append(16 * row + input_column)
    return tuple(source)


RECTANGLE = SPNParameters(
    name="rectangle",
    block_size=64,
    sbox_table=RECTANGLE_SBOX,
    sbox_groups=tuple(
        tuple(16 * row + column for row in range(4))
        for column in range(16)
    ),
    permutation=_rectangle_source_permutation(),
)


def sub_column(value: int) -> int:
    """按列计算 RECTANGLE S 盒层，row 0 对应 S 盒最低位。"""
    validate_vector(value, 64)
    output = 0
    for column, group in enumerate(RECTANGLE.sbox_groups):
        nibble = sum(((value >> index) & 1) << row for row, index in enumerate(group))
        substituted = RECTANGLE_SBOX[nibble]
        for row, index in enumerate(group):
            output |= ((substituted >> row) & 1) << index
    return output


def shift_row(value: int) -> int:
    """计算 RECTANGLE 的四行循环左移。"""
    validate_vector(value, 64)
    output = 0
    for output_index, input_index in enumerate(RECTANGLE.permutation):
        output |= ((value >> input_index) & 1) << output_index
    return output
