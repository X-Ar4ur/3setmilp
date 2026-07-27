"""LBlock 的 Algorithm 2 局部序列与 Gurobi oracle。"""

from functools import partial

from three_set_milp.ciphers.lblock import propagate_core, propagate_swap
from three_set_milp.milp.gurobi_backend import SolveStatus
from three_set_milp.milp.lblock import LBlockBoundary, LBlockSuffixModel

from .bdpt_search import SearchPart


def lblock_search_parts(rounds: int) -> tuple[SearchPart, ...]:
    """按每轮 8 个 keyed core 和轮末交换生成局部序列。"""
    if rounds <= 0:
        raise ValueError("轮数必须为正数")
    parts: list[SearchPart] = []
    for round_index in range(rounds):
        for sbox_index in range(8):
            parts.append(
                SearchPart(
                    boundary=LBlockBoundary(round_index, sbox_index),
                    propagate=partial(propagate_core, sbox_index=sbox_index),
                )
            )
        parts.append(
            SearchPart(
                boundary=LBlockBoundary(round_index, 8),
                propagate=propagate_swap,
            )
        )
    return tuple(parts)


class LBlockGurobiOracle:
    """复用当前边界的 LBlock 后缀模型。"""

    def __init__(
        self,
        rounds: int,
        *,
        time_limit: float | None = None,
        output_flag: bool = False,
    ) -> None:
        self.rounds = rounds
        self.time_limit = time_limit
        self.output_flag = output_flag
        self._boundary: LBlockBoundary | None = None
        self._model: LBlockSuffixModel | None = None

    def __call__(self, boundary: object, vector: int, target_index: int) -> bool:
        if not isinstance(boundary, LBlockBoundary):
            raise TypeError("LBlock oracle 收到非 LBlock 边界")
        if boundary != self._boundary:
            self._model = LBlockSuffixModel(
                self.rounds,
                boundary,
                output_flag=self.output_flag,
            )
            self._boundary = boundary
        if self._model is None:
            raise RuntimeError("LBlock 后缀模型初始化失败")
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
