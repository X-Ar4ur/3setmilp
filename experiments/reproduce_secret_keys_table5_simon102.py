"""复现后续论文 Table 5 的 SIMON(102) 精确常量输出位。"""

import argparse
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

if __package__:
    from .followup_common import (
        ALGORITHM_VERSIONS,
        build_initial_state,
        environment_payload,
        update_summary,
        write_checkpoint,
    )
else:
    from followup_common import (
        ALGORITHM_VERSIONS,
        build_initial_state,
        environment_payload,
        update_summary,
        write_checkpoint,
    )
from three_set_milp.ciphers.simon import (
    SIMON102_32,
    SIMON102_48,
    SIMON102_64,
    SimonParameters,
)
from three_set_milp.search.bdpt_search import (
    CachedSuffixOracle,
    search_bdpt,
    search_k_bdpt,
    search_k_bdpt_literal,
)
from three_set_milp.search.simon import (
    SimonGurobiOracle,
    simon_k_bdpt_parts,
)


PARAMETERS = {
    "simon10232": SIMON102_32,
    "simon10248": SIMON102_48,
    "simon10264": SIMON102_64,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", choices=tuple(PARAMETERS))
    parser.add_argument(
        "--algorithm",
        choices=("bdpt", "k-bdpt", "k-bdpt-literal"),
        default="k-bdpt",
    )
    parser.add_argument(
        "--key-bit-order",
        choices=("ascending", "descending"),
        default="ascending",
    )
    parser.add_argument("--targets", type=int, nargs="*", default=None)
    parser.add_argument("--constant-values", default=None)
    parser.add_argument("--time-limit", type=float, default=None)
    parser.add_argument("--gurobi-log", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def load_config(experiment: str) -> dict[str, Any]:
    path = Path("configs/secret_keys/table5") / f"{experiment}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    config = load_config(args.experiment)
    parameters: SimonParameters = PARAMETERS[args.experiment]
    rounds = int(config["rounds"])
    initial_state, constant_semantics = build_initial_state(
        str(config["input_pattern"]),
        parameters.paper_print_indices,
        parameters.block_size,
        args.constant_values,
    )
    output = args.output or Path(
        "output/results/secret_keys_table5_"
        f"{args.experiment}_{args.algorithm.replace('-', '_')}_"
        f"key_{args.key_bit_order}.json"
    )
    identity = {
        "experiment": "secret_keys_table5_simon102",
        "case": args.experiment,
        "algorithm": args.algorithm,
        "algorithm_version": ALGORITHM_VERSIONS[args.algorithm],
        "key_bit_order": args.key_bit_order,
        "constant_semantics": constant_semantics,
        "config": config,
    }
    if output.exists():
        payload = json.loads(output.read_text(encoding="utf-8"))
        for key, value in identity.items():
            if payload.get(key) != value:
                raise ValueError(f"已有检查点字段 {key} 与当前命令不一致")
    else:
        payload = {
            **identity,
            "environment": environment_payload(),
            "rotation_constants": {
                "and": parameters.and_rotations,
                "xor": parameters.xor_rotation,
            },
            "results": {},
            "pattern": "-" * parameters.block_size,
            "comparison": {"complete": False, "matches": False},
        }

    targets = (
        list(range(parameters.block_size))
        if args.targets is None
        else sorted(set(args.targets))
    )
    if any(index < 0 or index >= parameters.block_size for index in targets):
        raise ValueError("SIMON(102) 目标位超出分组范围")
    parts = simon_k_bdpt_parts(
        parameters,
        rounds,
        key_bit_order=args.key_bit_order,
    )
    search = {
        "bdpt": search_bdpt,
        "k-bdpt": search_k_bdpt,
        "k-bdpt-literal": search_k_bdpt_literal,
    }[args.algorithm]

    for target_index in targets:
        key = str(target_index)
        if key in payload["results"]:
            print(f"跳过已完成目标位 {target_index}")
            continue
        oracle = CachedSuffixOracle(
            SimonGurobiOracle(
                parameters,
                rounds,
                time_limit=args.time_limit,
                output_flag=args.gurobi_log,
            )
        )
        payload["running_target"] = target_index
        write_checkpoint(output, payload)
        print(f"开始 SIMON(102) 目标位 {target_index}", flush=True)
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
        update_summary(
            payload,
            parameters.paper_print_indices,
            str(config["expected_output"]),
            int(config["group_size"]),
        )
        write_checkpoint(output, payload)
        print(f"目标位 {target_index}: {result.parity.value}")

    update_summary(
        payload,
        parameters.paper_print_indices,
        str(config["expected_output"]),
        int(config["group_size"]),
    )
    write_checkpoint(output, payload)
    print(json.dumps(payload["comparison"], ensure_ascii=False, indent=2))
    print(f"检查点: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
