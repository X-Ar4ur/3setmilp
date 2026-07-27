"""PRESENT/RECTANGLE 的 Algorithm 2 局部序列与 Gurobi oracle。"""

from functools import partial

from three_set_milp.ciphers.spn import (
    SPNParameters,
    propagate_key_and_permutation,
    propagate_sbox_part,
)
from three_set_milp.milp.gurobi_backend import SolveStatus
from three_set_milp.milp.spn import SPNBoundary, SPNSuffixModel

from .bdpt_search import SearchPart


def spn_search_parts(
    parameters: SPNParameters, rounds: int
) -> tuple[SearchPart, ...]:
    """按每轮全部 S 盒和轮末置换/密钥步骤生成局部序列。"""
    if rounds <= 0:
        raise ValueError("轮数必须为正数")
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
                    propagate_key_and_permutation,
                    parameters=parameters,
                ),
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
