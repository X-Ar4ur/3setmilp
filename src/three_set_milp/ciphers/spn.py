"""PRESENT 与 RECTANGLE 共用的 4-bit SPN 描述和 BDPT 传播。"""

from dataclasses import dataclass

from three_set_milp.core.bdpt import BDPTState
from three_set_milp.core.propagation import (
    permute_state,
    propagate_local_sbox,
    xor_secret_key,
)


@dataclass(frozen=True, slots=True)
class SPNParameters:
    """由局部 S 盒分组和线性位排列定义的 SPN 轮函数。"""

    name: str
    block_size: int
    sbox_table: tuple[int, ...]
    sbox_groups: tuple[tuple[int, ...], ...]
    permutation: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.block_size <= 0:
            raise ValueError("分组长度必须为正数")
        if len(self.sbox_table) != 16 or sorted(self.sbox_table) != list(range(16)):
            raise ValueError("当前 SPN 实现要求 4-bit 双射 S 盒")
        if not self.sbox_groups:
            raise ValueError("S 盒分组不能为空")
        flattened = [index for group in self.sbox_groups for index in group]
        if any(len(group) != 4 for group in self.sbox_groups):
            raise ValueError("每个 S 盒必须恰好连接 4 个状态位")
        if sorted(flattened) != list(range(self.block_size)):
            raise ValueError("S 盒分组必须无重叠地覆盖整个状态")
        if sorted(self.permutation) != list(range(self.block_size)):
            raise ValueError("位排列必须恰好包含全部状态索引")

    @property
    def parts_per_round(self) -> int:
        """返回每轮的局部 S 盒数加轮末置换步骤。"""
        return len(self.sbox_groups) + 1


def propagate_sbox_part(
    state: BDPTState,
    parameters: SPNParameters,
    sbox_index: int,
) -> BDPTState:
    """精确传播一轮中的一个 4-bit S 盒。"""
    if state.width != parameters.block_size:
        raise ValueError("BDPT 状态宽度与 SPN 参数不一致")
    if sbox_index < 0 or sbox_index >= len(parameters.sbox_groups):
        raise IndexError("S 盒局部编号超出范围")
    return propagate_local_sbox(
        state,
        parameters.sbox_groups[sbox_index],
        parameters.sbox_table,
    )


def propagate_key_and_permutation(
    state: BDPTState,
    parameters: SPNParameters,
) -> BDPTState:
    """传播论文的轮末公开置换和独立未知轮密钥异或。"""
    if state.width != parameters.block_size:
        raise ValueError("BDPT 状态宽度与 SPN 参数不一致")
    current = permute_state(state, parameters.permutation)
    for index in range(parameters.block_size):
        current = xor_secret_key(current, index)
    return current


def propagate_public_permutation(
    state: BDPTState,
    parameters: SPNParameters,
) -> BDPTState:
    """CBDP 中轮密钥视为常量，因此只传播轮末位排列。"""
    if state.width != parameters.block_size:
        raise ValueError("BDPT 状态宽度与 SPN 参数不一致")
    return permute_state(state, parameters.permutation)


def propagate_round(state: BDPTState, parameters: SPNParameters) -> BDPTState:
    """按论文局部划分顺序传播一整轮 BDPT。"""
    current = state
    for sbox_index in range(len(parameters.sbox_groups)):
        current = propagate_sbox_part(current, parameters, sbox_index)
    return propagate_key_and_permutation(current, parameters)
