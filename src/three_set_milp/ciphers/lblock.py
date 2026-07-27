"""LBlock 的轮函数、位序和精确局部 BDPT 传播。"""

from functools import partial

from three_set_milp.core.bdpt import BDPTState
from three_set_milp.core.bitvector import validate_vector, vector_mask
from three_set_milp.core.propagation import (
    compress_xor,
    copy_bit,
    permute_state,
    propagate_local_sbox,
    propagate_local_transform,
    xor_secret_key,
)


LBLOCK_SBOXES = (
    (14, 9, 15, 0, 13, 4, 10, 11, 1, 2, 8, 3, 7, 6, 12, 5),
    (4, 11, 14, 9, 15, 13, 0, 10, 7, 12, 5, 6, 2, 8, 1, 3),
    (1, 14, 7, 12, 15, 13, 0, 6, 11, 5, 9, 3, 2, 4, 8, 10),
    (7, 6, 8, 11, 0, 15, 3, 14, 9, 10, 12, 13, 5, 2, 4, 1),
    (14, 5, 15, 0, 7, 2, 12, 13, 1, 8, 4, 9, 11, 10, 6, 3),
    (2, 13, 11, 12, 15, 14, 0, 9, 7, 10, 6, 3, 1, 8, 4, 5),
    (11, 9, 4, 14, 0, 15, 10, 13, 6, 12, 5, 7, 3, 8, 1, 2),
    (13, 10, 15, 0, 14, 4, 9, 11, 2, 1, 8, 3, 7, 5, 12, 6),
)
LBLOCK_KEY_SBOX8 = (8, 7, 14, 5, 15, 13, 0, 6, 11, 12, 9, 10, 2, 4, 1, 3)
LBLOCK_KEY_SBOX9 = (11, 5, 15, 0, 7, 2, 9, 13, 4, 8, 1, 12, 14, 10, 3, 6)

# 输入 S_j 的结果写入输出 nibble P(j)。
LBLOCK_P = (2, 0, 3, 1, 6, 4, 7, 5)
LBLOCK_BLOCK_SIZE = 64
LBLOCK_HALF_SIZE = 32


def rotate_left(value: int, distance: int, width: int) -> int:
    """在固定字长内循环左移。"""
    validate_vector(value, width)
    distance %= width
    mask = vector_mask(width)
    return ((value << distance) | (value >> (width - distance))) & mask


def f_function(value: int, round_key: int) -> int:
    """计算 LBlock 的 32-bit F 函数。"""
    validate_vector(value, 32)
    validate_vector(round_key, 32)
    substituted = 0
    keyed = value ^ round_key
    for sbox_index, sbox in enumerate(LBLOCK_SBOXES):
        nibble = (keyed >> (4 * sbox_index)) & 0xF
        substituted |= sbox[nibble] << (4 * sbox_index)

    output = 0
    for input_nibble, output_nibble in enumerate(LBLOCK_P):
        nibble = (substituted >> (4 * input_nibble)) & 0xF
        output |= nibble << (4 * output_nibble)
    return output


def round_function(left: int, right: int, round_key: int) -> tuple[int, int]:
    """计算一轮 ``(X,Y) -> (F(X,K)+(Y<<<8),X)``。"""
    validate_vector(left, 32)
    validate_vector(right, 32)
    validate_vector(round_key, 32)
    return f_function(left, round_key) ^ rotate_left(right, 8, 32), left


def expand_round_keys(master_key: int) -> tuple[int, ...]:
    """按修订版规范生成 32 个 LBlock 轮密钥。"""
    validate_vector(master_key, 80)
    register = master_key
    keys = [register >> 48]
    mask = vector_mask(80)
    for round_index in range(1, 32):
        register = rotate_left(register, 29, 80)
        # 修订版 s8、s9 仅用于密钥编排，不参与数据轮函数。
        high_byte = (
            LBLOCK_KEY_SBOX9[(register >> 76) & 0xF] << 4
        ) | LBLOCK_KEY_SBOX8[(register >> 72) & 0xF]
        register &= ~(0xFF << 72)
        register |= high_byte << 72
        register ^= round_index << 46
        register &= mask
        keys.append(register >> 48)
    return tuple(keys)


def encrypt(plaintext: int, master_key: int) -> int:
    """计算 32 轮 LBlock，用官方测试向量校验实现方向。"""
    validate_vector(plaintext, 64)
    validate_vector(master_key, 80)
    left = plaintext >> 32
    right = plaintext & vector_mask(32)
    for round_key in expand_round_keys(master_key):
        left, right = round_function(left, right, round_key)
    # 规范测试向量在最后一轮后按 (Y, X) 输出，不再保留 Feistel 内部顺序。
    return (right << 32) | left


def _right_rotation_permutation() -> tuple[int, ...]:
    """保持左半不变，并将右半循环左移 8 bit。"""
    source = list(range(32))
    source.extend(32 + ((index - 8) % 32) for index in range(32))
    return tuple(source)


def _swap_permutation() -> tuple[int, ...]:
    return tuple(range(32, 64)) + tuple(range(32))


