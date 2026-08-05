"""KATAN/KTANTAN 的精确 CBDP 后缀 MILP。"""

from dataclasses import dataclass
from typing import Any

from three_set_milp.ciphers.katan import (
    AND_XOR_ACCUMULATE_TABLE,
    IR_SEQUENCE,
    XOR_ACCUMULATE_TABLE,
    KatanParameters,
    ir_for_clock,
    shift_permutation,
)
from three_set_milp.core.bitvector import unit_vector, validate_vector

from .gurobi_backend import GurobiModel, SolveStatus


@dataclass(frozen=True, slots=True)
class KatanBoundary:
    """KATAN 时钟内局部函数的输入边界。"""

    clock_index: int
    part_index: int

    def validate(self, total_clocks: int) -> None:
        if total_clocks <= 0:
            raise ValueError("KATAN 总时钟数必须为正数")
        if self.clock_index < 0 or self.clock_index > total_clocks:
            raise ValueError("KATAN 起始时钟超出目标范围")
        if self.clock_index == total_clocks:
            if self.part_index != 0:
                raise ValueError("KATAN 最终边界的局部编号必须为 0")
            return
        if self.part_index < 0 or self.part_index > 3:
            raise ValueError("KATAN 局部函数编号只能为 0 到 3")


def _add_local_transform(
    backend: GurobiModel,
    state: tuple[Any, ...],
    indices: tuple[int, ...],
    truth_table: tuple[int, ...],
    *,
    name: str,
) -> tuple[Any, ...]:
    """添加固定索引上的等宽小型布尔函数。"""
    output = backend.add_binary_vector(f"{name}_out", len(indices))
    backend.add_sbox(
        tuple(state[index] for index in indices),
        output,
        truth_table,
        name=name,
    )
    current = list(state)
    for local_index, state_index in enumerate(indices):
        current[state_index] = output[local_index]
    return tuple(current)


def _add_xor_accumulator(
    backend: GurobiModel,
    state: tuple[Any, ...],
    accumulator: int,
    source: int,
    *,
    name: str,
) -> tuple[Any, ...]:
    return _add_local_transform(
        backend,
        state,
        (accumulator, source),
        XOR_ACCUMULATE_TABLE,
        name=name,
    )


def _add_and_xor_accumulator(
    backend: GurobiModel,
    state: tuple[Any, ...],
    accumulator: int,
    first: int,
    second: int,
    *,
    name: str,
) -> tuple[Any, ...]:
    return _add_local_transform(
        backend,
        state,
        (accumulator, first, second),
        AND_XOR_ACCUMULATE_TABLE,
        name=name,
    )


def add_feedback_constraints(
    backend: GurobiModel,
    input_state: tuple[Any, ...],
    parameters: KatanParameters,
    *,
    clock_index: int,
) -> tuple[Any, ...]:
    """用 2/3 bit 精确 transition 在两个旧 MSB 中构造 fa、fb。"""
    if len(input_state) != parameters.state_width:
        raise ValueError("KATAN MILP 输入状态宽度不正确")
    prefix = f"c{clock_index}_feedback"
    fa = parameters.fa_index
    fb = parameters.fb_index
    _, x2, x3, x4, x5 = parameters.x_taps
    _, y2, y3, y4, y5, y6 = (
        parameters.l1_size + index for index in parameters.y_taps
    )
    current = _add_xor_accumulator(
        backend, input_state, fa, x2, name=f"{prefix}_fa_x2"
    )
    if ir_for_clock(parameters, clock_index):
        current = _add_xor_accumulator(
            backend, current, fa, x5, name=f"{prefix}_fa_ir"
        )
    current = _add_and_xor_accumulator(
        backend,
        current,
        fa,
        x3,
        x4,
        name=f"{prefix}_fa_and",
    )

    current = _add_xor_accumulator(
        backend, current, fb, y2, name=f"{prefix}_fb_y2"
    )
    current = _add_and_xor_accumulator(
        backend,
        current,
        fb,
        y3,
        y4,
        name=f"{prefix}_fb_and1",
    )
    return _add_and_xor_accumulator(
        backend,
        current,
        fb,
        y5,
        y6,
        name=f"{prefix}_fb_and2",
    )


def add_shift_constraints(
    input_state: tuple[Any, ...],
    parameters: KatanParameters,
) -> tuple[Any, ...]:
    """把两个旧 MSB 中的反馈值移入相反寄存器的 LSB。"""
    return tuple(
        input_state[index] for index in shift_permutation(parameters)
    )


def add_clock_constraints(
    backend: GurobiModel,
    input_state: tuple[Any, ...],
    parameters: KatanParameters,
    *,
    clock_index: int,
    start_part: int = 0,
) -> tuple[Any, ...]:
    """添加一个时钟或其后半部分的 KATAN CBDP 约束。"""
    if start_part < 0 or start_part > 3:
        raise ValueError("KATAN 部分时钟起始编号只能为 0 到 3")
    current = input_state
    if start_part <= 0:
        current = add_feedback_constraints(
            backend,
            current,
            parameters,
            clock_index=clock_index,
        )
    # part 1/2 是常量密钥 XOR，对 CBDP transition 均为恒等。
    current = add_shift_constraints(
        current,
        parameters,
    )
    return current


class KatanSuffixModel:
    """从任意 KATAN 局部边界到最终输出的可复用 CBDP 模型。"""

    def __init__(
        self,
        parameters: KatanParameters,
        total_clocks: int,
        boundary: KatanBoundary,
        *,
        output_flag: bool = False,
    ) -> None:
        boundary.validate(total_clocks)
        last_round = (total_clocks - 1) // parameters.clocks_per_round
        if last_round >= len(IR_SEQUENCE):
            raise ValueError("KATAN 实验超过规范的 254 轮")
        self.parameters = parameters
        self.total_clocks = total_clocks
        self.boundary = boundary
        self.backend = GurobiModel(
            f"katan_{parameters.block_size}_{total_clocks}_"
            f"{boundary.clock_index}_{boundary.part_index}",
            output_flag=output_flag,
        )
        self.input_variables = self.backend.add_binary_vector(
            "suffix_input", parameters.state_width
        )
        current = self.input_variables
        for clock_index in range(boundary.clock_index, total_clocks):
            start_part = (
                boundary.part_index
                if clock_index == boundary.clock_index
                else 0
            )
            current = add_clock_constraints(
                self.backend,
                current,
                parameters,
                clock_index=clock_index,
                start_part=start_part,
            )
        self.output_variables = current
        self._input_fixer = self.backend.add_vector_fixer(
            self.input_variables, name="suffix_input_fix"
        )
        self._output_fixer = self.backend.add_vector_fixer(
            self.output_variables, name="suffix_output_fix"
        )
        self.backend.model.update()

    def check_trail(
        self,
        input_vector: int,
        target_index: int,
        *,
        time_limit: float | None = None,
    ) -> SolveStatus:
        """固定扩展输入和真实分组输出单位向量，判断可达性。"""
        validate_vector(input_vector, self.parameters.state_width)
        if target_index < 0 or target_index >= self.parameters.block_size:
            raise ValueError("KATAN 目标位超出分组范围")
        target = unit_vector(target_index, self.parameters.state_width)
        self.backend.set_vector_fixer(self._input_fixer, input_vector)
        self.backend.set_vector_fixer(self._output_fixer, target)
        return self.backend.solve(time_limit=time_limit)
