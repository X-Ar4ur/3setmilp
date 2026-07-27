"""逐输出位复现论文 Table 4 的 SIMON32/SIMON64 结果。"""

import argparse
import json
import platform
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from three_set_milp.ciphers.simon import SIMON32, SIMON64, SimonParameters
from three_set_milp.core.oracle import theoretical_unknown_constant_cube_state
from three_set_milp.search.bdpt_search import CachedSuffixOracle, search_bdpt
from three_set_milp.search.simon import SimonGurobiOracle, simon_search_parts


PARAMETERS = {"simon32": SIMON32, "simon64": SIMON64}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("variant", choices=sorted(PARAMETERS))
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


def load_config(variant: str) -> dict[str, Any]:
    path = Path("configs/table4") / f"{variant}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def paper_pattern(
    results: dict[str, Any], parameters: SimonParameters
) -> tuple[str, str]:
    """将已完成目标位按论文高索引到低索引的左右字顺序格式化。"""
    symbols = {"zero": "b", "one": "1", "unknown": "?"}

    def symbol(index: int) -> str:
        result = results.get(str(index))
        return "-" if result is None else symbols[result["parity"]]

    width = parameters.word_size
    left = "".join(symbol(index) for index in reversed(range(width)))
    right = "".join(
        symbol(width + index) for index in reversed(range(width))
    )
    return left, right


def initial_payload(
    variant: str, config: dict[str, Any], parameters: SimonParameters
) -> dict[str, Any]:
    import gurobipy as gp

    return {
        "experiment": "paper_table4_simon",
        "variant": variant,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "gurobi": tuple(gp.gurobi.version()),
        },
        "config": config,
        "results": {},
        "pattern": {"left": "-" * parameters.word_size, "right": "-" * parameters.word_size},
        "comparison": {"complete": False, "matches": False},
    }


def update_summary(
    payload: dict[str, Any], parameters: SimonParameters
) -> None:
    left, right = paper_pattern(payload["results"], parameters)
    config = payload["config"]
    complete = "-" not in left + right
    payload["pattern"] = {"left": left, "right": right}
    payload["comparison"] = {
        "complete": complete,
        "matches": complete
        and left == config["expected_left"]
        and right == config["expected_right"],
    }


def write_checkpoint(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    parameters = PARAMETERS[args.variant]
    config = load_config(args.variant)
    output = args.output or Path(
        f"output/results/table4_{args.variant}.json"
    )
    if output.exists():
        payload = json.loads(output.read_text(encoding="utf-8"))
        if payload.get("variant") != args.variant:
            raise ValueError("已有检查点的密码变体与当前命令不一致")
    else:
        payload = initial_payload(args.variant, config, parameters)

    targets = (
        list(range(parameters.block_size))
        if args.targets is None
        else sorted(set(args.targets))
    )
    if any(index < 0 or index >= parameters.block_size for index in targets):
        raise ValueError("目标位超出密码状态范围")

    constant_index = int(config["constant_index"])
    active = set(range(parameters.block_size)) - {constant_index}
    initial_state = theoretical_unknown_constant_cube_state(
        parameters.block_size,
        active,
    )
    parts = simon_search_parts(parameters, int(config["direct_rounds"]))

    for target_index in targets:
        key = str(target_index)
        if key in payload["results"]:
            print(f"跳过已完成目标位 {target_index}")
            continue
        oracle = CachedSuffixOracle(
            SimonGurobiOracle(
                parameters,
                int(config["direct_rounds"]),
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
        update_summary(payload, parameters)
        write_checkpoint(output, payload)
        print(
            f"目标位 {target_index}: {result.parity.value}; "
            f"当前输出 ({payload['pattern']['left']}, {payload['pattern']['right']})"
        )

    update_summary(payload, parameters)
    write_checkpoint(output, payload)
    print(json.dumps(payload["comparison"], ensure_ascii=False, indent=2))
    print(f"检查点: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

