"""布尔函数 ANF 的小规模精确运算。"""

from collections.abc import Sequence

from .bitvector import validate_vector, validate_width


ANF = frozenset[int]


def truth_table_to_anf(values: Sequence[int]) -> ANF:
    """通过 Möbius 变换将单输出真值表转换为 ANF 单项式集合。"""
    size = len(values)
    if size == 0 or size & (size - 1):
        raise ValueError("真值表长度必须是 2 的正整数次幂")
    if any(value not in (0, 1) or isinstance(value, bool) for value in values):
        raise ValueError("布尔真值表只能包含整数 0 或 1")

    coefficients = list(values)
    width = size.bit_length() - 1
    for index in range(width):
        bit = 1 << index
        for mask in range(size):
            if mask & bit:
                coefficients[mask] ^= coefficients[mask ^ bit]
    return frozenset(
        exponent for exponent, coefficient in enumerate(coefficients) if coefficient
    )


def multiply_anf(left: ANF, right: ANF) -> ANF:
    """在布尔环中相乘两个 ANF，多项式系数按模 2 合并。"""
    result: set[int] = set()
    for left_term in left:
        for right_term in right:
            term = left_term | right_term
            if term in result:
                result.remove(term)
            else:
                result.add(term)
    return frozenset(result)


def coordinate_anfs(
    truth_table: Sequence[int], input_width: int, output_width: int
) -> tuple[ANF, ...]:
    """计算向量布尔函数每个输出坐标的 ANF。"""
    validate_width(input_width)
    validate_width(output_width)
    if len(truth_table) != 1 << input_width:
        raise ValueError("向量函数真值表长度与输入维度不一致")
    for value in truth_table:
        validate_vector(value, output_width)
    return tuple(
        truth_table_to_anf(
            tuple((value >> output_index) & 1 for value in truth_table)
        )
        for output_index in range(output_width)
    )


def output_monomial_anfs(
    truth_table: Sequence[int], input_width: int, output_width: int
) -> tuple[ANF, ...]:
    """计算所有输出单项式代回输入后的 ANF。"""
    coordinates = coordinate_anfs(truth_table, input_width, output_width)
    monomials: list[ANF] = []
    for output_exponent in range(1 << output_width):
        polynomial: ANF = frozenset({0})
        for output_index, coordinate in enumerate(coordinates):
            if output_exponent & (1 << output_index):
                polynomial = multiply_anf(polynomial, coordinate)
        monomials.append(polynomial)
    return tuple(monomials)

