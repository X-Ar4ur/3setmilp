"""PRESENT/RECTANGLE 共用的精确 CBDP 后缀 MILP。"""

from dataclasses import dataclass
from typing import Any

from three_set_milp.ciphers.spn import SPNParameters
from three_set_milp.core.bitvector import unit_vector, validate_vector

from .gurobi_backend import GurobiModel, SolveStatus


@dataclass(frozen=True, slots=True)
class SPNBoundary:
    """SPN 局部函数的输入边界，编号均从 0 开始。"""

    round_index: int
    part_index: int

    def validate(self, parameters: SPNParameters, rounds: int) -> None:
        if rounds <= 0:
            raise ValueError("轮数必须为正数")
        if self.round_index < 0 or self.round_index >= rounds:
            raise ValueError("起始轮超出目标密码轮数")
        if self.part_index < 0 or self.part_index > len(parameters.sbox_groups):
            raise ValueError("SPN 局部函数编号超出范围")


def add_round_constraints(
    backend: GurobiModel,
    input_state: tuple[Any, ...],
    parameters: SPNParameters,
    *,
    round_index: int,
    start_part: int = 0,
) -> tuple[Any, ...]:
    """添加一轮或首轮剩余 S 盒的精确 CBDP 约束。"""
    if len(input_state) != parameters.block_size:
        raise ValueError("SPN MILP 输入状态宽度不正确")
    if start_part < 0 or start_part > len(parameters.sbox_groups):
        raise ValueError("部分轮起始编号超出范围")

    current = list(input_state)
    for sbox_index in range(start_part, len(parameters.sbox_groups)):
        group = parameters.sbox_groups[sbox_index]
        output = backend.add_binary_vector(
            f"r{round_index}_s{sbox_index}_out", 4
        )
        backend.add_sbox(
            tuple(current[index] for index in group),
            output,
            parameters.sbox_table,
            name=f"r{round_index}_s{sbox_index}",
        )
        for local_index, state_index in enumerate(group):
            current[state_index] = output[local_index]

    # 公开轮密钥不改变 CBDP trail，位排列只需重排变量引用。
    return tuple(current[input_index] for input_index in parameters.permutation)


class SPNSuffixModel:
    """从任意 SPN 局部边界到最终输出的可复用 CBDP 模型。"""

    def __init__(
        self,
        parameters: SPNParameters,
        rounds: int,
        boundary: SPNBoundary,
        *,
        output_flag: bool = False,
    ) -> None:
        boundary.validate(parameters, rounds)
        self.parameters = parameters
        self.rounds = rounds
        self.boundary = boundary
        self.backend = GurobiModel(
            f"{parameters.name}_{rounds}_{boundary.round_index}_{boundary.part_index}",
            output_flag=output_flag,
        )
        self.input_variables = self.backend.add_binary_vector(
            "suffix_input", parameters.block_size
        )

        current = self.input_variables
        for round_index in range(boundary.round_index, rounds):
            start_part = boundary.part_index if round_index == boundary.round_index else 0
            current = add_round_constraints(
                self.backend,
                current,
                parameters,
                round_index=round_index,
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
        """更新边界条件并执行一次 Algorithm 1 可达性查询。"""
        validate_vector(input_vector, self.parameters.block_size)
        target = unit_vector(target_index, self.parameters.block_size)
        self.backend.set_vector_fixer(self._input_fixer, input_vector)
        self.backend.set_vector_fixer(self._output_fixer, target)
        return self.backend.solve(time_limit=time_limit)


def scbdp_spn(
    parameters: SPNParameters,
    rounds: int,
    boundary: SPNBoundary,
    input_vector: int,
    target_index: int,
    *,
    time_limit: float | None = None,
    output_flag: bool = False,
) -> SolveStatus:
    """构建一次性 SPN 后缀模型并返回 CBDP trail 可达性。"""
    suffix = SPNSuffixModel(
        parameters,
        rounds,
        boundary,
        output_flag=output_flag,
    )
    return suffix.check_trail(input_vector, target_index, time_limit=time_limit)
