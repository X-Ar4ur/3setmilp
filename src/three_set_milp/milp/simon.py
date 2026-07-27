"""SIMON 的紧凑 CBDP 后缀 MILP 和 Algorithm 1。"""

from dataclasses import dataclass
from typing import Any

from three_set_milp.ciphers.simon import SimonParameters
from three_set_milp.core.bitvector import unit_vector, validate_vector

from .gurobi_backend import GurobiModel, SolveStatus


@dataclass(frozen=True, slots=True)
class SimonBoundary:
    """局部函数输入边界；轮号和局部编号均从 0 开始。"""

    round_index: int
    part_index: int

    def validate(self, parameters: SimonParameters, rounds: int) -> None:
        if rounds <= 0:
            raise ValueError("轮数必须为正数")
        if self.round_index < 0 or self.round_index >= rounds:
            raise ValueError("起始轮超出目标密码轮数")
        if self.part_index < 0 or self.part_index > parameters.word_size:
            raise ValueError("SIMON 局部函数编号超出范围")


def add_round_constraints(
    backend: GurobiModel,
    input_state: tuple[Any, ...],
    parameters: SimonParameters,
    *,
    round_index: int,
    start_part: int = 0,
) -> tuple[Any, ...]:
    """添加一轮或首轮后半部分的紧凑 CBDP trail 约束。"""
    width = parameters.word_size
    if len(input_state) != parameters.block_size:
        raise ValueError("SIMON MILP 输入状态宽度不正确")
    if start_part < 0 or start_part > width:
        raise ValueError("部分轮起始编号超出范围")

    prefix = f"r{round_index}"
    input_left = input_state[:width]
    input_right = input_state[width:]
    copy_first = backend.add_binary_vector(f"{prefix}_u", width)
    copy_second = backend.add_binary_vector(f"{prefix}_v", width)
    copy_linear = backend.add_binary_vector(f"{prefix}_w", width)
    and_output = backend.add_binary_vector(f"{prefix}_t", width)
    output_left = backend.add_binary_vector(f"{prefix}_a", width)
    output_right = backend.add_binary_vector(f"{prefix}_b", width)

    model = backend.model
    first_rotation, second_rotation = parameters.and_rotations
    xor_rotation = parameters.xor_rotation
    for index in range(width):
        # L1：一个输入指数分配到两个 AND 分支、线性分支或右支输出。
        model.addConstr(
            input_left[index]
            == copy_first[index]
            + copy_second[index]
            + copy_linear[index]
            + output_right[index],
            name=f"{prefix}_copy_{index}",
        )

        first_input = copy_first[(index - first_rotation) % width]
        second_input = copy_second[(index - second_rotation) % width]
        # L2：这里采用论文 SIMON 专用的精确 OR 描述。
        model.addConstr(
            and_output[index] >= first_input,
            name=f"{prefix}_and_first_{index}",
        )
        model.addConstr(
            and_output[index] >= second_input,
            name=f"{prefix}_and_second_{index}",
        )
        model.addConstr(
            and_output[index] <= first_input + second_input,
            name=f"{prefix}_and_upper_{index}",
        )

        # L3：论文右端误印为 1；按 XOR Model 2 应为 0。
        model.addConstr(
            output_left[index]
            == input_right[index]
            + and_output[index]
            + copy_linear[(index - xor_rotation) % width],
            name=f"{prefix}_xor_{index}",
        )

        # L4：起始边界前的核心操作已经执行，在后缀模型中改为恒等。
        if index < start_part:
            model.addConstr(
                output_left[index] == input_right[index],
                name=f"{prefix}_partial_identity_{index}",
            )

    return tuple(output_left) + tuple(output_right)


class SimonSuffixModel:
    """从任意 ``Q[round,part]`` 输入边界到最终输出的 CBDP 模型。"""

    def __init__(
        self,
        parameters: SimonParameters,
        rounds: int,
        boundary: SimonBoundary,
        *,
        output_flag: bool = False,
    ) -> None:
        boundary.validate(parameters, rounds)
        self.parameters = parameters
        self.rounds = rounds
        self.boundary = boundary
        self.backend = GurobiModel(
            f"simon_{parameters.block_size}_{rounds}_"
            f"{boundary.round_index}_{boundary.part_index}",
            output_flag=output_flag,
        )
        self.input_variables = self.backend.add_binary_vector(
            "suffix_input", parameters.block_size
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
        """固定输入向量和目标单位向量，执行 Algorithm 1。"""
        validate_vector(input_vector, self.parameters.block_size)
        target = unit_vector(target_index, self.parameters.block_size)
        self.backend.set_vector_fixer(self._input_fixer, input_vector)
        self.backend.set_vector_fixer(self._output_fixer, target)
        return self.backend.solve(time_limit=time_limit)


def scbdp_simon(
    parameters: SimonParameters,
    rounds: int,
    boundary: SimonBoundary,
    input_vector: int,
    target_index: int,
    *,
    time_limit: float | None = None,
    output_flag: bool = False,
) -> SolveStatus:
    """构建一次性后缀模型并返回 CBDP trail 可达性。"""
    suffix = SimonSuffixModel(
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