def _propagate_sbox_xor_local(
    state: BDPTState,
    sbox: tuple[int, ...],
    *,
    secret_key: bool,
) -> BDPTState:
    """传播局部 S 盒异或电路，局部位序为 x0..x3,y0..y3。"""
    if state.width != 8:
        raise ValueError("LBlock 局部核心必须是 8-bit 状态")
    labels = [f"x{index}" for index in range(4)] + [f"y{index}" for index in range(4)]
    current = state

    for bit_index in range(4):
        label = f"x{bit_index}"
        position = labels.index(label)
        current = copy_bit(current, position)
        labels[position : position + 1] = [label, f"w{bit_index}"]

    work_indices = tuple(labels.index(f"w{index}") for index in range(4))
    if secret_key:
        for index in work_indices:
            current = xor_secret_key(current, index)
    current = propagate_local_sbox(current, work_indices, sbox)

    for bit_index in range(4):
        work_position = labels.index(f"w{bit_index}")
        y_position = labels.index(f"y{bit_index}")
        lower = min(work_position, y_position)
        upper = max(work_position, y_position)
        current = compress_xor(current, work_position, y_position)
        labels[lower] = f"z{bit_index}"
        labels.pop(upper)

    desired = [f"x{index}" for index in range(4)] + [f"z{index}" for index in range(4)]
    source_indices = tuple(labels.index(label) for label in desired)
    return permute_state(current, source_indices)


def propagate_keyed_sbox_xor_local(
    state: BDPTState, sbox: tuple[int, ...]
) -> BDPTState:
    """传播局部 ``(x,y)->(x,S(x+k)+y)``。"""
    return _propagate_sbox_xor_local(state, sbox, secret_key=True)


def propagate_public_sbox_xor_local(
    state: BDPTState, sbox: tuple[int, ...]
) -> BDPTState:
    """传播 CBDP 使用的固定轮密钥局部核心。"""
    return _propagate_sbox_xor_local(state, sbox, secret_key=False)


def core_indices(sbox_index: int) -> tuple[int, ...]:
    """返回局部核心的 x nibble 与已旋转右半目标 nibble 索引。"""
    if sbox_index < 0 or sbox_index >= 8:
        raise IndexError("LBlock S 盒编号超出范围")
    destination = LBLOCK_P[sbox_index]
    x_indices = tuple(4 * sbox_index + bit for bit in range(4))
    y_indices = tuple(32 + 4 * destination + bit for bit in range(4))
    return x_indices + y_indices


def propagate_core(state: BDPTState, sbox_index: int) -> BDPTState:
    """传播一个带独立未知子密钥 nibble 的 LBlock 局部核心。"""
    if state.width != 64:
        raise ValueError("BDPT 状态宽度必须为 64")
    current = state
    if sbox_index == 0:
        current = permute_state(current, _right_rotation_permutation())
    return propagate_local_transform(
        current,
        core_indices(sbox_index),
        partial(propagate_keyed_sbox_xor_local, sbox=LBLOCK_SBOXES[sbox_index]),
    )


def propagate_public_core(state: BDPTState, sbox_index: int) -> BDPTState:
    """传播固定轮密钥下的一个 LBlock 局部核心。"""
    if state.width != 64:
        raise ValueError("BDPT 状态宽度必须为 64")
    current = state
    if sbox_index == 0:
        current = permute_state(current, _right_rotation_permutation())
    return propagate_local_transform(
        current,
        core_indices(sbox_index),
        partial(propagate_public_sbox_xor_local, sbox=LBLOCK_SBOXES[sbox_index]),
    )


def propagate_swap(state: BDPTState) -> BDPTState:
    """传播 LBlock 轮末左右半交换。"""
    if state.width != 64:
        raise ValueError("BDPT 状态宽度必须为 64")
    return permute_state(state, _swap_permutation())


def propagate_round(state: BDPTState) -> BDPTState:
    """按 8 个 keyed core 和轮末交换传播完整一轮。"""
    current = state
    for sbox_index in range(8):
        current = propagate_core(current, sbox_index)
    return propagate_swap(current)


def propagate_public_round(state: BDPTState) -> BDPTState:
    """传播 CBDP 使用的固定轮密钥完整一轮。"""
    current = state
    for sbox_index in range(8):
        current = propagate_public_core(current, sbox_index)
    return propagate_swap(current)


def active_indices_from_paper_pattern(pattern: str) -> frozenset[int]:
    """解析论文按 ``(x31..x0,y31..y0)`` 打印的 LBlock 输入模式。"""
    compact = "".join(char for char in pattern.lower() if char not in "()[], \t\r\n")
    if len(compact) != 64 or any(char not in "ac" for char in compact):
        raise ValueError("LBlock 输入模式长度或字符不合法")
    active: set[int] = set()
    for printed_index, char in enumerate(compact[:32]):
        if char == "a":
            active.add(31 - printed_index)
    for printed_index, char in enumerate(compact[32:]):
        if char == "a":
            active.add(63 - printed_index)
    return frozenset(active)


def format_paper_parities(parities: dict[int, str]) -> str:
    """按论文左右半和高位到低位顺序格式化输出三值结果。"""
    def symbol(index: int) -> str:
        return parities.get(index, "-")

    left = "".join(symbol(index) for index in reversed(range(32)))
    right = "".join(symbol(32 + index) for index in reversed(range(32)))
    return f"{left},{right}"
