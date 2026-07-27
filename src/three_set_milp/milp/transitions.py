"""与具体求解器无关的 CBDP 合法 transition 定义。"""

from collections.abc import Sequence
from functools import lru_cache
from itertools import product

from three_set_milp.core.anf import output_monomial_anfs
from three_set_milp.core.order import dominates, reduce_k


# Xiang 等人在 ASIACRYPT 2016 附录 C 给出的紧凑 S 盒不等式。
# 每行依次对应 (a3,a2,a1,a0,b3,b2,b1,b0,常数)，并要求线性和 >= 0。
_PRESENT_SBOX = (
    0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
    0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2,
)
_RECTANGLE_SBOX = (
    0x6, 0x5, 0xC, 0xA, 0x1, 0xE, 0x7, 0x9,
    0xB, 0x0, 0x3, 0xD, 0x8, 0xF, 0x4, 0x2,
)
_COMPACT_SBOX_INEQUALITIES = {
    _PRESENT_SBOX: (
        (1, 1, 1, 1, -1, -1, -1, -1, 0),
        (0, -1, -1, -2, 1, 0, 1, -1, 3),
        (0, -1, -1, -2, 4, 3, 4, 2, 0),
        (-2, -1, -1, 0, 2, 2, 2, 1, 1),
        (-2, -1, -1, 0, 3, 3, 3, 2, 0),
        (0, 0, 0, 0, -1, 1, -1, 1, 1),
        (-2, -2, -2, -4, 1, 4, 1, -3, 7),
        (1, 1, 1, 1, -2, -2, 1, -2, 1),
        (0, -4, -4, -2, 1, -3, 1, 2, 9),
        (0, 0, 0, -2, -1, -1, -1, 2, 3),
        (0, 0, 0, 1, 1, -1, -2, -1, 2),
    ),
    _RECTANGLE_SBOX: (
        (-1, -1, -2, -3, -2, 0, 1, 2, 6),
        (0, 0, 0, 0, -1, -1, 0, 1, 1),
        (1, 1, 1, 1, -1, -1, -1, -1, 0),
        (3, 1, 0, 0, -1, -2, -1, -2, 2),
        (0, 1, 0, 1, 0, -1, -2, -1, 2),
        (0, -1, -1, -1, 1, 2, 0, 2, 1),
        (-2, 0, -1, -1, 1, 0, 2, 1, 2),
        (-3, -1, -1, -2, 1, 2, 2, -1, 4),
        (0, -1, -1, 0, 1, 1, 1, 0, 1),
        (-3, -1, -1, -2, 3, 2, 2, 1, 2),
        (0, 2, 3, 0, -3, -1, -2, -1, 3),
        (-1, -1, 0, -1, 2, 2, 1, 1, 0),
        (0, -2, -1, -1, 3, 4, 2, 2, 0),
        (1, 1, 1, 1, -2, 0, 0, -2, 1),
        (0, 0, 0, 2, -1, -1, -1, 0, 1),
        (3, -4, -1, -1, -2, -1, -3, 2, 7),
        (1, 0, 1, 1, 1, -3, -2, -2, 3),
    ),
}


def copy_transition_is_valid(input_bit: int, output_bits: Sequence[int]) -> bool:
    """判断 Copy 的 CBDP transition 是否满足论文 Model 1。"""
    _validate_bit(input_bit)
    _validate_bits(output_bits)
    return input_bit == sum(output_bits)


def xor_transition_is_valid(input_bits: Sequence[int], output_bit: int) -> bool:
    """判断 XOR 的 CBDP transition 是否满足论文 Model 2。"""
    _validate_bits(input_bits)
    _validate_bit(output_bit)
    return output_bit == sum(input_bits)


def and_transition_is_valid(input_bits: Sequence[int], output_bit: int) -> bool:
    """判断 AND 的 CBDP transition 是否满足论文 Model 3。"""
    _validate_bits(input_bits)
    _validate_bit(output_bit)
    return all(output_bit >= bit for bit in input_bits)


