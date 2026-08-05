"""后续论文三个新增实验入口共用的检查点与格式化工具。"""

import json
import platform
import sys
from importlib import import_module
from pathlib import Path
from typing import Any

from three_set_milp.core.bdpt import BDPTState, Parity
from three_set_milp.core.oracle import (
    append_known_zero_bits,
    theoretical_known_constant_cube_state,
    theoretical_unknown_constant_cube_state,
)
from three_set_milp.core.patterns import (
    active_indices_from_layout_pattern,
    compact_pattern,
    constant_values_from_layout_pattern,
    format_parity_layout_pattern,
)


ALGORITHM_VERSIONS = {
    "bdpt": "original_algorithm2_literal_v1",
    "k-bdpt": "followup_algorithm1_example_semantics_v5",
    "k-bdpt-literal": "followup_algorithm1_literal_v2",
}


def build_initial_state(
    pattern: str,
    layout: tuple[int, ...],
    analysis_width: int,
    constant_values: str | None,
) -> tuple[BDPTState, dict[str, str]]:
    """构造论文明文 cube，并把密码专用辅助位固定为 0。"""
    block_size = len(layout)
    active = active_indices_from_layout_pattern(pattern, layout)
    if constant_values is None:
        state = theoretical_unknown_constant_cube_state(block_size, active)
        semantics = {"mode": "unknown"}
    else:
        normalized = compact_pattern(constant_values)
        constants = constant_values_from_layout_pattern(
            pattern,
            layout,
            normalized,
        )
        state = theoretical_known_constant_cube_state(
            block_size,
            active,
            constants,
        )
        semantics = {
            "mode": "known",
            "values_in_print_order": normalized,
        }
    if analysis_width < block_size:
        raise ValueError("分析状态不能窄于真实分组")
    if analysis_width > block_size:
        state = append_known_zero_bits(state, analysis_width - block_size)
    return state, semantics


def environment_payload() -> dict[str, Any]:
    """记录可用的 Python、平台和 Gurobi 版本。"""
    try:
        gp = import_module("gurobipy")

        gurobi: tuple[int, ...] | None = tuple(gp.gurobi.version())
    except (ImportError, OSError):
        gurobi = None
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "gurobi": gurobi,
    }


def update_summary(
    payload: dict[str, Any],
    layout: tuple[int, ...],
    expected_output: str,
    group_size: int,
) -> None:
    """按论文 layout 生成当前输出模式并与表格逐字符比较。"""
    parities = {
        int(index): Parity(result["parity"])
        for index, result in payload["results"].items()
    }
    pattern = format_parity_layout_pattern(
        parities,
        layout,
        group_size=group_size,
    )
    complete = "-" not in pattern
    payload["pattern"] = pattern
    payload["comparison"] = {
        "complete": complete,
        "matches": complete
        and compact_pattern(pattern) == compact_pattern(expected_output),
    }


def write_checkpoint(path: Path, payload: dict[str, Any]) -> None:
    """以 UTF-8 单文件检查点形式写出 JSON。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
