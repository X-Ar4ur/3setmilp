"""PRESENT 的位编号、S 盒和置换参数。"""

from three_set_milp.core.bitvector import validate_vector

from .spn import SPNParameters


PRESENT_SBOX = (0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
                0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2)


def _present_source_permutation() -> tuple[int, ...]:
    """将规范的“输入 i 移到 P(i)”转换为输出到输入的索引表。"""
    destination = tuple(16 * index % 63 if index < 63 else 63 for index in range(64))
    source = [0] * 64
    for input_index, output_index in enumerate(destination):
        source[output_index] = input_index
    return tuple(source)


PRESENT = SPNParameters(
    name="present",
    block_size=64,
    sbox_table=PRESENT_SBOX,
    sbox_groups=tuple(tuple(range(4 * index, 4 * index + 4)) for index in range(16)),
    permutation=_present_source_permutation(),
)

# PRESENT 规范将 bit 0 放在分组最右侧，Table 5 按 x63,...,x0 打印。
PRESENT_PAPER_PRINT_INDICES = tuple(reversed(range(64)))


def sbox_layer(value: int) -> int:
    """计算 PRESENT 的公开 S 盒层，用于位序和测试向量校验。"""
    validate_vector(value, 64)
    output = 0
    for index in range(16):
        output |= PRESENT_SBOX[(value >> (4 * index)) & 0xF] << (4 * index)
    return output


def p_layer(value: int) -> int:
    """计算规范定义的 PRESENT 位排列。"""
    validate_vector(value, 64)
    output = 0
    for output_index, input_index in enumerate(PRESENT.permutation):
        output |= ((value >> input_index) & 1) << output_index
    return output
