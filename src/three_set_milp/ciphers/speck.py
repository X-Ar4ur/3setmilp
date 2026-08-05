"""SPECK 数据路径及 K-BDPT 所需的精确局部传播。"""

from dataclasses import dataclass

from three_set_milp.core.bdpt import BDPTState
from three_set_milp.core.bitvector import validate_vector, vector_mask
from three_set_milp.core.propagation import (
    permute_state,
    propagate_local_sbox,
    xor_secret_key,
)


def _full_adder_table() -> tuple[int, ...]:
    """返回 ``(x,y,c)->(x+y+c 的和位,y,进位)`` 真值表。"""
    outputs: list[int] = []
    for value in range(8):
        x = value & 1
        y = (value >> 1) & 1
        carry = (value >> 2) & 1
        total = x + y + carry
        outputs.append((total & 1) | (y << 1) | ((total >> 1) << 2))
    return tuple(outputs)


def _xor_into_second_table() -> tuple[int, ...]:
    """返回 ``(x,y)->(x,x xor y)`` 真值表。"""
    return tuple(
        (value & 1) | ((((value & 1) ^ ((value >> 1) & 1))) << 1)
        for value in range(4)
    )


FULL_ADDER_TABLE = _full_adder_table()
XOR_INTO_SECOND_TABLE = _xor_into_second_table()
ZERO_BIT_TABLE = (0, 0)


@dataclass(frozen=True, slots=True)
class SpeckParameters:
    """论文涉及的 SPECK2n 轮函数参数。"""

    word_size: int
    alpha: int
    beta: int

    def __post_init__(self) -> None:
        if self.word_size <= 1:
            raise ValueError("SPECK 字长必须大于 1")
        if not 0 < self.alpha < self.word_size:
            raise ValueError("SPECK 右旋常数超出字长")
        if not 0 < self.beta < self.word_size:
            raise ValueError("SPECK 左旋常数超出字长")

    @property
    def block_size(self) -> int:
        return 2 * self.word_size

    @property
    def state_width(self) -> int:
        """分析状态额外保留一个模加进位辅助位。"""
        return self.block_size + 1

    @property
    def carry_index(self) -> int:
        return self.block_size

    @property
    def parts_per_round(self) -> int:
        """旋转、n 个加法位、n 个密钥位、旋转、n 个 XOR 位和清进位。"""
        return 3 * self.word_size + 3

    @property
    def paper_print_indices(self) -> tuple[int, ...]:
        """论文按第一字、第二字且各自从高位到低位打印。"""
        return tuple(reversed(range(self.block_size)))


SPECK32 = SpeckParameters(word_size=16, alpha=7, beta=2)
SPECK48 = SpeckParameters(word_size=24, alpha=8, beta=3)
SPECK64 = SpeckParameters(word_size=32, alpha=8, beta=3)
SPECK96 = SpeckParameters(word_size=48, alpha=8, beta=3)
SPECK128 = SpeckParameters(word_size=64, alpha=8, beta=3)


def rotate_left(value: int, distance: int, width: int) -> int:
    """在固定字长内循环左移。"""
    validate_vector(value, width)
    distance %= width
    mask = vector_mask(width)
    return ((value << distance) | (value >> (width - distance))) & mask


def rotate_right(value: int, distance: int, width: int) -> int:
    """在固定字长内循环右移。"""
    return rotate_left(value, width - (distance % width), width)


def round_function(
    first: int,
    second: int,
    round_key: int,
    parameters: SpeckParameters,
) -> tuple[int, int]:
    """计算标准 SPECK 轮 ``x=ROR(x)+y; x^=k; y=ROL(y)^x``。"""
    width = parameters.word_size
    validate_vector(first, width)
    validate_vector(second, width)
    validate_vector(round_key, width)
    mask = vector_mask(width)
    next_first = (
        rotate_right(first, parameters.alpha, width) + second
    ) & mask
    next_first ^= round_key
    next_second = rotate_left(second, parameters.beta, width) ^ next_first
    return next_first, next_second


