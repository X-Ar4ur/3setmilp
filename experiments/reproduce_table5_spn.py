"""逐输出位复现论文 Table 5 的 PRESENT/RECTANGLE 结果。"""

import argparse
import json
import platform
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from three_set_milp.ciphers.present import (
    PRESENT,
    PRESENT_PAPER_PRINT_INDICES,
)
from three_set_milp.ciphers.rectangle import (
    RECTANGLE,
    RECTANGLE_PAPER_PRINT_INDICES,
)
from three_set_milp.ciphers.spn import SPNParameters
from three_set_milp.core.bdpt import Parity
from three_set_milp.core.oracle import theoretical_unknown_constant_cube_state
from three_set_milp.core.patterns import (
    active_indices_from_layout_pattern,
    compact_pattern,
    format_parity_layout_pattern,
)
from three_set_milp.search.bdpt_search import (
    CachedSuffixOracle,
    search_bdpt,
    search_k_bdpt,
)
from three_set_milp.search.spn import (
    SPNGurobiOracle,
    spn_k_bdpt_parts,
    spn_search_parts,
)


PARAMETERS = {"present": PRESENT, "rectangle": RECTANGLE}
PAPER_LAYOUTS = {
    "present": PRESENT_PAPER_PRINT_INDICES,
    "rectangle": RECTANGLE_PAPER_PRINT_INDICES,
}
EXPERIMENTS = ("present60", "present63", "rectangle60")


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
    parser.add_argument(
        "--algorithm",
        choices=("bdpt", "k-bdpt"),
        default="bdpt",
        help="主论文 Algorithm 2，或后续论文的密钥旁路 K-BDPT",
    )
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def load_config(experiment: str) -> dict[str, Any]:
    path = Path("configs/table5") / f"{experiment}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def initial_payload(
    experiment: str,
    config: dict[str, Any],
    parameters: SPNParameters,
    algorithm: str,
) -> dict[str, Any]:
    import gurobipy as gp

    return {
        "experiment": "paper_table5_spn",
        "case": experiment,
        "algorithm": algorithm,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "gurobi": tuple(gp.gurobi.version()),
        },
        "config": config,
        "results": {},
        "pattern": "-" * parameters.block_size,
        "comparison": {"complete": False, "matches": False},
    }


def update_summary(
    payload: dict[str, Any], parameters: SPNParameters
) -> None:
    parities = {
        int(index): Parity(result["parity"])
        for index, result in payload["results"].items()
    }
    group_size = int(payload["config"]["group_size"])
    layout = PAPER_LAYOUTS[str(payload["config"]["cipher"])]
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
    parameters = PARAMETERS[str(config["cipher"])]
    rounds = int(config["rounds"])
    algorithm_suffix = "" if args.algorithm == "bdpt" else "_k_bdpt"
    output = args.output or Path(
        f"output/results/table5_{args.experiment}{algorithm_suffix}.json"
    )
    if output.exists():
        payload = json.loads(output.read_text(encoding="utf-8"))
        if payload.get("case") != args.experiment:
            raise ValueError("已有检查点的实验配置与当前命令不一致")
        if payload.get("algorithm", "bdpt") != args.algorithm:
            raise ValueError("已有检查点的搜索算法与当前命令不一致")
        if payload.get("config") != config:
            raise ValueError(
                "已有检查点由旧配置生成，请移动旧文件或使用新的 --output 路径"
            )
    else:
        payload = initial_payload(
            args.experiment, config, parameters, args.algorithm
        )

    targets = (
        list(range(parameters.block_size))
        if args.targets is None
        else sorted(set(args.targets))
    )
    if any(index < 0 or index >= parameters.block_size for index in targets):
        raise ValueError("目标位超出密码状态范围")

    active = active_indices_from_layout_pattern(
        str(config["input_pattern"]),
        PAPER_LAYOUTS[str(config["cipher"])],
    )
    initial_state = theoretical_unknown_constant_cube_state(
        parameters.block_size, active
    )
    if args.algorithm == "k-bdpt":
        parts = spn_k_bdpt_parts(parameters, rounds)
        search = search_k_bdpt
    else:
        parts = spn_search_parts(parameters, rounds)
        search = search_bdpt

    for target_index in targets:
        key = str(target_index)
        if key in payload["results"]:
            print(f"跳过已完成目标位 {target_index}")
            continue
        oracle = CachedSuffixOracle(
            SPNGurobiOracle(
                parameters,
                rounds,
                time_limit=args.time_limit,
                output_flag=args.gurobi_log,
            )
        )
        payload["running_target"] = target_index
        write_checkpoint(output, payload)
        print(f"开始目标位 {target_index}，正在执行首个后缀查询……", flush=True)
        started = time.perf_counter()
        result = search(initial_state, target_index, parts, oracle)
        payload["results"][key] = {
            "parity": result.parity.value,
            "reason": result.reason.value,
            "elapsed_seconds": time.perf_counter() - started,
            "oracle_calls": oracle.calls,
            "cache_hits": oracle.cache_hits,
            "trace": [asdict(entry) for entry in result.trace],
        }
        payload["running_target"] = None
        update_summary(payload, parameters)
        write_checkpoint(output, payload)
        print(
            f"目标位 {target_index}: {result.parity.value}; "
            f"当前输出 {payload['pattern']}"
        )

    update_summary(payload, parameters)
    write_checkpoint(output, payload)
    print(json.dumps(payload["comparison"], ensure_ascii=False, indent=2))
    print(f"检查点: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
