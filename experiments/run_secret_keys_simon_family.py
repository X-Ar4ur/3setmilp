"""运行论文未给出完整表格参数的 SIMON/SIMECK K-BDPT 实验。"""

import argparse
import json
import time
from dataclasses import asdict
from pathlib import Path

if __package__:
    from .followup_common import (
        ALGORITHM_VERSIONS,
        build_initial_state,
        environment_payload,
        write_checkpoint,
    )
else:
    from followup_common import (
        ALGORITHM_VERSIONS,
        build_initial_state,
        environment_payload,
        write_checkpoint,
    )
from three_set_milp.ciphers.simon import (
    SIMON32,
    SIMON48,
    SIMON64,
    SIMON96,
    SIMON128,
    SIMECK32,
    SIMECK48,
    SIMECK64,
    SimonParameters,
)
from three_set_milp.core.bdpt import Parity
from three_set_milp.core.patterns import (
    compact_pattern,
    format_parity_layout_pattern,
)
from three_set_milp.search.bdpt_search import (
    CachedSuffixOracle,
    search_bdpt,
    search_k_bdpt,
    search_k_bdpt_literal,
)
from three_set_milp.search.simon import SimonGurobiOracle, simon_k_bdpt_parts


PARAMETERS = {
    "simon32": SIMON32,
    "simon48": SIMON48,
    "simon64": SIMON64,
    "simon96": SIMON96,
    "simon128": SIMON128,
    "simeck32": SIMECK32,
    "simeck48": SIMECK48,
    "simeck64": SIMECK64,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("variant", choices=tuple(PARAMETERS))
    parser.add_argument("--rounds", type=int, required=True)
    parser.add_argument(
        "--input-pattern",
        required=True,
        help="论文格式的 a/c 模式，依次为左右字",
    )
    parser.add_argument("--expected-output", default=None)
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
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def update_summary(
    payload: dict,
    parameters: SimonParameters,
    expected_output: str | None,
) -> None:
    parities = {
        int(index): Parity(result["parity"])
        for index, result in payload["results"].items()
    }
    pattern = format_parity_layout_pattern(
        parities,
        parameters.paper_print_indices,
        group_size=parameters.word_size,
    )
    complete = "-" not in pattern
    payload["pattern"] = pattern
    payload["comparison"] = {
        "complete": complete,
        "matches": None
        if expected_output is None or not complete
        else compact_pattern(pattern) == compact_pattern(expected_output),
        "paper_data_available": expected_output is not None,
    }


def main() -> int:
    args = parse_args()
    if args.rounds <= 0:
        raise ValueError("轮数必须为正数")
    parameters = PARAMETERS[args.variant]
    initial_state, constant_semantics = build_initial_state(
        args.input_pattern,
        parameters.paper_print_indices,
        parameters.block_size,
        args.constant_values,
    )
    identity = {
        "experiment": "secret_keys_simon_simeck_custom",
        "variant": args.variant,
        "rounds": args.rounds,
        "input_pattern": args.input_pattern,
        "expected_output": args.expected_output,
        "algorithm": args.algorithm,
        "algorithm_version": ALGORITHM_VERSIONS[args.algorithm],
        "key_bit_order": args.key_bit_order,
        "constant_semantics": constant_semantics,
    }
    if args.output.exists():
        payload = json.loads(args.output.read_text(encoding="utf-8"))
        for key, value in identity.items():
            if payload.get(key) != value:
                raise ValueError(f"已有检查点字段 {key} 与当前命令不一致")
    else:
        payload = {
            **identity,
            "environment": environment_payload(),
            "paper_limitation": (
                "后续论文仅称结果与既有最长区分器一致，未列出本变体的"
                "完整轮数、输入模式和输出模式；本入口要求调用者显式提供"
            ),
            "results": {},
            "pattern": "-" * parameters.block_size,
            "comparison": {
                "complete": False,
                "matches": None,
                "paper_data_available": args.expected_output is not None,
            },
        }
    targets = (
        list(range(parameters.block_size))
        if args.targets is None
        else sorted(set(args.targets))
    )
    if any(index < 0 or index >= parameters.block_size for index in targets):
        raise ValueError("目标位超出 SIMON/SIMECK 分组范围")
    parts = simon_k_bdpt_parts(
        parameters,
        args.rounds,
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
                args.rounds,
                time_limit=args.time_limit,
                output_flag=args.gurobi_log,
            )
        )
        payload["running_target"] = target_index
        write_checkpoint(args.output, payload)
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
        update_summary(payload, parameters, args.expected_output)
        write_checkpoint(args.output, payload)
        print(f"目标位 {target_index}: {result.parity.value}")
    update_summary(payload, parameters, args.expected_output)
    write_checkpoint(args.output, payload)
    print(json.dumps(payload["comparison"], ensure_ascii=False, indent=2))
    print(f"检查点: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
