"""复现后续论文 Table 3 的 KATAN/KTANTAN 积分区分器。"""

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
from three_set_milp.ciphers.katan import (
    KATAN32,
    KATAN48,
    KATAN64,
    KatanParameters,
)
from three_set_milp.search.bdpt_search import (
    CachedSuffixOracle,
    search_bdpt,
    search_k_bdpt,
    search_k_bdpt_literal,
)
from three_set_milp.search.katan import KatanGurobiOracle, katan_search_parts


PARAMETERS = {
    "katan32": KATAN32,
    "katan48": KATAN48,
    "katan64": KATAN64,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", choices=tuple(PARAMETERS))
    parser.add_argument(
        "--algorithm",
        choices=("bdpt", "k-bdpt", "k-bdpt-literal"),
        default="k-bdpt",
    )
    parser.add_argument("--targets", type=int, nargs="*", default=None)
    parser.add_argument("--constant-values", default=None)
    parser.add_argument("--time-limit", type=float, default=None)
    parser.add_argument("--gurobi-log", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def load_config(experiment: str) -> dict[str, Any]:
    path = Path("configs/secret_keys/table3") / f"{experiment}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    config = load_config(args.experiment)
    parameters: KatanParameters = PARAMETERS[args.experiment]
    total_clocks = int(config["total_clocks"])
    initial_state, constant_semantics = build_initial_state(
        str(config["input_pattern"]),
        parameters.paper_print_indices,
        parameters.state_width,
        args.constant_values,
    )
    output = args.output or Path(
        "output/results/secret_keys_table3_"
        f"{args.experiment}_{args.algorithm.replace('-', '_')}.json"
    )
    identity = {
        "experiment": "secret_keys_table3_katan_ktantan",
        "case": args.experiment,
        "algorithm": args.algorithm,
        "algorithm_version": ALGORITHM_VERSIONS[args.algorithm],
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
            "analysis_state_width": parameters.state_width,
            "feedback_accumulators": {
                "fa_old_l1_msb": parameters.fa_index,
                "fb_old_l2_msb": parameters.fb_index,
            },
            "key_schedule_scope": (
                "KATAN 与 KTANTAN 共用轮变换；CBDP/K-BDPT 把轮密钥位视为"
                "未知常量，因此同一模型覆盖两种密钥编排"
            ),
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
        raise ValueError("KATAN 目标位超出分组范围")
    parts = katan_search_parts(parameters, total_clocks)
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
            KatanGurobiOracle(
                parameters,
                total_clocks,
                time_limit=args.time_limit,
                output_flag=args.gurobi_log,
            )
        )
        payload["running_target"] = target_index
        write_checkpoint(output, payload)
        print(f"开始 KATAN 目标位 {target_index}", flush=True)
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
