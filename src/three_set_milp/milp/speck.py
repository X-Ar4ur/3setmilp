"""SPECK 的精确 CBDP 后缀 MILP。"""

from dataclasses import dataclass
from typing import Any

from three_set_milp.ciphers.speck import (
    FULL_ADDER_TABLE,
    XOR_INTO_SECOND_TABLE,
    ZERO_BIT_TABLE,
    SpeckParameters,
    classify_part,
    first_rotation_permutation,
    second_rotation_permutation,
)
from three_set_milp.core.bitvector import unit_vector, validate_vector

from .gurobi_backend import GurobiModel, SolveStatus


@dataclass(frozen=True, slots=True)
class SpeckBoundary:
    """SPECK 轮内局部函数的输入边界。"""

    round_index: int
    part_index: int

    def validate(self, parameters: SpeckParameters, rounds: int) -> None:
        if rounds <= 0:
            raise ValueError("轮数必须为正数")
        if self.round_index < 0 or self.round_index > rounds:
            raise ValueError("SPECK 起始轮超出目标轮数")
        if self.round_index == rounds:
            if self.part_index != 0:
                raise ValueError("SPECK 最终边界的局部编号必须为 0")
            return
        if self.part_index < 0 or self.part_index >= parameters.parts_per_round:
            raise ValueError("SPECK 局部函数编号超出范围")


def _add_local_transform(
    backend: GurobiModel,
    state: tuple[Any, ...],
    indices: tuple[int, ...],
    truth_table: tuple[int, ...],
    *,
    name: str,
) -> tuple[Any, ...]:
    """在固定状态的若干索引上添加一个等宽局部布尔函数。"""
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


def add_part_constraints(
    backend: GurobiModel,
    state: tuple[Any, ...],
    parameters: SpeckParameters,
    *,
    round_index: int,
    part_index: int,
) -> tuple[Any, ...]:
    """添加一个 SPECK 局部操作的 CBDP transition。"""
    operation, bit_index = classify_part(parameters, part_index)
    prefix = f"r{round_index}_p{part_index}"
    width = parameters.word_size
    if operation == "rotate_first":
        return tuple(
            state[index] for index in first_rotation_permutation(parameters)
        )
    if operation == "add":
        if bit_index is None:
            raise RuntimeError("模加局部操作缺少比特编号")
        return _add_local_transform(
            backend,
            state,
            (width + bit_index, bit_index, parameters.carry_index),
            FULL_ADDER_TABLE,
            name=prefix,
        )
    if operation == "key":
        # 对 CBDP 而言，异或任意常量轮密钥是恒等映射。
        return state
    if operation == "rotate_second":
        return tuple(
            state[index] for index in second_rotation_permutation(parameters)
        )
    if operation == "xor":
        if bit_index is None:
            raise RuntimeError("XOR 局部操作缺少比特编号")
        return _add_local_transform(
            backend,
            state,
            (width + bit_index, bit_index),
            XOR_INTO_SECOND_TABLE,
            name=prefix,
        )
    return _add_local_transform(
        backend,
        state,
        (parameters.carry_index,),
        ZERO_BIT_TABLE,
        name=prefix,
    )


def add_round_constraints(
    backend: GurobiModel,
    input_state: tuple[Any, ...],
    parameters: SpeckParameters,
    *,
    round_index: int,
    start_part: int = 0,
) -> tuple[Any, ...]:
    """添加一轮或首轮剩余部分的 SPECK 约束。"""
    if len(input_state) != parameters.state_width:
        raise ValueError("SPECK MILP 输入状态宽度不正确")
    if start_part < 0 or start_part >= parameters.parts_per_round:
        raise ValueError("SPECK 部分轮起始编号超出范围")
    current = input_state
    for part_index in range(start_part, parameters.parts_per_round):
        current = add_part_constraints(
            backend,
            current,
            parameters,
            round_index=round_index,
            part_index=part_index,
        )
    return current


class SpeckSuffixModel:
    """从任意 SPECK 局部边界到最终输出的可复用 CBDP 模型。"""

    def __init__(
        self,
        parameters: SpeckParameters,
        rounds: int,
        boundary: SpeckBoundary,
        *,
        output_flag: bool = False,
    ) -> None:
        boundary.validate(parameters, rounds)
        self.parameters = parameters
        self.rounds = rounds
        self.boundary = boundary
        self.backend = GurobiModel(
            f"speck_{parameters.block_size}_{rounds}_"
            f"{boundary.round_index}_{boundary.part_index}",
            output_flag=output_flag,
        )
        self.input_variables = self.backend.add_binary_vector(
            "suffix_input", parameters.state_width
        )
        current = self.input_variables
        for round_index in range(boundary.round_index, rounds):
            start_part = (
                boundary.part_index
                if round_index == boundary.round_index
                else 0
            )
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
        """固定输入和真实分组输出单位向量，判断后缀可达性。"""
        validate_vector(input_vector, self.parameters.state_width)
        if target_index < 0 or target_index >= self.parameters.block_size:
            raise ValueError("SPECK 目标位超出分组范围")
        target = unit_vector(target_index, self.parameters.state_width)
        self.backend.set_vector_fixer(self._input_fixer, input_vector)
        self.backend.set_vector_fixer(self._output_fixer, target)
        return self.backend.solve(time_limit=time_limit)


def scbdp_speck(
    parameters: SpeckParameters,
    rounds: int,
    boundary: SpeckBoundary,
    input_vector: int,
    target_index: int,
    *,
    time_limit: float | None = None,
    output_flag: bool = False,
) -> SolveStatus:
    """构建一次性 SPECK 后缀模型并执行 CBDP 可达性查询。"""
    suffix = SpeckSuffixModel(
        parameters,
        rounds,
        boundary,
        output_flag=output_flag,
    )
    return suffix.check_trail(
        input_vector,
        target_index,
        time_limit=time_limit,
    )
