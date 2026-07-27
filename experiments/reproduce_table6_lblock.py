"""逐输出位复现论文 Table 6 的 LBlock 结果。"""

import argparse
import json
import platform
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from three_set_milp.ciphers.lblock import (
    active_indices_from_paper_pattern,
    format_paper_parities,
)
from three_set_milp.core.oracle import theoretical_unknown_constant_cube_state
from three_set_milp.core.patterns import compact_pattern
from three_set_milp.search.bdpt_search import CachedSuffixOracle, search_bdpt
from three_set_milp.search.lblock import LBlockGurobiOracle, lblock_search_parts


EXPERIMENTS = ("lblock63", "lblock62")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", choices=EXPERIMENTS)
    parser.add_argument(
        "--targets",
        type=int,
        nargs="*",
        default=None,
        help="只运行指定内部输出位；默认运行全部位",
    )
    parser.add_argument(
        "--time-limit",
        type=float,
        default=None,
        help="单次 MILP 查询秒数上限；未确定状态会终止",
    )
    parser.add_argument("--gurobi-log", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def load_config(experiment: str) -> dict[str, Any]:
    path = Path("configs/table6") / f"{experiment}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def initial_payload(experiment: str, config: dict[str, Any]) -> dict[str, Any]:
    import gurobipy as gp

    return {
        "experiment": "paper_table6_lblock",
        "case": experiment,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "gurobi": tuple(gp.gurobi.version()),
        },
        "config": config,
        "model_note": "每轮先显式旋转右半，再执行 8 个 keyed core，最后交换两半",
        "results": {},
        "pattern": "-" * 32 + "," + "-" * 32,
        "comparison": {"complete": False, "matches": False},
    }


def update_summary(payload: dict[str, Any]) -> None:
    symbols = {"zero": "b", "one": "1", "unknown": "?"}
    parities = {
        int(index): symbols[result["parity"]]
        for index, result in payload["results"].items()
    }
    pattern = format_paper_parities(parities)
    complete = "-" not in pattern
    payload["pattern"] = pattern
    payload["comparison"] = {
        "complete": complete,
        "matches": complete
        and compact_pattern(pattern)
        == compact_pattern(payload["config"]["expected_output"]),
    }


def write_checkpoint(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    config = load_config(args.experiment)
    rounds = int(config["rounds"])
    output = args.output or Path(
        f"output/results/table6_{args.experiment}.json"
    )
    if output.exists():
        payload = json.loads(output.read_text(encoding="utf-8"))
        if payload.get("case") != args.experiment:
            raise ValueError("已有检查点的实验配置与当前命令不一致")
    else:
        payload = initial_payload(args.experiment, config)

    targets = list(range(64)) if args.targets is None else sorted(set(args.targets))
    if any(index < 0 or index >= 64 for index in targets):
        raise ValueError("目标位超出 LBlock 状态范围")

    active = active_indices_from_paper_pattern(str(config["input_pattern"]))
    initial_state = theoretical_unknown_constant_cube_state(64, active)
    parts = lblock_search_parts(rounds)

    for target_index in targets:
        key = str(target_index)
        if key in payload["results"]:
            print(f"跳过已完成目标位 {target_index}")
            continue
        oracle = CachedSuffixOracle(
            LBlockGurobiOracle(
                rounds,
                time_limit=args.time_limit,
                output_flag=args.gurobi_log,
            )
        )
        started = time.perf_counter()
        result = search_bdpt(initial_state, target_index, parts, oracle)
        payload["results"][key] = {
            "parity": result.parity.value,
            "reason": result.reason.value,
            "elapsed_seconds": time.perf_counter() - started,
            "oracle_calls": oracle.calls,
            "cache_hits": oracle.cache_hits,
            "trace": [asdict(entry) for entry in result.trace],
        }
        update_summary(payload)
        write_checkpoint(output, payload)
        print(
            f"目标位 {target_index}: {result.parity.value}; "
            f"当前输出 {payload['pattern']}"
        )

    update_summary(payload)
    write_checkpoint(output, payload)
    print(json.dumps(payload["comparison"], ensure_ascii=False, indent=2))
    print(f"检查点: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
