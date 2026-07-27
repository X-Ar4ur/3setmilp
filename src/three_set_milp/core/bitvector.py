"""二进制向量的整数表示与边界检查。"""

from collections.abc import Iterable


def validate_width(width: int) -> None:
    """检查向量维度。"""
    if not isinstance(width, int) or isinstance(width, bool) or width <= 0:
        raise ValueError("向量维度必须是正整数")


def vector_mask(width: int) -> int:
    """返回指定维度的全 1 掩码。"""
    validate_width(width)
    return (1 << width) - 1


def validate_vector(value: int, width: int) -> None:
    """检查整数是否能表示指定维度的二进制向量。"""
    validate_width(width)
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError("向量必须使用整数表示")
    if value < 0 or value > vector_mask(width):
        raise ValueError(f"向量 {value} 超出 {width} 位范围")


def from_index_bits(bits: Iterable[int]) -> int:
    """从索引顺序 ``[u_0, u_1, ...]`` 构造整数向量。"""
    value = 0
    count = 0
    for index, bit in enumerate(bits):
        if bit not in (0, 1) or isinstance(bit, bool):
            raise ValueError("向量分量只能是整数 0 或 1")
        value |= bit << index
        count += 1
    if count == 0:
        raise ValueError("向量不能为空")
    return value


def to_index_bits(value: int, width: int) -> tuple[int, ...]:
    """按索引顺序返回 ``(u_0, u_1, ...)``。"""
    validate_vector(value, width)
    return tuple((value >> index) & 1 for index in range(width))


def from_printed_bits(bits: str) -> int:
    """将论文从左到右打印的 ``u_0 u_1 ...`` 转换为内部表示。"""
    compact = bits.replace(" ", "").replace("_", "")
    if not compact or any(char not in "01" for char in compact):
        raise ValueError("打印向量必须是非空的 0/1 字符串")
    return from_index_bits(int(char) for char in compact)


def to_printed_bits(value: int, width: int) -> str:
    """按论文索引从小到大的顺序打印向量。"""
    return "".join(str(bit) for bit in to_index_bits(value, width))


def unit_vector(index: int, width: int) -> int:
    """返回仅第 ``index`` 个分量为 1 的单位向量。"""
    validate_width(width)
    if not isinstance(index, int) or isinstance(index, bool):
        raise TypeError("向量索引必须是整数")
    if index < 0 or index >= width:
        raise IndexError(f"索引 {index} 超出 {width} 位向量范围")
    return 1 << index


def extract_bits(value: int, width: int, indices: Iterable[int]) -> int:
    """按给定索引顺序抽取分量，结果的第 0 位对应第一个索引。"""
    validate_vector(value, width)
    selected = tuple(indices)
    if len(set(selected)) != len(selected):
        raise ValueError("抽取索引不能重复")
    for index in selected:
        unit_vector(index, width)
    return from_index_bits((value >> index) & 1 for index in selected)


def replace_bits(
    value: int,
    width: int,
    indices: Iterable[int],
    replacement: int,
) -> int:
    """按给定索引顺序替换分量，其他分量保持不变。"""
    validate_vector(value, width)
    selected = tuple(indices)
    if not selected:
        raise ValueError("替换索引不能为空")
    if len(set(selected)) != len(selected):
        raise ValueError("替换索引不能重复")
    validate_vector(replacement, len(selected))

    result = value
    for local_index, state_index in enumerate(selected):
        bit_mask = unit_vector(state_index, width)
        if replacement & (1 << local_index):
            result |= bit_mask
        else:
            result &= ~bit_mask
    return result


def permute_bits(value: int, width: int, source_indices: Iterable[int]) -> int:
    """置换向量；输出第 i 位取自 ``source_indices[i]``。"""
    validate_vector(value, width)
    permutation = tuple(source_indices)
    if sorted(permutation) != list(range(width)):
        raise ValueError("位排列必须恰好包含全部输入索引")
    return extract_bits(value, width, permutation)
