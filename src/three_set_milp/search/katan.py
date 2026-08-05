"""KATAN/KTANTAN 的 K-BDPT 局部序列与后缀 oracle。"""

from functools import partial

from three_set_milp.ciphers.katan import KatanParameters, propagate_clock_part
from three_set_milp.milp.gurobi_backend import SolveStatus
from three_set_milp.milp.katan import KatanBoundary, KatanSuffixModel

from .bdpt_search import SearchPart


def katan_search_parts(
    parameters: KatanParameters,
    total_clocks: int,
) -> tuple[SearchPart, ...]:
    """每个时钟拆为公开反馈、ka、kb 和寄存器移位四个步骤。"""
    if total_clocks <= 0:
        raise ValueError("KATAN 总时钟数必须为正数")
    parts: list[SearchPart] = []
    for clock_index in range(total_clocks):
        round_index = clock_index // parameters.clocks_per_round
        for part_index in range(4):
            boundary_part = 0 if part_index == 0 else 1
            destination = None
            label = None
            if part_index == 1:
                destination = parameters.fa_index
                label = f"ka^{round_index}"
            elif part_index == 2:
                destination = parameters.fb_index
                label = f"kb^{round_index}"
            parts.append(
                SearchPart(
                    # 两个密钥 XOR 对 CBDP 都是恒等，移位前的三个边界等价。
                    boundary=KatanBoundary(clock_index, boundary_part),
                    propagate=partial(
                        propagate_clock_part,
                        parameters=parameters,
                        clock_index=clock_index,
                        part_index=part_index,
                    ),
                    secret_key_index=destination,
                    secret_key_label=label,
                )
            )
    return tuple(parts)


class KatanGurobiOracle:
    """复用当前 KATAN 边界的 CBDP 后缀模型。"""

    def __init__(
        self,
        parameters: KatanParameters,
        total_clocks: int,
        *,
        time_limit: float | None = None,
        output_flag: bool = False,
    ) -> None:
        self.parameters = parameters
        self.total_clocks = total_clocks
        self.time_limit = time_limit
        self.output_flag = output_flag
        self._boundary: KatanBoundary | None = None
        self._model: KatanSuffixModel | None = None

    def __call__(self, boundary: object, vector: int, target_index: int) -> bool:
        if not isinstance(boundary, KatanBoundary):
            raise TypeError("KATAN oracle 收到非 KATAN 边界")
        canonical = (
            KatanBoundary(boundary.clock_index, 1)
            if boundary.part_index > 0
            else boundary
        )
        if canonical != self._boundary:
            self._model = KatanSuffixModel(
                self.parameters,
                self.total_clocks,
                canonical,
                output_flag=self.output_flag,
            )
            self._boundary = canonical
        if self._model is None:
            raise RuntimeError("KATAN 后缀模型初始化失败")
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