def encode_state(
    first: int, second: int, parameters: SpeckParameters
) -> int:
    """将论文中的第一字放在高半、第二字放在低半。"""
    width = parameters.word_size
    validate_vector(first, width)
    validate_vector(second, width)
    return (first << width) | second


def decode_state(
    value: int, parameters: SpeckParameters
) -> tuple[int, int]:
    """将不含辅助位的分组状态解码为两个字。"""
    validate_vector(value, parameters.block_size)
    mask = vector_mask(parameters.word_size)
    return value >> parameters.word_size, value & mask


def classify_part(
    parameters: SpeckParameters, part_index: int
) -> tuple[str, int | None]:
    """把轮内局部编号映射为操作种类和字内比特编号。"""
    width = parameters.word_size
    if part_index < 0 or part_index >= parameters.parts_per_round:
        raise ValueError("SPECK 局部函数编号超出范围")
    if part_index == 0:
        return "rotate_first", None
    if part_index <= width:
        return "add", part_index - 1
    if part_index <= 2 * width:
        return "key", part_index - width - 1
    if part_index == 2 * width + 1:
        return "rotate_second", None
    if part_index <= 3 * width + 1:
        return "xor", part_index - 2 * width - 2
    return "clear_carry", None


def first_rotation_permutation(
    parameters: SpeckParameters,
) -> tuple[int, ...]:
    """返回第一字循环右移对应的输出到输入索引排列。"""
    width = parameters.word_size
    source = list(range(parameters.state_width))
    for index in range(width):
        source[width + index] = width + (index + parameters.alpha) % width
    return tuple(source)


def second_rotation_permutation(
    parameters: SpeckParameters,
) -> tuple[int, ...]:
    """返回第二字循环左移对应的输出到输入索引排列。"""
    width = parameters.word_size
    source = list(range(parameters.state_width))
    for index in range(width):
        source[index] = (index - parameters.beta) % width
    return tuple(source)


def propagate_part(
    state: BDPTState,
    parameters: SpeckParameters,
    part_index: int,
    *,
    include_secret_key: bool = True,
) -> BDPTState:
    """精确传播一项 SPECK 局部操作。"""
    if state.width != parameters.state_width:
        raise ValueError("BDPT 状态宽度与 SPECK 分析状态不一致")
    operation, bit_index = classify_part(parameters, part_index)
    width = parameters.word_size
    if operation == "rotate_first":
        return permute_state(state, first_rotation_permutation(parameters))
    if operation == "add":
        if bit_index is None:
            raise RuntimeError("模加局部操作缺少比特编号")
        return propagate_local_sbox(
            state,
            (width + bit_index, bit_index, parameters.carry_index),
            FULL_ADDER_TABLE,
        )
    if operation == "key":
        if bit_index is None:
            raise RuntimeError("密钥局部操作缺少比特编号")
        if not include_secret_key:
            return state
        return xor_secret_key(state, width + bit_index)
    if operation == "rotate_second":
        return permute_state(state, second_rotation_permutation(parameters))
    if operation == "xor":
        if bit_index is None:
            raise RuntimeError("XOR 局部操作缺少比特编号")
        return propagate_local_sbox(
            state,
            (width + bit_index, bit_index),
            XOR_INTO_SECOND_TABLE,
        )
    return propagate_local_sbox(
        state,
        (parameters.carry_index,),
        ZERO_BIT_TABLE,
    )


def propagate_round(
    state: BDPTState,
    parameters: SpeckParameters,
    *,
    include_secret_key: bool = True,
) -> BDPTState:
    """按固定局部顺序传播一轮 SPECK。"""
    current = state
    for part_index in range(parameters.parts_per_round):
        current = propagate_part(
            current,
            parameters,
            part_index,
            include_secret_key=include_secret_key,
        )
    return current
