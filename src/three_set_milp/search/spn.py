"""PRESENT/RECTANGLE 的 Algorithm 2 局部序列与 Gurobi oracle。"""

from functools import partial
from typing import Literal

from three_set_milp.ciphers.spn import (
    SPNParameters,
    propagate_key_and_permutation,
    propagate_public_permutation,
    propagate_sbox_part,
)
from three_set_milp.core.propagation import xor_secret_key
from three_set_milp.milp.gurobi_backend import SolveStatus
from three_set_milp.milp.spn import SPNBoundary, SPNSuffixModel

from .bdpt_search import SearchPart


KeyBitOrder = Literal["ascending", "descending"]
KeyTreatment = Literal["paper", "ignore-rule4"]


def spn_search_parts(
    parameters: SPNParameters,
    rounds: int,
    *,
    key_treatment: KeyTreatment = "paper",
) -> tuple[SearchPart, ...]:
    """按每轮全部 S 盒和轮末置换/密钥步骤生成局部序列。

    ``ignore-rule4`` 仅用于定位论文 Table 5 差异，不属于主论文算法。
    """
    if rounds <= 0:
        raise ValueError("轮数必须为正数")
    if key_treatment == "paper":
        round_end_propagate = propagate_key_and_permutation
    elif key_treatment == "ignore-rule4":
        round_end_propagate = propagate_public_permutation
    else:
        raise ValueError("密钥处理方式只能是 paper 或 ignore-rule4")
    parts: list[SearchPart] = []
    sbox_count = len(parameters.sbox_groups)
    for round_index in range(rounds):
        for sbox_index in range(sbox_count):
            parts.append(
                SearchPart(
                    boundary=SPNBoundary(round_index, sbox_index),
                    propagate=partial(
                        propagate_sbox_part,
                        parameters=parameters,
                        sbox_index=sbox_index,
                    ),
                )
            )
        parts.append(
            SearchPart(
                boundary=SPNBoundary(round_index, sbox_count),
                propagate=partial(
                    round_end_propagate,
                    parameters=parameters,
                ),
            )
        )
    return tuple(parts)


def spn_k_bdpt_parts(
    parameters: SPNParameters,
    rounds: int,
    *,
    key_bit_order: KeyBitOrder = "ascending",
) -> tuple[SearchPart, ...]:
    """按后续论文 Algorithm 1 将每个轮密钥比特拆成独立局部函数。"""
    if rounds <= 0:
        raise ValueError("轮数必须为正数")
    if key_bit_order == "ascending":
        key_indices = range(parameters.block_size)
    elif key_bit_order == "descending":
        key_indices = range(parameters.block_size - 1, -1, -1)
    else:
        raise ValueError("轮密钥比特顺序只能是 ascending 或 descending")
    parts: list[SearchPart] = []
    sbox_count = len(parameters.sbox_groups)
    for round_index in range(rounds):
        for sbox_index in range(sbox_count):
            parts.append(
                SearchPart(
                    boundary=SPNBoundary(round_index, sbox_index),
                    propagate=partial(
                        propagate_sbox_part,
                        parameters=parameters,
                        sbox_index=sbox_index,
                    ),
                )
            )
        parts.append(
            SearchPart(
                boundary=SPNBoundary(round_index, sbox_count),
                propagate=partial(
                    propagate_public_permutation,
                    parameters=parameters,
                ),
            )
        )
        next_boundary = SPNBoundary(round_index + 1, 0)
        for key_index in key_indices:
            parts.append(
                SearchPart(
                    boundary=next_boundary,
                    propagate=partial(xor_secret_key, index=key_index),
                    secret_key_index=key_index,
                )
            )
    return tuple(parts)


class SPNGurobiOracle:
    """复用当前边界的 SPN 后缀模型，避免每次查询重新建模。"""

    def __init__(
        self,
        parameters: SPNParameters,
        rounds: int,
        *,
        time_limit: float | None = None,
        output_flag: bool = False,
    ) -> None:
        self.parameters = parameters
        self.rounds = rounds
        self.time_limit = time_limit
        self.output_flag = output_flag
        self._boundary: SPNBoundary | None = None
        self._model: SPNSuffixModel | None = None

    def __call__(self, boundary: object, vector: int, target_index: int) -> bool:
        if not isinstance(boundary, SPNBoundary):
            raise TypeError("SPN oracle 收到非 SPN 边界")
        if boundary != self._boundary:
            self._model = SPNSuffixModel(
                self.parameters,
                self.rounds,
                boundary,
                output_flag=self.output_flag,
            )
            self._boundary = boundary
        if self._model is None:
            raise RuntimeError("SPN 后缀模型初始化失败")
        status = self._model.check_trail(
            vector,
            target_index,
            time_limit=self.time_limit,
        )
        if status is SolveStatus.FEASIBLE:
            return True
        if status is SolveStatus.INFEASIBLE:
            return False
        raise RuntimeError("Gurobi 未证明可行或不可行，不能据此给出可分性结论")
