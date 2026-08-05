"""复现后续论文 Table 2 的 SPECK 积分区分器与不精确密钥位。"""

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
from three_set_milp.ciphers.speck import (
    SPECK32,
    SPECK48,
    SPECK64,
    SPECK96,
    SpeckParameters,
)
from three_set_milp.search.bdpt_search import (
    CachedSuffixOracle,
    SearchResult,
    search_bdpt,
    search_k_bdpt,
    search_k_bdpt_literal,
)
from three_set_milp.search.speck import SpeckGurobiOracle, speck_search_parts


PARAMETERS = {
    "speck32": SPECK32,
    "speck48": SPECK48,
    "speck64": SPECK64,
    "speck96": SPECK96,
}
EXPERIMENTS = tuple(PARAMETERS)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", choices=EXPERIMENTS)
    parser.add_argument(
        "case",
        nargs="?",
        help="配置中的区分器 id；只有一个区分器时可以省略",
    )
    parser.add_argument(
        "--algorithm",
        choices=("bdpt", "k-bdpt", "k-bdpt-literal", "compare"),
        default="compare",
    )
    parser.add_argument("--targets", type=int, nargs="*", default=None)
    parser.add_argument("--constant-values", default=None)
    parser.add_argument("--time-limit", type=float, default=None)
    parser.add_argument("--gurobi-log", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def load_config(experiment: str) -> dict[str, Any]:
    path = Path("configs/secret_keys/table2") / f"{experiment}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def select_case(config: dict[str, Any], case_id: str | None) -> dict[str, Any]:
    cases = list(config["cases"])
    if case_id is None:
        if len(cases) != 1:
            choices = ", ".join(str(item["id"]) for item in cases)
            raise ValueError(f"该实验包含多个区分器，请指定 case：{choices}")
        return dict(cases[0])
    for item in cases:
        if item["id"] == case_id:
            return dict(item)
    raise ValueError(f"未知 SPECK 区分器 case：{case_id}")


def generated_key_label(result: SearchResult) -> str | None:
    """定位 Stopping Rule 1 前最后一个实际生成 K 的密钥 XOR。"""
    for entry in reversed(result.trace[:-1]):
        if entry.secret_key_label is not None and entry.k_after_propagation:
            return entry.secret_key_label
    return None


def serialize_result(
    result: SearchResult,
    *,
    elapsed: float,
    oracle_calls: int,
    cache_hits: int,
) -> dict[str, Any]:
    return {
        "parity": result.parity.value,
        "reason": result.reason.value,
        "elapsed_seconds": elapsed,
        "oracle_calls": oracle_calls,
        "cache_hits": cache_hits,
        "trace": [asdict(entry) for entry in result.trace],
    }


def main() -> int:
    args = parse_args()
    config = load_config(args.experiment)
    case = select_case(config, args.case)
    parameters: SpeckParameters = PARAMETERS[args.experiment]
    rounds = int(config["rounds"])
    initial_state, constant_semantics = build_initial_state(
        str(case["input_pattern"]),
        parameters.paper_print_indices,
        parameters.state_width,
        args.constant_values,
    )
    output = args.output or Path(
        "output/results/secret_keys_table2_"
        f"{args.experiment}_{case['id']}_{args.algorithm.replace('-', '_')}.json"
    )
    identity = {
        "experiment": "secret_keys_table2_speck",
        "case": f"{args.experiment}:{case['id']}",
        "algorithm": args.algorithm,
        "algorithm_version": (
            {
                "k-bdpt": ALGORITHM_VERSIONS["k-bdpt"],
                "bdpt": ALGORITHM_VERSIONS["bdpt"],
            }
            if args.algorithm == "compare"
            else ALGORITHM_VERSIONS[args.algorithm]
        ),
        "constant_semantics": constant_semantics,
        "config": config,
        "distinguisher": case,
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
            "auxiliary_bits": {"carry": parameters.carry_index, "initial": 0},
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
        raise ValueError("SPECK 目标位超出分组范围")
    parts = speck_search_parts(parameters, rounds)

    for target_index in targets:
        key = str(target_index)
        if key in payload["results"]:
            print(f"跳过已完成目标位 {target_index}")
            continue
        oracle = CachedSuffixOracle(
            SpeckGurobiOracle(
                parameters,
                rounds,
                time_limit=args.time_limit,
                output_flag=args.gurobi_log,
            )
        )
        payload["running_target"] = target_index
        write_checkpoint(output, payload)
        print(f"开始 SPECK 目标位 {target_index}", flush=True)

        started = time.perf_counter()
        if args.algorithm in ("k-bdpt", "compare"):
            result = search_k_bdpt(initial_state, target_index, parts, oracle)
        elif args.algorithm == "k-bdpt-literal":
            result = search_k_bdpt_literal(
                initial_state, target_index, parts, oracle
            )
        else:
            result = search_bdpt(initial_state, target_index, parts, oracle)
        record = serialize_result(
            result,
            elapsed=time.perf_counter() - started,
            oracle_calls=oracle.calls,
            cache_hits=oracle.cache_hits,
        )

        if args.algorithm == "compare":
            calls_before = oracle.calls
            hits_before = oracle.cache_hits
            baseline_started = time.perf_counter()
            baseline = search_bdpt(
                initial_state,
                target_index,
                parts,
                oracle,
            )
            record["bdpt_baseline"] = serialize_result(
                baseline,
                elapsed=time.perf_counter() - baseline_started,
                oracle_calls=oracle.calls - calls_before,
                cache_hits=oracle.cache_hits - hits_before,
            )
            record["identified_inaccuracy_key"] = generated_key_label(baseline)
            expected_key = case.get("expected_inaccuracy_key")
            record["inaccuracy_key_matches"] = (
                expected_key is None
                or record["identified_inaccuracy_key"] == expected_key
            )

        payload["results"][key] = record
        payload["running_target"] = None
        update_summary(
            payload,
            parameters.paper_print_indices,
            str(case["expected_output"]),
            int(config["group_size"]),
        )
        write_checkpoint(output, payload)
        print(f"目标位 {target_index}: {result.parity.value}")

    update_summary(
        payload,
        parameters.paper_print_indices,
        str(case["expected_output"]),
        int(config["group_size"]),
    )
    write_checkpoint(output, payload)
    print(json.dumps(payload["comparison"], ensure_ascii=False, indent=2))
    print(f"检查点: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
