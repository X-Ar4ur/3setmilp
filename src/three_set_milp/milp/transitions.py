"""与具体求解器无关的 CBDP 合法 transition 定义。"""

from collections.abc import Sequence
from functools import lru_cache
from itertools import product

from three_set_milp.core.anf import output_monomial_anfs
from three_set_milp.core.order import dominates


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
    """按 CBDP S-box 规则判断一条输入输出 transition。"""
    if input_exponent < 0:
        raise ValueError("输入指数不能为负数")
    if output_exponent < 0 or output_exponent >= len(monomial_anfs):
        raise ValueError("输出指数超出 S-box 范围")
    return any(
        dominates(input_term, input_exponent)
        for input_term in monomial_anfs[output_exponent]
    )


def valid_sbox_transitions(
    truth_table: Sequence[int], input_width: int, output_width: int
) -> frozenset[tuple[int, int]]:
    """枚举 S-box 的全部合法 CBDP transition。"""
    monomial_anfs = output_monomial_anfs(
        truth_table,
        input_width=input_width,
        output_width=output_width,
    )
    return frozenset(
        (input_exponent, output_exponent)
        for input_exponent in range(1 << input_width)
        for output_exponent in range(1 << output_width)
        if sbox_transition_is_valid(
            input_exponent,
            output_exponent,
            monomial_anfs,
        )
    )


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
    valid = valid_sbox_transitions(truth_table, input_width, output_width)
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
