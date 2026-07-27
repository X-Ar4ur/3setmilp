"""论文定义的 BDPT 基本传播规则。"""

from collections.abc import Callable, Sequence

from .anf import output_monomial_anfs
from .bdpt import BDPTState
from .bitvector import (
    extract_bits,
    from_index_bits,
    permute_bits,
    replace_bits,
    to_index_bits,
    unit_vector,
    validate_vector,
)
from .order import dominates


def _toggle(vectors: set[int], vector: int) -> None:
    """按模 2 插入向量。"""
    if vector in vectors:
        vectors.remove(vector)
    else:
        vectors.add(vector)


def _copy_vector(value: int, width: int, index: int, pair: tuple[int, int]) -> int:
    """将一个输入分量替换为相邻的两个输出分量。"""
    validate_vector(value, width)
    unit_vector(index, width)
    bits = list(to_index_bits(value, width))
    return from_index_bits(bits[:index] + list(pair) + bits[index + 1 :])


def _compress_vector(
    value: int,
    width: int,
    first_index: int,
    second_index: int,
    merged_bit: int,
) -> int:
    """合并两个分量，并将结果放在较小索引处。"""
    validate_vector(value, width)
    unit_vector(first_index, width)
    unit_vector(second_index, width)
    if first_index == second_index:
        raise ValueError("压缩操作需要两个不同的输入分量")
    if merged_bit not in (0, 1):
        raise ValueError("合并后的分量只能是 0 或 1")

    lower = min(first_index, second_index)
    upper = max(first_index, second_index)
    input_bits = to_index_bits(value, width)
    output_bits: list[int] = []
    for index, bit in enumerate(input_bits):
        if index == lower:
            output_bits.append(merged_bit)
        elif index != upper:
            output_bits.append(bit)
    return from_index_bits(output_bits)


def copy_bit(state: BDPTState, index: int) -> BDPTState:
    """传播 ``x_i -> (x_i, x_i)``。"""
    unit_vector(index, state.width)
    output_k: set[int] = set()
    output_l: set[int] = set()

    for vector in state.k:
        bit = (vector >> index) & 1
        pairs = ((0, 0),) if bit == 0 else ((1, 0), (0, 1))
        output_k.update(
            _copy_vector(vector, state.width, index, pair) for pair in pairs
        )

    for vector in state.l:
        bit = (vector >> index) & 1
        pairs = ((0, 0),) if bit == 0 else ((1, 0), (0, 1), (1, 1))
        output_l.update(
            _copy_vector(vector, state.width, index, pair) for pair in pairs
        )

    return BDPTState(
        width=state.width + 1,
        k=frozenset(output_k),
        l=frozenset(output_l),
    ).normalized()


def compress_and(
    state: BDPTState, first_index: int, second_index: int
) -> BDPTState:
    """传播两个输入分量的 AND 压缩。"""
    output_k: set[int] = set()
    output_l: set[int] = set()

    for vector in state.k:
        first = (vector >> first_index) & 1
        second = (vector >> second_index) & 1
        output_k.add(
            _compress_vector(
                vector,
                state.width,
                first_index,
                second_index,
                first | second,
            )
        )

    for vector in state.l:
        first = (vector >> first_index) & 1
        second = (vector >> second_index) & 1
        if first == second:
            output_l.add(
                _compress_vector(
                    vector,
                    state.width,
                    first_index,
                    second_index,
                    first,
                )
            )

    return BDPTState(
        width=state.width - 1,
        k=frozenset(output_k),
        l=frozenset(output_l),
    ).normalized()


def compress_xor(
    state: BDPTState, first_index: int, second_index: int
) -> BDPTState:
    """传播两个输入分量的 XOR 压缩。"""
    output_k: set[int] = set()
    output_l: set[int] = set()

    for vector in state.k:
        first = (vector >> first_index) & 1
        second = (vector >> second_index) & 1
        if first + second <= 1:
            output_k.add(
                _compress_vector(
                    vector,
                    state.width,
                    first_index,
                    second_index,
                    first + second,
                )
            )

    for vector in state.l:
        first = (vector >> first_index) & 1
        second = (vector >> second_index) & 1
        if first + second <= 1:
            output = _compress_vector(
                vector,
                state.width,
                first_index,
                second_index,
                first + second,
            )
            _toggle(output_l, output)

    return BDPTState(
        width=state.width - 1,
        k=frozenset(output_k),
        l=frozenset(output_l),
    ).normalized()


def xor_secret_key(state: BDPTState, index: int) -> BDPTState:
    """传播单个未知轮密钥比特与状态位的 XOR。"""
    bit_mask = unit_vector(index, state.width)
    output_k = set(state.k)
    for vector in state.l:
        if vector & bit_mask == 0:
            output_k.add(vector | bit_mask)
    return BDPTState(
        width=state.width,
        k=frozenset(output_k),
        l=state.l,
    ).normalized()


