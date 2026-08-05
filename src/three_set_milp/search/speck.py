"""SPECK 的 K-BDPT 局部序列与 Gurobi 后缀 oracle。"""

from functools import partial

from three_set_milp.ciphers.speck import (
    SpeckParameters,
    classify_part,
    propagate_part,
)
from three_set_milp.milp.gurobi_backend import SolveStatus
from three_set_milp.milp.speck import SpeckBoundary, SpeckSuffixModel

from .bdpt_search import SearchPart


def speck_search_parts(
    parameters: SpeckParameters,
    rounds: int,
) -> tuple[SearchPart, ...]:
    """按轮函数真实顺序生成公开操作和标量轮密钥 XOR。"""
    if rounds <= 0:
        raise ValueError("轮数必须为正数")
    parts: list[SearchPart] = []
    for round_index in range(rounds):
        for part_index in range(parameters.parts_per_round):
            operation, bit_index = classify_part(parameters, part_index)
            boundary_part = (
                parameters.word_size + 1
                if operation in {"key", "rotate_second"}
                else part_index
            )
            destination = (
                parameters.word_size + bit_index
                if operation == "key" and bit_index is not None
                else None
            )
            label = (
                f"k^{round_index}_{bit_index}"
                if destination is not None
                else None
            )
            parts.append(
                SearchPart(
                    # 连续密钥 XOR 在 CBDP 中均为恒等，后续旋转前的边界也等价。
                    boundary=SpeckBoundary(round_index, boundary_part),
                    propagate=partial(
                        propagate_part,
                        parameters=parameters,
                        part_index=part_index,
                    ),
                    secret_key_index=destination,
                    secret_key_label=label,
                )
            )
    return tuple(parts)


class SpeckGurobiOracle:
    """复用当前 SPECK 边界的后缀模型。"""

    def __init__(
        self,
        parameters: SpeckParameters,
        rounds: int,
        *,
        time_limit: float | None = None,
        output_flag: bool = False,
    ) -> None:
        self.parameters = parameters
        self.rounds = rounds
        self.time_limit = time_limit
        self.output_flag = output_flag
        self._boundary: SpeckBoundary | None = None
        self._model: SpeckSuffixModel | None = None

    def __call__(self, boundary: object, vector: int, target_index: int) -> bool:
        if not isinstance(boundary, SpeckBoundary):
            raise TypeError("SPECK oracle 收到非 SPECK 边界")
        canonical = boundary
        first_key = self.parameters.word_size + 1
        last_key = 2 * self.parameters.word_size
        if first_key <= boundary.part_index <= last_key + 1:
            canonical = SpeckBoundary(boundary.round_index, first_key)
        if canonical != self._boundary:
            self._model = SpeckSuffixModel(
                self.parameters,
                self.rounds,
                canonical,
                output_flag=self.output_flag,
            )
            self._boundary = canonical
        if self._model is None:
            raise RuntimeError("SPECK 后缀模型初始化失败")
        status = self._model.check_trail(
            vector,
            target_index,
            time_limit=self.time_limit,
        )
        if status is SolveStatus.FEASIBLE:
            return True
        if status is SolveStatus.INFEASIBLE:
            return False
        raise RuntimeError("Gurobi 未证明可行或不可行，不能给出可分性结论")