def sbox_transition_is_valid(
    input_exponent: int,
    output_exponent: int,
    monomial_anfs: Sequence[frozenset[int]],
) -> bool:
    """判断一条约化后的 CBDP S-box division trail 是否有效。"""
    if input_exponent < 0:
        raise ValueError("输入指数不能为负数")
    if output_exponent < 0 or output_exponent >= len(monomial_anfs):
        raise ValueError("输出指数超出 S-box 范围")
    output_count = len(monomial_anfs)
    if output_count == 0 or output_count & (output_count - 1):
        raise ValueError("S-box 输出单项式表长度必须是 2 的幂")
    output_width = output_count.bit_length() - 1
    candidates = {
        candidate
        for candidate, input_terms in enumerate(monomial_anfs)
        if any(
            dominates(input_term, input_exponent)
            for input_term in input_terms
        )
    }
    return output_exponent in reduce_k(candidates, output_width)


def compact_sbox_inequalities(
    truth_table: Sequence[int], input_width: int, output_width: int
) -> tuple[tuple[int, ...], ...] | None:
    """返回论文给出的紧凑不等式；未知 S 盒返回 ``None``。"""
    if input_width != 4 or output_width != 4:
        return None
    return _COMPACT_SBOX_INEQUALITIES.get(tuple(truth_table))


def valid_sbox_transitions(
    truth_table: Sequence[int], input_width: int, output_width: int
) -> frozenset[tuple[int, int]]:
    """枚举 S-box 的全部合法 CBDP transition。"""
    return _cached_valid_sbox_transitions(
        tuple(truth_table), input_width, output_width
    )


@lru_cache(maxsize=None)
def _cached_valid_sbox_transitions(
    truth_table: tuple[int, ...], input_width: int, output_width: int
) -> frozenset[tuple[int, int]]:
    """缓存固定 S 盒的合法 transition。"""
    monomial_anfs = output_monomial_anfs(
        truth_table,
        input_width=input_width,
        output_width=output_width,
    )
    transitions: set[tuple[int, int]] = set()
    for input_exponent in range(1 << input_width):
        candidates = {
            output_exponent
            for output_exponent, input_terms in enumerate(monomial_anfs)
            if any(
                dominates(input_term, input_exponent)
                for input_term in input_terms
            )
        }
        transitions.update(
            (input_exponent, output_exponent)
            for output_exponent in reduce_k(candidates, output_width)
        )
    return frozenset(transitions)


def invalid_sbox_assignments(
    truth_table: Sequence[int], input_width: int, output_width: int
) -> tuple[tuple[int, ...], ...]:
    """返回需要由 no-good 约束排除的全部非法 0/1 赋值。"""
    return _cached_invalid_sbox_assignments(
        tuple(truth_table), input_width, output_width
    )


@lru_cache(maxsize=None)
def _cached_invalid_sbox_assignments(
    truth_table: tuple[int, ...], input_width: int, output_width: int
) -> tuple[tuple[int, ...], ...]:
    """缓存固定 S 盒的非法赋值，避免每个局部模型重复枚举。"""
    valid = _cached_valid_sbox_transitions(
        truth_table, input_width, output_width
    )
    invalid: list[tuple[int, ...]] = []
    for assignment in product((0, 1), repeat=input_width + output_width):
        input_exponent = sum(
            bit << index for index, bit in enumerate(assignment[:input_width])
        )
        output_exponent = sum(
            bit << index for index, bit in enumerate(assignment[input_width:])
        )
        if (input_exponent, output_exponent) not in valid:
            invalid.append(assignment)
    return tuple(invalid)


def _validate_bit(bit: int) -> None:
    if bit not in (0, 1) or isinstance(bit, bool):
        raise ValueError("transition 分量只能是整数 0 或 1")


def _validate_bits(bits: Sequence[int]) -> None:
    if not bits:
        raise ValueError("transition 输入不能为空")
    for bit in bits:
        _validate_bit(bit)
