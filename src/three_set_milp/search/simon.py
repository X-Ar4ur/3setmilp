"""SIMON 的 Algorithm 2 局部序列与 Gurobi 后缀 oracle。"""

from functools import partial

from three_set_milp.ciphers.simon import (
    SimonParameters,
    propagate_core,
    propagate_key_and_swap,
)
from three_set_milp.core.bdpt import BDPTState
from three_set_milp.milp.gurobi_backend import SolveStatus
from three_set_milp.milp.simon import SimonBoundary, SimonSuffixModel

from .bdpt_search import SearchPart


def simon_search_parts(
    parameters: SimonParameters, rounds: int
) -> tuple[SearchPart, ...]:
    """按论文顺序生成每轮 ``n`` 个核心和一个密钥交换步骤。"""
    if rounds <= 0:
        raise ValueError("轮数必须为正数")
    parts: list[SearchPart] = []
    for round_index in range(rounds):
        for part_index in range(parameters.word_size):
            parts.append(
                SearchPart(
                    boundary=SimonBoundary(round_index, part_index),
                    propagate=partial(
                        propagate_core,
                        parameters=parameters,
                        output_index=part_index,
                    ),
                )
            )
        parts.append(
            SearchPart(
                boundary=SimonBoundary(round_index, parameters.word_size),
                propagate=partial(
                    propagate_key_and_swap,
                    parameters=parameters,
                ),
            )
        )
    return tuple(parts)


class SimonGurobiOracle:
    """将 Gurobi 三态求解结果转换为 Algorithm 2 所需的布尔可达性。"""

    def __init__(
        self,
        parameters: SimonParameters,
        rounds: int,
        *,
        time_limit: float | None = None,
        output_flag: bool = False,
    ) -> None:
        self.parameters = parameters
        self.rounds = rounds
        self.time_limit = time_limit
        self.output_flag = output_flag
        self._boundary: SimonBoundary | None = None
        self._model: SimonSuffixModel | None = None

    def __call__(
        self, boundary: object, vector: int, target_index: int
    ) -> bool:
        if not isinstance(boundary, SimonBoundary):
            raise TypeError("SIMON oracle 收到非 SIMON 边界")
        if boundary != self._boundary:
            self._model = SimonSuffixModel(
                self.parameters,
                self.rounds,
                boundary,
                output_flag=self.output_flag,
            )
            self._boundary = boundary
        if self._model is None:
            raise RuntimeError("SIMON 后缀模型初始化失败")
        status = self._model.check_trail(
            vector,
            target_index,
            time_limit=self.time_limit,
        )
        if status is SolveStatus.FEASIBLE:
            return True
        if status is SolveStatus.INFEASIBLE:
            return False
        raise RuntimeError(
            "Gurobi 未证明可行或不可行，不能据此给出可分性结论"
        )
