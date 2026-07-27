"""SIMON/SIMECK 的具体轮函数和精确局部 BDPT 传播。"""

from dataclasses import dataclass

from three_set_milp.core.bdpt import BDPTState
from three_set_milp.core.bitvector import (
    from_index_bits,
    to_index_bits,
    validate_vector,
    vector_mask,
)
from three_set_milp.core.propagation import (
    permute_state,
    propagate_local_sbox,
    xor_secret_key,
)


@dataclass(frozen=True, slots=True)
class SimonParameters:
    """SIMON 型轮函数参数。"""

    word_size: int
    and_rotations: tuple[int, int] = (1, 8)
    xor_rotation: int = 2

    def __post_init__(self) -> None:
        if self.word_size <= max(*self.and_rotations, self.xor_rotation):
            raise ValueError("字长必须大于全部旋转常数")

    @property
    def block_size(self) -> int:
        return 2 * self.word_size


SIMON32 = SimonParameters(word_size=16)
SIMON64 = SimonParameters(word_size=32)
SIMECK32 = SimonParameters(
    word_size=16,
    and_rotations=(0, 5),
    xor_rotation=1,
)


def rotate_left(value: int, distance: int, width: int) -> int:
    """在固定字长内循环左移。"""
    validate_vector(value, width)
    distance %= width
    mask = vector_mask(width)
    return ((value << distance) | (value >> (width - distance))) & mask


def round_function(
    left: int,
    right: int,
    round_key: int,
    parameters: SimonParameters,
) -> tuple[int, int]:
    """计算一轮 ``(L,R) -> (R+F(L)+K,L)``。"""
    width = parameters.word_size
    validate_vector(left, width)
    validate_vector(right, width)
    validate_vector(round_key, width)
    first, second = parameters.and_rotations
    nonlinear = rotate_left(left, first, width) & rotate_left(left, second, width)
    linear = rotate_left(left, parameters.xor_rotation, width)
    next_left = right ^ nonlinear ^ linear ^ round_key
    return next_left, left


def core_truth_table() -> tuple[int, ...]:
    """返回论文 4-bit 核心 ``(a,b,c,d)->(a,b,c,ab+c+d)``。"""
    table: list[int] = []
    for value in range(16):
        a, b, c, d = to_index_bits(value, 4)
        table.append(from_index_bits([a, b, c, (a & b) ^ c ^ d]))
    return tuple(table)


def core_indices(
    parameters: SimonParameters, output_index: int
) -> tuple[int, int, int, int]:
    """返回局部顺序 ``(x[j-r1],x[j-r2],x[j-r3],y[j])``。"""
    width = parameters.word_size
    if output_index < 0 or output_index >= width:
        raise IndexError("SIMON 核心输出索引超出字长")
    first, second = parameters.and_rotations
    return (
        (output_index - first) % width,
        (output_index - second) % width,
        (output_index - parameters.xor_rotation) % width,
        width + output_index,
    )


def propagate_core(
    state: BDPTState,
    parameters: SimonParameters,
    output_index: int,
) -> BDPTState:
    """精确传播论文中的一个局部核心操作 ``Q[i,j]``。"""
    if state.width != parameters.block_size:
        raise ValueError("BDPT 状态宽度与 SIMON 参数不一致")
    return propagate_local_sbox(
        state,
        core_indices(parameters, output_index),
        core_truth_table(),
    )


def propagate_key_and_swap(
    state: BDPTState, parameters: SimonParameters
) -> BDPTState:
    """传播独立未知轮密钥异或，并交换左右字。"""
    if state.width != parameters.block_size:
        raise ValueError("BDPT 状态宽度与 SIMON 参数不一致")
    current = state
    width = parameters.word_size
    for index in range(width, 2 * width):
        current = xor_secret_key(current, index)
    swap = tuple(range(width, 2 * width)) + tuple(range(width))
    return permute_state(current, swap)


def propagate_public_swap(
    state: BDPTState, parameters: SimonParameters
) -> BDPTState:
    """CBDP 中轮密钥是常量，只需执行轮末左右交换。"""
    if state.width != parameters.block_size:
        raise ValueError("BDPT 状态宽度与 SIMON 参数不一致")
    width = parameters.word_size
    swap = tuple(range(width, 2 * width)) + tuple(range(width))
    return permute_state(state, swap)


def propagate_round(
    state: BDPTState, parameters: SimonParameters
) -> BDPTState:
    """按论文局部划分传播完整一轮 BDPT。"""
    current = state
    for output_index in range(parameters.word_size):
        current = propagate_core(current, parameters, output_index)
    return propagate_key_and_swap(current, parameters)


def encode_state(left: int, right: int, parameters: SimonParameters) -> int:
    """将 ``(left,right)`` 编码为内部完整状态。"""
    width = parameters.word_size
    validate_vector(left, width)
    validate_vector(right, width)
    return left | (right << width)


def decode_state(value: int, parameters: SimonParameters) -> tuple[int, int]:
    """将内部完整状态解码为 ``(left,right)``。"""
    validate_vector(value, parameters.block_size)
    mask = vector_mask(parameters.word_size)
    return value & mask, value >> parameters.word_size


def parse_paper_state(bits: str, parameters: SimonParameters) -> int:
    """解析论文按 ``x[n-1]..x[0],y[n-1]..y[0]`` 打印的状态。"""
    compact = bits.replace(" ", "").replace(",", "")
    if len(compact) != parameters.block_size or any(
        char not in "01" for char in compact
    ):
        raise ValueError("论文状态字符串长度或字符不合法")
    width = parameters.word_size
    left = int(compact[:width], 2)
    right = int(compact[width:], 2)
    return encode_state(left, right, parameters)


def format_paper_state(value: int, parameters: SimonParameters) -> str:
    """按论文的左右字和高索引到低索引顺序打印状态。"""
    left, right = decode_state(value, parameters)
    width = parameters.word_size
    return f"{left:0{width}b}{right:0{width}b}"
