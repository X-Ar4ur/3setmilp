"""LBlock 的精确 CBDP 后缀 MILP。"""

from dataclasses import dataclass
from typing import Any

from three_set_milp.ciphers.lblock import LBLOCK_P, LBLOCK_SBOXES
from three_set_milp.core.bitvector import unit_vector, validate_vector

from .gurobi_backend import GurobiModel, SolveStatus


@dataclass(frozen=True, slots=True)
class LBlockBoundary:
    """LBlock 局部边界；part 0--7 为 keyed core，8 为交换。"""

    round_index: int
    part_index: int

    def validate(self, rounds: int) -> None:
        if rounds <= 0:
            raise ValueError("轮数必须为正数")
        if self.round_index < 0 or self.round_index >= rounds:
            raise ValueError("起始轮超出目标密码轮数")
        if self.part_index < 0 or self.part_index > 8:
            raise ValueError("LBlock 局部函数编号超出范围")


def _rotate_right_half_variables(state: tuple[Any, ...]) -> tuple[Any, ...]:
    """保持左半不变，将右半按规范循环左移 8 bit。"""
    return state[:32] + tuple(state[32 + ((index - 8) % 32)] for index in range(32))


def add_round_constraints(
    backend: GurobiModel,
    input_state: tuple[Any, ...],
    *,
    round_index: int,
    start_part: int = 0,
) -> tuple[Any, ...]:
    """添加一轮或首轮剩余局部函数的 CBDP 约束。"""
    if len(input_state) != 64:
        raise ValueError("LBlock MILP 输入状态宽度不正确")
    if start_part < 0 or start_part > 8:
        raise ValueError("部分轮起始编号超出范围")

    current = list(
        _rotate_right_half_variables(input_state)
        if start_part == 0
        else input_state
    )
    for sbox_index in range(start_part, 8):
        prefix = f"r{round_index}_s{sbox_index}"
        x_indices = tuple(4 * sbox_index + bit for bit in range(4))
        destination = LBLOCK_P[sbox_index]
        y_indices = tuple(32 + 4 * destination + bit for bit in range(4))

        preserved = backend.add_binary_vector(f"{prefix}_keep", 4)
        sbox_input = backend.add_binary_vector(f"{prefix}_in", 4)
        sbox_output = backend.add_binary_vector(f"{prefix}_out", 4)
        y_output = backend.add_binary_vector(f"{prefix}_xor", 4)
        for bit, state_index in enumerate(x_indices):
            backend.add_copy(current[state_index], (preserved[bit], sbox_input[bit]))
        backend.add_sbox(
            sbox_input,
            sbox_output,
            LBLOCK_SBOXES[sbox_index],
            name=prefix,
        )
        for bit, state_index in enumerate(y_indices):
            backend.add_xor((current[state_index], sbox_output[bit]), y_output[bit])
            current[x_indices[bit]] = preserved[bit]
            current[state_index] = y_output[bit]

    # part 8 是 Feistel 两半交换。
    return tuple(current[32:]) + tuple(current[:32])


class LBlockSuffixModel:
    """从任意 LBlock 局部边界到最终输出的可复用 CBDP 模型。"""

    def __init__(
        self,
        rounds: int,
        boundary: LBlockBoundary,
        *,
        output_flag: bool = False,
    ) -> None:
        boundary.validate(rounds)
        self.rounds = rounds
        self.boundary = boundary
        self.backend = GurobiModel(
            f"lblock_{rounds}_{boundary.round_index}_{boundary.part_index}",
            output_flag=output_flag,
        )
        self.input_variables = self.backend.add_binary_vector("suffix_input", 64)
        current = self.input_variables
        for round_index in range(boundary.round_index, rounds):
            start_part = boundary.part_index if round_index == boundary.round_index else 0
            current = add_round_constraints(
                self.backend,
                current,
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
        """更新边界条件并执行一次 Algorithm 1。"""
        validate_vector(input_vector, 64)
        target = unit_vector(target_index, 64)
        self.backend.set_vector_fixer(self._input_fixer, input_vector)
        self.backend.set_vector_fixer(self._output_fixer, target)
        return self.backend.solve(time_limit=time_limit)
