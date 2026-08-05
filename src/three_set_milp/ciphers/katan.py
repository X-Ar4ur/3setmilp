"""KATAN/KTANTAN 轮函数及 K-BDPT 精确局部传播。"""

from dataclasses import dataclass

from three_set_milp.core.bdpt import BDPTState
from three_set_milp.core.bitvector import validate_vector, vector_mask
from three_set_milp.core.propagation import (
    permute_state,
    propagate_local_sbox,
    xor_secret_key,
)


def _xor_accumulate_table() -> tuple[int, ...]:
    """返回 ``(累加器,源位)->(累加器 xor 源位,源位)`` 真值表。"""
    return tuple(
        ((value & 1) ^ ((value >> 1) & 1))
        | (((value >> 1) & 1) << 1)
        for value in range(4)
    )


def _and_xor_accumulate_table() -> tuple[int, ...]:
    """返回 ``(累加器,a,b)->(累加器 xor (a and b),a,b)`` 真值表。"""
    return tuple(
        ((value & 1) ^ (((value >> 1) & 1) & ((value >> 2) & 1)))
        | (value & 0b110)
        for value in range(8)
    )


XOR_ACCUMULATE_TABLE = _xor_accumulate_table()
AND_XOR_ACCUMULATE_TABLE = _and_xor_accumulate_table()


# 原始 KATAN/KTANTAN 论文附录给出的 254 位不规则更新序列。
_IR_BITS = (
    "1111111000" "1101010101" "1110110011" "0010100100"
    "0100011000" "1111000010" "0001010000" "0111110011"
    "1111010100" "0101010011" "0000110011" "1011111011"
    "1010010101" "1010011100" "1101100010" "1110110111"
    "1001011011" "0101110010" "0100110100" "0111000100"
    "1111010000" "1110101100" "0001011001" "0000001101"
    "1100000001" "0010"
)
IR_SEQUENCE = tuple(int(bit) for bit in _IR_BITS)
if len(IR_SEQUENCE) != 254:
    raise RuntimeError("KATAN IR 序列长度必须为 254")


@dataclass(frozen=True, slots=True)
class KatanParameters:
    """一个 KATAN/KTANTAN 分组长度变体的公开参数。"""

    block_size: int
    l1_size: int
    l2_size: int
    x_taps: tuple[int, int, int, int, int]
    y_taps: tuple[int, int, int, int, int, int]
    clocks_per_round: int

    def __post_init__(self) -> None:
        if self.l1_size + self.l2_size != self.block_size:
            raise ValueError("KATAN 两个寄存器长度之和必须等于分组长度")
        if self.clocks_per_round not in (1, 2, 3):
            raise ValueError("KATAN 每轮时钟数只能为 1、2 或 3")
        if any(index < 0 or index >= self.l1_size for index in self.x_taps):
            raise ValueError("KATAN L1 抽头超出寄存器范围")
        if any(index < 0 or index >= self.l2_size for index in self.y_taps):
            raise ValueError("KATAN L2 抽头超出寄存器范围")
        if len(set(self.x_taps)) != len(self.x_taps):
            raise ValueError("KATAN L1 抽头必须互不重复")
        if len(set(self.y_taps)) != len(self.y_taps):
            raise ValueError("KATAN L2 抽头必须互不重复")
        if self.x_taps[0] != self.l1_size - 1:
            raise ValueError("KATAN x1 必须是 L1 移出的最高位")
        if self.y_taps[0] != self.l2_size - 1:
            raise ValueError("KATAN y1 必须是 L2 移出的最高位")

    @property
    def state_width(self) -> int:
        """反馈原位写入两个移出位，因此分析状态等于真实分组宽度。"""
        return self.block_size

    @property
    def fa_index(self) -> int:
        return self.x_taps[0]

    @property
    def fb_index(self) -> int:
        return self.l1_size + self.y_taps[0]

    @property
    def paper_print_indices(self) -> tuple[int, ...]:
        """论文依次打印 L2、L1，均为高索引到低索引。"""
        return tuple(reversed(range(self.block_size)))


KATAN32 = KatanParameters(
    block_size=32,
    l1_size=13,
    l2_size=19,
    x_taps=(12, 7, 8, 5, 3),
    y_taps=(18, 7, 12, 10, 8, 3),
    clocks_per_round=1,
)
KATAN48 = KatanParameters(
    block_size=48,
    l1_size=19,
    l2_size=29,
    x_taps=(18, 12, 15, 7, 6),
    y_taps=(28, 19, 21, 13, 15, 6),
    clocks_per_round=2,
)
KATAN64 = KatanParameters(
    block_size=64,
    l1_size=25,
    l2_size=39,
    x_taps=(24, 15, 20, 11, 9),
    y_taps=(38, 25, 33, 21, 14, 9),
    clocks_per_round=3,
)


def encode_state(l1: int, l2: int, parameters: KatanParameters) -> int:
    """把 L1 放在低位、L2 放在高位，匹配论文打印顺序。"""
    validate_vector(l1, parameters.l1_size)
    validate_vector(l2, parameters.l2_size)
    return l1 | (l2 << parameters.l1_size)


def decode_state(
    value: int, parameters: KatanParameters
) -> tuple[int, int]:
    """从真实分组状态中解码 L1 和 L2。"""
    validate_vector(value, parameters.block_size)
    l1_mask = vector_mask(parameters.l1_size)
    return value & l1_mask, value >> parameters.l1_size