def propagate_sbox(
    state: BDPTState,
    truth_table: Sequence[int],
    output_width: int,
) -> BDPTState:
    """按主论文定理传播一个公开向量布尔函数。"""
    monomial_anfs = output_monomial_anfs(
        truth_table,
        input_width=state.width,
        output_width=output_width,
    )
    output_k: set[int] = set()
    output_l: set[int] = set()

    for output_exponent, input_terms in enumerate(monomial_anfs):
        if any(
            dominates(term, k)
            for term in input_terms
            for k in state.k
        ):
            output_k.add(output_exponent)

        for ell in state.l:
            if ell in input_terms:
                _toggle(output_l, output_exponent)

    return BDPTState(
        width=output_width,
        k=frozenset(output_k),
        l=frozenset(output_l),
    ).normalized()


def propagate_local_sbox(
    state: BDPTState,
    indices: Sequence[int],
    truth_table: Sequence[int],
) -> BDPTState:
    """在完整状态的指定分量上应用等宽公开向量函数。"""
    local_indices = tuple(indices)
    if not local_indices:
        raise ValueError("局部函数索引不能为空")
    if len(set(local_indices)) != len(local_indices):
        raise ValueError("局部函数索引不能重复")
    for index in local_indices:
        unit_vector(index, state.width)
    local_width = len(local_indices)

    output_k: set[int] = set()
    output_l: set[int] = set()
    for vector in state.k:
        local_input = extract_bits(vector, state.width, local_indices)
        local_state = BDPTState(
            width=local_width,
            k=frozenset({local_input}),
        )
        local_output = propagate_sbox(local_state, truth_table, local_width)
        output_k.update(
            replace_bits(vector, state.width, local_indices, local_vector)
            for local_vector in local_output.k
        )

    for vector in state.l:
        local_input = extract_bits(vector, state.width, local_indices)
        local_state = BDPTState(
            width=local_width,
            l=frozenset({local_input}),
        )
        local_output = propagate_sbox(local_state, truth_table, local_width)
        for local_vector in local_output.l:
            output_vector = replace_bits(
                vector,
                state.width,
                local_indices,
                local_vector,
            )
            _toggle(output_l, output_vector)

    return BDPTState(
        width=state.width,
        k=frozenset(output_k),
        l=frozenset(output_l),
    ).normalized()


def propagate_local_transform(
    state: BDPTState,
    indices: Sequence[int],
    transform: Callable[[BDPTState], BDPTState],
) -> BDPTState:
    """在指定分量上应用可改变内部维度但最终等宽的 BDPT 变换。"""
    local_indices = tuple(indices)
    if not local_indices:
        raise ValueError("局部变换索引不能为空")
    if len(set(local_indices)) != len(local_indices):
        raise ValueError("局部变换索引不能重复")
    for index in local_indices:
        unit_vector(index, state.width)
    local_width = len(local_indices)

    output_k: set[int] = set()
    output_l: set[int] = set()
    for vector in state.k:
        local_input = extract_bits(vector, state.width, local_indices)
        local_output = transform(
            BDPTState(width=local_width, k=frozenset({local_input}))
        )
        if local_output.width != local_width:
            raise ValueError("局部变换最终宽度与输入不一致")
        output_k.update(
            replace_bits(vector, state.width, local_indices, local_vector)
            for local_vector in local_output.k
        )

    for vector in state.l:
        local_input = extract_bits(vector, state.width, local_indices)
        local_output = transform(
            BDPTState(width=local_width, l=frozenset({local_input}))
        )
        if local_output.width != local_width:
            raise ValueError("局部变换最终宽度与输入不一致")
        output_k.update(
            replace_bits(vector, state.width, local_indices, local_vector)
            for local_vector in local_output.k
        )
        for local_vector in local_output.l:
            output_vector = replace_bits(
                vector, state.width, local_indices, local_vector
            )
            _toggle(output_l, output_vector)

    return BDPTState(
        width=state.width,
        k=frozenset(output_k),
        l=frozenset(output_l),
    ).normalized()


def permute_state(state: BDPTState, source_indices: Sequence[int]) -> BDPTState:
    """对 K、L 中的全部向量应用同一个公开位排列。"""
    permutation = tuple(source_indices)
    if len(permutation) != state.width:
        raise ValueError("排列宽度与 BDPT 状态不一致")
    return BDPTState(
        width=state.width,
        k=frozenset(
            permute_bits(vector, state.width, permutation) for vector in state.k
        ),
        l=frozenset(
            permute_bits(vector, state.width, permutation) for vector in state.l
        ),
    ).normalized()
