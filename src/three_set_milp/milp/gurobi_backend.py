"""Gurobi 的最小封装；模块导入本身不要求已安装 gurobipy。"""

from collections.abc import Sequence
from enum import Enum
from typing import Any

from three_set_milp.core.bitvector import validate_vector

from .transitions import valid_sbox_transitions


class SolveStatus(str, Enum):
    """可行性模型对密码分析有意义的三种状态。"""

    FEASIBLE = "feasible"
    INFEASIBLE = "infeasible"
    UNDETERMINED = "undetermined"


class GurobiUnavailableError(RuntimeError):
    """gurobipy、运行环境或许可证不可用。"""


def _load_gurobi() -> Any:
    try:
        import gurobipy as gp
    except (ImportError, OSError) as error:
        raise GurobiUnavailableError(f"无法导入 gurobipy：{error}") from error
    return gp


class GurobiModel:
    """用于构造 CBDP 可行性问题的最小 Gurobi 模型。"""

    def __init__(self, name: str, *, output_flag: bool = False) -> None:
        self._gp = _load_gurobi()
        try:
            self.model = self._gp.Model(name)
        except self._gp.GurobiError as error:
            raise GurobiUnavailableError(f"无法创建 Gurobi 模型：{error}") from error
        self.model.Params.OutputFlag = int(output_flag)

    def add_binary_vector(self, name: str, width: int) -> tuple[Any, ...]:
        """按索引顺序创建一组二进制变量。"""
        if width <= 0:
            raise ValueError("MILP 向量宽度必须为正数")
        return tuple(
            self.model.addVar(vtype=self._gp.GRB.BINARY, name=f"{name}_{index}")
            for index in range(width)
        )

    def add_copy(self, input_variable: Any, output_variables: Sequence[Any]) -> None:
        """添加论文 Model 1：输入等于全部 Copy 输出之和。"""
        if not output_variables:
            raise ValueError("Copy 至少需要一个输出变量")
        self.model.addConstr(
            input_variable == self._gp.quicksum(output_variables),
            name="copy",
        )

    def add_xor(self, input_variables: Sequence[Any], output_variable: Any) -> None:
        """添加论文 Model 2：XOR 输出等于全部输入之和。"""
        if not input_variables:
            raise ValueError("XOR 至少需要一个输入变量")
        self.model.addConstr(
            output_variable == self._gp.quicksum(input_variables),
            name="xor",
        )

    def add_and(self, input_variables: Sequence[Any], output_variable: Any) -> None:
        """添加论文 Model 3：AND 输出不小于任一输入。"""
        if not input_variables:
            raise ValueError("AND 至少需要一个输入变量")
        for index, input_variable in enumerate(input_variables):
            self.model.addConstr(
                output_variable >= input_variable,
                name=f"and_{index}",
            )

    def add_sbox(
        self,
        input_variables: Sequence[Any],
        output_variables: Sequence[Any],
        truth_table: Sequence[int],
        *,
        name: str = "sbox",
    ) -> None:
        """用扩展凸包公式精确描述全部合法 S-box transition。"""
        if not input_variables or not output_variables:
            raise ValueError("S-box 输入和输出变量不能为空")
        input_width = len(input_variables)
        output_width = len(output_variables)
        transitions = tuple(sorted(valid_sbox_transitions(
            truth_table,
            input_width=input_width,
            output_width=output_width,
        )))
        weights = tuple(
            self.model.addVar(
                lb=0.0,
                ub=1.0,
                vtype=self._gp.GRB.CONTINUOUS,
                name=f"{name}_lambda_{index}",
            )
            for index in range(len(transitions))
        )
        self.model.addConstr(
            self._gp.quicksum(weights) == 1,
            name=f"{name}_convex_sum",
        )
        for bit_index, variable in enumerate(input_variables):
            self.model.addConstr(
                variable
                == self._gp.quicksum(
                    weight
                    for weight, (input_value, _) in zip(
                        weights, transitions, strict=True
                    )
                    if input_value & (1 << bit_index)
                ),
                name=f"{name}_input_{bit_index}",
            )
        for bit_index, variable in enumerate(output_variables):
            self.model.addConstr(
                variable
                == self._gp.quicksum(
                    weight
                    for weight, (_, output_value) in zip(
                        weights, transitions, strict=True
                    )
                    if output_value & (1 << bit_index)
                ),
                name=f"{name}_output_{bit_index}",
            )

    def add_vector_fixer(
        self, variables: Sequence[Any], *, name: str
    ) -> tuple[Any, ...]:
        """添加可修改右端值的向量固定约束。"""
        if not variables:
            raise ValueError("固定向量不能为空")
        return tuple(
            self.model.addConstr(variable == 0, name=f"{name}_{index}")
            for index, variable in enumerate(variables)
        )

    def set_vector_fixer(self, constraints: Sequence[Any], value: int) -> None:
        """更新一组固定约束的右端值，用于复用已构建的模型。"""
        validate_vector(value, len(constraints))
        for index, constraint in enumerate(constraints):
            constraint.RHS = (value >> index) & 1

    def fix_vector(
        self, variables: Sequence[Any], value: int, *, name: str = "fix"
    ) -> None:
        """将一组二进制变量固定为给定整数向量。"""
        validate_vector(value, len(variables))
        for index, variable in enumerate(variables):
            self.model.addConstr(
                variable == ((value >> index) & 1),
                name=f"{name}_{index}",
            )

    def solve(self, *, time_limit: float | None = None) -> SolveStatus:
        """求解无目标可行性模型；只有严格不可行才能证明 balanced。"""
        if time_limit is not None:
            if time_limit <= 0:
                raise ValueError("时间限制必须为正数")
            self.model.Params.TimeLimit = time_limit
        try:
            self.model.optimize()
        except self._gp.GurobiError as error:
            raise GurobiUnavailableError(f"Gurobi 求解失败：{error}") from error

        if self.model.Status == self._gp.GRB.INFEASIBLE:
            return SolveStatus.INFEASIBLE
        if self.model.SolCount > 0:
            return SolveStatus.FEASIBLE
        return SolveStatus.UNDETERMINED