def clock_function(
    l1: int,
    l2: int,
    key_a: int,
    key_b: int,
    ir: int,
    parameters: KatanParameters,
) -> tuple[int, int]:
    """执行一次 KATAN/KTANTAN 寄存器更新。"""
    validate_vector(l1, parameters.l1_size)
    validate_vector(l2, parameters.l2_size)
    if key_a not in (0, 1) or key_b not in (0, 1) or ir not in (0, 1):
        raise ValueError("KATAN 密钥位和 IR 只能取 0 或 1")
    x1, x2, x3, x4, x5 = parameters.x_taps
    y1, y2, y3, y4, y5, y6 = parameters.y_taps
    fa = (
        ((l1 >> x1) & 1)
        ^ ((l1 >> x2) & 1)
        ^ (((l1 >> x3) & 1) & ((l1 >> x4) & 1))
        ^ (((l1 >> x5) & 1) & ir)
        ^ key_a
    )
    fb = (
        ((l2 >> y1) & 1)
        ^ ((l2 >> y2) & 1)
        ^ (((l2 >> y3) & 1) & ((l2 >> y4) & 1))
        ^ (((l2 >> y5) & 1) & ((l2 >> y6) & 1))
        ^ key_b
    )
    next_l1 = ((l1 << 1) & vector_mask(parameters.l1_size)) | fb
    next_l2 = ((l2 << 1) & vector_mask(parameters.l2_size)) | fa
    return next_l1, next_l2


def ir_for_clock(parameters: KatanParameters, clock_index: int) -> int:
    """按同一轮的 1/2/3 次更新复用对应 IR。"""
    if clock_index < 0:
        raise ValueError("KATAN 时钟编号不能为负数")
    round_index = clock_index // parameters.clocks_per_round
    if round_index >= len(IR_SEQUENCE):
        raise ValueError("KATAN 时钟编号超过 254 轮规范")
    return IR_SEQUENCE[round_index]


def _l2_index(parameters: KatanParameters, local_index: int) -> int:
    return parameters.l1_size + local_index


def _xor_accumulator(
    state: BDPTState, accumulator: int, source: int
) -> BDPTState:
    return propagate_local_sbox(
        state,
        (accumulator, source),
        XOR_ACCUMULATE_TABLE,
    )


def _and_xor_accumulator(
    state: BDPTState, accumulator: int, first: int, second: int
) -> BDPTState:
    return propagate_local_sbox(
        state,
        (accumulator, first, second),
        AND_XOR_ACCUMULATE_TABLE,
    )


def propagate_public_feedback(
    state: BDPTState,
    parameters: KatanParameters,
    ir: int,
) -> BDPTState:
    """在两个即将移出的最高位中原位计算不含轮密钥的 fa 和 fb。"""
    if state.width != parameters.state_width:
        raise ValueError("BDPT 状态宽度与 KATAN 分析状态不一致")
    if ir not in (0, 1):
        raise ValueError("KATAN IR 只能取 0 或 1")
    fa = parameters.fa_index
    fb = parameters.fb_index
    _, x2, x3, x4, x5 = parameters.x_taps
    _, y2, y3, y4, y5, y6 = (
        _l2_index(parameters, index) for index in parameters.y_taps
    )

    # x1/y1 在本次移位后都会被丢弃，可安全复用为反馈累加器。
    current = _xor_accumulator(state, fa, x2)
    if ir:
        current = _xor_accumulator(current, fa, x5)
    current = _and_xor_accumulator(current, fa, x3, x4)

    current = _xor_accumulator(current, fb, y2)
    current = _and_xor_accumulator(current, fb, y3, y4)
    return _and_xor_accumulator(current, fb, y5, y6)


def shift_permutation(parameters: KatanParameters) -> tuple[int, ...]:
    """把存放在两个旧 MSB 中的反馈值送入两个寄存器的 LSB。"""
    source = [0] * parameters.state_width
    source[0] = parameters.fb_index
    for index in range(1, parameters.l1_size):
        source[index] = index - 1
    source[parameters.l1_size] = parameters.fa_index
    for index in range(parameters.l1_size + 1, parameters.block_size):
        source[index] = index - 1
    if sorted(source) != list(range(parameters.state_width)):
        raise RuntimeError("KATAN 扩展状态移位必须是一个排列")
    return tuple(source)


def propagate_shift(
    state: BDPTState, parameters: KatanParameters
) -> BDPTState:
    """完成两个反馈移位；该原位电路没有需要清零的辅助位。"""
    return permute_state(state, shift_permutation(parameters))


def propagate_clock_part(
    state: BDPTState,
    parameters: KatanParameters,
    clock_index: int,
    part_index: int,
    *,
    include_secret_key: bool = True,
) -> BDPTState:
    """传播时钟内的反馈、两个密钥 XOR 或移位步骤。"""
    if part_index == 0:
        return propagate_public_feedback(
            state,
            parameters,
            ir_for_clock(parameters, clock_index),
        )
    if part_index == 1:
        return (
            xor_secret_key(state, parameters.fa_index)
            if include_secret_key
            else state
        )
    if part_index == 2:
        return (
            xor_secret_key(state, parameters.fb_index)
            if include_secret_key
            else state
        )
    if part_index == 3:
        return propagate_shift(state, parameters)
    raise ValueError("KATAN 时钟局部函数编号只能为 0 到 3")


def propagate_clock(
    state: BDPTState,
    parameters: KatanParameters,
    clock_index: int,
    *,
    include_secret_key: bool = True,
) -> BDPTState:
    """按 Algorithm 1 使用的四个局部步骤传播一次时钟。"""
    current = state
    for part_index in range(4):
        current = propagate_clock_part(
            current,
            parameters,
            clock_index,
            part_index,
            include_secret_key=include_secret_key,
        )
    return current
