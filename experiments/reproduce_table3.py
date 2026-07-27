"""在有 Gurobi License 的服务器上复现论文 Table 3 的 SIMON32 目标位。"""

import argparse
import json
import platform
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from three_set_milp.ciphers.simon import SIMON32, format_paper_state
from three_set_milp.core.oracle import theoretical_unknown_constant_cube_state
from three_set_milp.search.bdpt_search import CachedSuffixOracle, search_bdpt
from three_set_milp.search.simon import SimonGurobiOracle, simon_search_parts


PAPER_K = [1, 0, 0, 0, 0, 0]
PAPER_L = [1, 1, 1, 2, 2, 0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=14)
    parser.add_argument(
        "--target-index",
        type=int,
        default=16,
        help="内部输出位索引；16 是论文打印状态最右侧的 y_0",
    )
    parser.add_argument(
        "--time-limit",
        type=float,
        default=None,
        help="每次 MILP 查询的秒数上限；未证明不可行时实验会失败",
    )
    parser.add_argument(
        "--gurobi-log",
        action="store_true",
        help="显示每次 Gurobi 求解日志",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="JSON 输出路径",
    )
    return parser.parse_args()


def gurobi_version() -> tuple[int, ...]:
    import gurobipy as gp

    return tuple(gp.gurobi.version())


def build_round_summary(initial_state: Any, result: Any) -> list[dict[str, int]]:
    """按论文轮边界汇总剪枝后的 K/L 规模。"""
    summary = [{"round": 0, "k": len(initial_state.k), "l": len(initial_state.l)}]
    for entry in result.trace:
        boundary = entry.boundary
        if boundary.part_index == 0 and boundary.round_index > 0:
            summary.append(
                {
                    "round": boundary.round_index,
                    "k": 0,
                    "l": entry.l_survivors,
                }
            )
    return summary


def compare_table3_prefix(summary: list[dict[str, int]]) -> dict[str, Any]:
    observed_k = [entry["k"] for entry in summary[: len(PAPER_K)]]
    observed_l = [entry["l"] for entry in summary[: len(PAPER_L)]]
    return {
        "expected_k": PAPER_K,
        "expected_l": PAPER_L,
        "observed_k": observed_k,
        "observed_l": observed_l,
        "matches": observed_k == PAPER_K and observed_l == PAPER_L,
    }


def main() -> int:
    args = parse_args()
    if args.rounds <= 0:
        raise ValueError("轮数必须为正数")
    if args.target_index < 0 or args.target_index >= SIMON32.block_size:
        raise ValueError("目标位超出 SIMON32 状态范围")

    constant_index = 15
    active_indices = set(range(SIMON32.block_size)) - {constant_index}
    initial_state = theoretical_unknown_constant_cube_state(
        SIMON32.block_size,
        active_indices,
    )

    raw_oracle = SimonGurobiOracle(
        SIMON32,
        args.rounds,
        time_limit=args.time_limit,
        output_flag=args.gurobi_log,
    )
    oracle = CachedSuffixOracle(raw_oracle)
    parts = simon_search_parts(SIMON32, args.rounds)

    started = time.perf_counter()
    result = search_bdpt(initial_state, args.target_index, parts, oracle)
    elapsed = time.perf_counter() - started
    round_summary = build_round_summary(initial_state, result)

    payload = {
        "experiment": "paper_table3_simon32_rightmost_output",
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "gurobi": gurobi_version(),
        },
        "parameters": {
            "rounds": args.rounds,
            "target_index": args.target_index,
            "constant_index": constant_index,
            "time_limit_per_query": args.time_limit,
        },
        "initial": {
            "k": [format_paper_state(value, SIMON32) for value in sorted(initial_state.k)],
            "l": [format_paper_state(value, SIMON32) for value in sorted(initial_state.l)],
        },
        "result": {
            "parity": result.parity.value,
            "reason": result.reason.value,
            "elapsed_seconds": elapsed,
            "oracle_calls": oracle.calls,
            "cache_hits": oracle.cache_hits,
        },
        "round_summary": round_summary,
        "table3_prefix": compare_table3_prefix(round_summary),
        "trace": [asdict(entry) for entry in result.trace],
    }

    output = args.output or Path(
        f"output/results/table3_simon32_target_{args.target_index}.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload["result"], ensure_ascii=False, indent=2))
    print(f"结果已写入: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

