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
from three_set_milp.core.oracle import (
    theoretical_known_constant_cube_state,
    theoretical_unknown_constant_cube_state,
)
from three_set_milp.core.patterns import (
    active_indices_from_layout_pattern,
    compact_pattern,
    constant_values_from_layout_pattern,
    format_parity_layout_pattern,
)
from three_set_milp.milp.gurobi_backend import SolveStatus
from three_set_milp.milp.spn import (
    SPNBoundary,
    SPNSuffixModel,
    validate_spn_witness,
)
from three_set_milp.search.bdpt_search import (
    CachedSuffixOracle,
    SearchResult,
    StopReason,
    search_bdpt,
    search_k_bdpt,
    search_k_bdpt_literal,
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
ALGORITHM_VERSIONS = {
    "bdpt": None,
    "k-bdpt": "followup_algorithm1_example_semantics_v4",
    "k-bdpt-literal": "followup_algorithm1_literal_v2",
}


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
        "--record-witness",
        action="store_true",
        help="对 Stopping Rule 1 的决定性 K 向量记录并独立核验 CBDP 轨迹",
    )
    parser.add_argument(
        "--algorithm",
        choices=("bdpt", "k-bdpt", "k-bdpt-literal"),
        default="bdpt",
        help=(
            "主论文 Algorithm 2、按 Example 2 补齐终态语义的 K-BDPT，"
            "或字面伪代码 K-BDPT 诊断模式"
        ),
    )
    parser.add_argument(
        "--constant-values",
        default=None,
        help=(
            "按输入模式中 c 的论文打印顺序指定全部 0/1 值；"
            "省略时按论文的未知常量初态建模"
        ),
    )
    parser.add_argument(
        "--key-bit-order",
        choices=("ascending", "descending"),
        default="ascending",
        help=(
            "K-BDPT 将轮密钥拆成标量 XOR 后的扫描顺序；"
            "默认 ascending 保持现有复现语义"
        ),
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
    constant_semantics: dict[str, str],
    key_bit_order: str | None,
) -> dict[str, Any]:
    import gurobipy as gp

    return {
        "experiment": "paper_table5_spn",
        "case": experiment,
        "algorithm": algorithm,
        "algorithm_version": ALGORITHM_VERSIONS[algorithm],
        "constant_semantics": constant_semantics,
        "key_bit_order": key_bit_order,
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


def has_recorded_witness(result: dict[str, Any], algorithm: str) -> bool:
    """判断续跑时是否已保存当前算法所需的审计证据。"""
    if "decisive_cbdp_witness" not in result:
        return False
    return algorithm == "bdpt" or "bypass_obstruction_witnesses" in result


def write_checkpoint(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_cbdp_witness(
    parameters: SPNParameters,
    rounds: int,
    boundary: SPNBoundary,
    input_vector: int,
    target_index: int,
    *,
    time_limit: float | None,
    output_flag: bool,
) -> dict[str, Any]:
    """重新求解并导出指定 CBDP 输入向量的可审计轨迹。"""

    model = SPNSuffixModel(
        parameters,
        rounds,
        boundary,
        output_flag=output_flag,
    )
    status = model.check_trail(
        input_vector,
        target_index,
        time_limit=time_limit,
    )
    if status is not SolveStatus.FEASIBLE:
        raise RuntimeError("重新求解决定性 K 向量时没有得到可行轨迹")
    steps = model.trail_witness()
    validate_spn_witness(
        parameters,
        rounds,
        boundary,
        input_vector,
        target_index,
        steps,
    )
    hex_width = (parameters.block_size + 3) // 4
    return {
        "verified": True,
        "boundary": asdict(boundary),
        "input_vector": input_vector,
        "input_hex": f"{input_vector:0{hex_width}x}",
        "target_index": target_index,
        "steps": [
            {
                "boundary": asdict(step.boundary),
                "state": step.state,
                "state_hex": f"{step.state:0{hex_width}x}",
                "hamming_weight": step.state.bit_count(),
            }
            for step in steps
        ],
    }


def build_decisive_witness(
    parameters: SPNParameters,
    rounds: int,
    result: SearchResult,
    target_index: int,
    *,
    time_limit: float | None,
    output_flag: bool,
) -> dict[str, Any] | None:
    """为最外层 Stopping Rule 1 导出可审计的 CBDP 轨迹。"""
    if result.reason is not StopReason.K_REACHABLE:
        return None
    decisive = result.trace[-1]
    if not isinstance(decisive.boundary, SPNBoundary):
        raise TypeError("决定性轨迹不是 SPN 边界")
    if decisive.decisive_vector is None:
        raise RuntimeError("Stopping Rule 1 缺少决定性 K 向量")
    return build_cbdp_witness(
        parameters,
        rounds,
        decisive.boundary,
        decisive.decisive_vector,
        target_index,
        time_limit=time_limit,
        output_flag=output_flag,
    )


def build_bypass_obstruction_witnesses(
    parameters: SPNParameters,
    rounds: int,
    result: SearchResult,
    target_index: int,
    *,
    time_limit: float | None,
    output_flag: bool,
) -> list[dict[str, Any]]:
    """为记录到的 K-BDPT 旁路阻塞点逐一重放 CBDP 轨迹。"""
    hex_width = (parameters.block_size + 3) // 4
    witnesses: list[dict[str, Any]] = []
    for entry in result.trace:
        if entry.bypass_obstruction_vector is None:
            continue
        if not isinstance(entry.boundary, SPNBoundary):
            raise TypeError("旁路来源不是 SPN 边界")
        if not isinstance(entry.bypass_obstruction_boundary, SPNBoundary):
            raise TypeError("旁路阻塞点不是 SPN 边界")
        witnesses.append(
            {
                "source_secret_key_index": entry.secret_key_index,
                "source_boundary": asdict(entry.boundary),
                "source_l_prime": [
                    {
                        "vector": vector,
                        "hex": f"{vector:0{hex_width}x}",
                    }
                    for vector in entry.bypass_l_prime or ()
                ],
                "bypass_parity": entry.bypass_parity,
                "bypass_reason": entry.bypass_reason,
                "obstruction": build_cbdp_witness(
                    parameters,
                    rounds,
                    entry.bypass_obstruction_boundary,
                    entry.bypass_obstruction_vector,
                    target_index,
                    time_limit=time_limit,
                    output_flag=output_flag,
                ),
            }
        )
    return witnesses


def main() -> int:
    args = parse_args()
    if args.algorithm == "bdpt" and args.key_bit_order != "ascending":
        raise ValueError("--key-bit-order 只适用于 K-BDPT 模式")
    key_bit_order = (
        args.key_bit_order if args.algorithm != "bdpt" else None
    )
    config = load_config(args.experiment)
    parameters = PARAMETERS[str(config["cipher"])]
    rounds = int(config["rounds"])
    layout = PAPER_LAYOUTS[str(config["cipher"])]
    active = active_indices_from_layout_pattern(
        str(config["input_pattern"]),
        layout,
    )
    if args.constant_values is None:
        initial_state = theoretical_unknown_constant_cube_state(
            parameters.block_size, active
        )
        constant_semantics = {"mode": "unknown"}
    else:
        normalized_values = compact_pattern(args.constant_values)
        constants = constant_values_from_layout_pattern(
            str(config["input_pattern"]),
            layout,
            normalized_values,
        )
        initial_state = theoretical_known_constant_cube_state(
            parameters.block_size,
            active,
            constants,
        )
        constant_semantics = {
            "mode": "known",
            "values_in_print_order": normalized_values,
        }
    algorithm_suffix = (
        "" if args.algorithm == "bdpt" else f"_{args.algorithm.replace('-', '_')}"
    )
    if key_bit_order is not None:
        algorithm_suffix += f"_key_{key_bit_order}"
    output = args.output or Path(
        f"output/results/table5_{args.experiment}{algorithm_suffix}.json"
    )
    if output.exists():
        payload = json.loads(output.read_text(encoding="utf-8"))
        if payload.get("case") != args.experiment:
            raise ValueError("已有检查点的实验配置与当前命令不一致")
        if payload.get("algorithm", "bdpt") != args.algorithm:
            raise ValueError("已有检查点的搜索算法与当前命令不一致")
        if payload.get("algorithm_version") != ALGORITHM_VERSIONS[args.algorithm]:
            raise ValueError(
                "已有检查点使用旧算法语义，请使用新的 --output 路径"
            )
        if payload.get("constant_semantics", {"mode": "unknown"}) != constant_semantics:
            raise ValueError("已有检查点的常量语义与当前命令不一致")
        if payload.get("key_bit_order") != key_bit_order:
            raise ValueError("已有检查点的轮密钥比特顺序与当前命令不一致")
        if payload.get("config") != config:
            raise ValueError(
                "已有检查点由旧配置生成，请移动旧文件或使用新的 --output 路径"
            )
    else:
        payload = initial_payload(
            args.experiment,
            config,
            parameters,
            args.algorithm,
            constant_semantics,
            key_bit_order,
        )

    targets = (
        list(range(parameters.block_size))
        if args.targets is None
        else sorted(set(args.targets))
    )
    if any(index < 0 or index >= parameters.block_size for index in targets):
        raise ValueError("目标位超出密码状态范围")

    if args.algorithm == "k-bdpt":
        parts = spn_k_bdpt_parts(
            parameters,
            rounds,
            key_bit_order=args.key_bit_order,
        )
        search = search_k_bdpt
    elif args.algorithm == "k-bdpt-literal":
        parts = spn_k_bdpt_parts(
            parameters,
            rounds,
            key_bit_order=args.key_bit_order,
        )
        search = search_k_bdpt_literal
    else:
        parts = spn_search_parts(parameters, rounds)
        search = search_bdpt

    for target_index in targets:
        key = str(target_index)
        existing_result = payload["results"].get(key)
        if existing_result is not None and (
            not args.record_witness
            or has_recorded_witness(existing_result, args.algorithm)
        ):
            print(f"跳过已完成目标位 {target_index}")
            continue
        if existing_result is not None:
            print(f"目标位 {target_index} 缺少审计证据，重新执行")
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
        if args.algorithm == "bdpt":
            result = search(initial_state, target_index, parts, oracle)
        else:
            result = search(
                initial_state,
                target_index,
                parts,
                oracle,
                record_bypass_provenance=args.record_witness,
            )
        payload["results"][key] = {
            "parity": result.parity.value,
            "reason": result.reason.value,
            "elapsed_seconds": time.perf_counter() - started,
            "oracle_calls": oracle.calls,
            "cache_hits": oracle.cache_hits,
            "trace": [asdict(entry) for entry in result.trace],
        }
        if args.record_witness:
            payload["results"][key]["decisive_cbdp_witness"] = (
                build_decisive_witness(
                    parameters,
                    rounds,
                    result,
                    target_index,
                    time_limit=args.time_limit,
                    output_flag=args.gurobi_log,
                )
            )
            if args.algorithm != "bdpt":
                payload["results"][key]["bypass_obstruction_witnesses"] = (
                    build_bypass_obstruction_witnesses(
                        parameters,
                        rounds,
                        result,
                        target_index,
                        time_limit=args.time_limit,
                        output_flag=args.gurobi_log,
                    )
                )
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
