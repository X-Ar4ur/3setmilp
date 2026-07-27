from itertools import product

from three_set_milp.ciphers.simon import (
    SIMON32,
    decode_state,
    encode_state,
    propagate_core,
    propagate_public_swap,
)
from three_set_milp.core.bdpt import BDPTState
from three_set_milp.core.order import reduce_k


def _enumerate_compact_round_outputs(
    input_vector: int, start_part: int
) -> frozenset[int]:
    """直接枚举 L1--L4 的稀疏分支分配，不调用 Gurobi。"""
    width = SIMON32.word_size
    input_left, input_right = decode_state(input_vector, SIMON32)
    active_left = [index for index in range(width) if input_left & (1 << index)]
    if len(active_left) > 6:
        raise ValueError("该测试 oracle 只用于稀疏输入")

    outputs: set[int] = set()
    # 每个活动 a_j 按 L1 恰好分配到 u、v、w、b_next 中的一条分支。
    for allocation in product(range(4), repeat=len(active_left)):
        u = v = w = output_right = 0
        for index, branch in zip(active_left, allocation, strict=True):
            if branch == 0:
                u |= 1 << index
            elif branch == 1:
                v |= 1 << index
            elif branch == 2:
                w |= 1 << index
            else:
                output_right |= 1 << index

        output_left = 0
        valid = True
        for index in range(width):
            first = (u >> ((index - 1) % width)) & 1
            second = (v >> ((index - 8) % width)) & 1
            and_bit = first | second
            linear_bit = (w >> ((index - 2) % width)) & 1
            right_bit = (input_right >> index) & 1
            xor_sum = right_bit + and_bit + linear_bit
            # L3 是整数等式，多个活动输入不能同时汇入同一 XOR 输出。
            if xor_sum > 1:
                valid = False
                break
            if xor_sum:
                output_left |= 1 << index
            if index < start_part and xor_sum != right_bit:
                valid = False
                break

        if valid:
            outputs.add(encode_state(output_left, output_right, SIMON32))
    return reduce_k(outputs, SIMON32.block_size)


def _exact_partial_round(input_state: BDPTState, start_part: int) -> BDPTState:
    current = input_state
    for output_index in range(start_part, SIMON32.word_size):
        current = propagate_core(current, SIMON32, output_index)
    return propagate_public_swap(current, SIMON32)


def test_compact_full_round_equations_match_exact_local_propagation() -> None:
    for input_vector in (1, 1 << 16, (1 << 0) | (1 << 5)):
        expected = _exact_partial_round(
            BDPTState(width=32, k=frozenset({input_vector})),
            start_part=0,
        )
        observed = _enumerate_compact_round_outputs(input_vector, start_part=0)
        assert observed == expected.k


def test_l4_partial_round_equations_match_remaining_local_operations() -> None:
    initial = BDPTState(width=32, k=frozenset({1}))
    intermediate = initial
    start_part = 8
    for output_index in range(start_part):
        intermediate = propagate_core(intermediate, SIMON32, output_index)

    observed_outputs: set[int] = set()
    for vector in intermediate.k:
        observed_outputs.update(
            _enumerate_compact_round_outputs(vector, start_part=start_part)
        )
    observed = reduce_k(observed_outputs, 32)
    expected = _exact_partial_round(intermediate, start_part)
    assert observed == expected.k

