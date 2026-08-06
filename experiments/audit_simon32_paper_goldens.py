"""逐检查点对拍主论文 SIMON32 示例、Table 3 和 Table 4。"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from three_set_milp.ciphers.simon import (
    SIMON32,
    format_paper_state,
    parse_paper_state,
    propagate_core,
    propagate_key_and_swap,
)
from three_set_milp.core.bdpt import BDPTState, Parity
from three_set_milp.core.order import reduce_k, reduce_l
from three_set_milp.core.oracle import theoretical_unknown_constant_cube_state
from three_set_milp.core.propagation import permute_state, xor_secret_key
from three_set_milp.search.bdpt_search import (
    CachedSuffixOracle,
    StopReason,
    search_bdpt,
)
from three_set_milp.search.simon import SimonGurobiOracle, simon_search_parts


PAPER_K_SIZES = (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
PAPER_L_SIZES = (1, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
PAPER_EXPECTED_LEFT = "????????????????"
PAPER_EXPECTED_RIGHT = "?b??????b??????b"


def _paper_vector(left: str, right: str) -> int:
    return parse_paper_state(left + right, SIMON32)


L1 = _paper_vector("1011111111111111", "0111111111111111")
L2 = _paper_vector("1001111111111111", "1111111111111111")
L3 = L1
L4 = _paper_vector("1011111111111111", "1111111111111111")
EXPECTED_K = _paper_vector("1111111111111111", "1011111111111111")
L5 = _paper_vector("0111111111111111", "1011111111111111")


def _vector_record(vector: int) -> dict[str, Any]:
    return {
        "internal_hex": f"0x{vector:08x}",
        "paper_bits": format_paper_state(vector, SIMON32),
    }


def _vectors(vectors: Any) -> list[dict[str, Any]]:
    return [_vector_record(vector) for vector in sorted(vectors)]


def _stable_hash(vectors: Any) -> str:
    canonical = "\n".join(f"{vector:08x}" for vector in sorted(vectors))
    return hashlib.sha256(canonical.encode("ascii")).hexdigest()


def _state_record(state: BDPTState) -> dict[str, Any]:
    return {
        "k_size": len(state.k),
        "l_size": len(state.l),
        "k_hash": _stable_hash(state.k),
        "l_hash": _stable_hash(state.l),
        "k": _vectors(state.k),
        "l": _vectors(state.l),
    }


def paper_bit_mapping() -> dict[str, Any]:
    mapping = []
    for paper_position, internal_index in enumerate(SIMON32.paper_print_indices):
        word = "left" if paper_position < SIMON32.word_size else "right"
        bit_in_word = SIMON32.word_size - 1 - (paper_position % SIMON32.word_size)
        mapping.append(
            {
                "paper_position": paper_position,
                "paper_label": f"{word}[{bit_in_word}]",
                "internal_m": internal_index,
            }
        )
    return {
        "layout": "left[15..0],right[15..0]",
        "rightmost_paper_position": 31,
        "rightmost_internal_m": mapping[-1]["internal_m"],
        "positions": mapping,
    }


def q_1_15_golden() -> dict[str, Any]:
    contributions: dict[int, list[int]] = {}
    for source in (L1, L2):
        output = propagate_core(
            BDPTState(width=32, l=frozenset({source})),
            SIMON32,
            output_index=15,
        )
        if output.k:
            raise AssertionError("论文 Q_(1,15) singleton 传播不应产生 K")
        contributions[source] = sorted(output.l)

    counts = Counter(vector for outputs in contributions.values() for vector in outputs)
    odd = frozenset(vector for vector, count in counts.items() if count % 2 == 1)
    combined = propagate_core(
        BDPTState(width=32, l=frozenset({L1, L2})),
        SIMON32,
        output_index=15,
    )
    expected_l = frozenset({L3, L4})
    expected_counts = Counter({L3: 1, L2: 2, L4: 1})
    return {
        "name": "Q_(1,15)",
        "input": _state_record(BDPTState(width=32, l=frozenset({L1, L2}))),
        "per_input": [
            {
                "source": _vector_record(source),
                "outputs": _vectors(outputs),
            }
            for source, outputs in contributions.items()
        ],
        "occurrences": [
            {"vector": _vector_record(vector), "count": count}
            for vector, count in sorted(counts.items())
        ],
        "odd_after_mod2": _vectors(odd),
        "actual": _state_record(combined),
        "expected": _state_record(BDPTState(width=32, l=expected_l)),
        "checks": {
            "occurrences_exact": counts == expected_counts,
            "odd_set_exact": odd == expected_l,
            "combined_k_exact": combined.k == frozenset(),
            "combined_l_exact": combined.l == expected_l,
        },
    }


def q_1_16_golden() -> dict[str, Any]:
    initial = BDPTState(width=32, l=frozenset({L3, L4}))
    key_indices = range(SIMON32.word_size, SIMON32.block_size)
    raw_additions: list[dict[str, Any]] = []
    raw_k = set(initial.k)
    for ell in sorted(initial.l):
        for index in key_indices:
            if ell & (1 << index) == 0:
                generated = ell | (1 << index)
                raw_k.add(generated)
                raw_additions.append(
                    {
                        "source_l": _vector_record(ell),
                        "key_internal_index": index,
                        "generated_k": _vector_record(generated),
                    }
                )

    k_after_reduce0 = reduce_k(raw_k, 32)
    l_before_reduce1 = initial.l
    l_after_reduce1 = reduce_l(k_after_reduce0, l_before_reduce1, 32)
    before_swap = BDPTState(
        width=32,
        k=k_after_reduce0,
        l=l_after_reduce1,
    )
    swap = tuple(range(16, 32)) + tuple(range(16))
    staged_final = permute_state(before_swap, swap)

    sequential = initial
    rule4_steps = []
    for index in key_indices:
        before = sequential
        sequential = xor_secret_key(sequential, index)
        if sequential != before:
            rule4_steps.append(
                {
                    "key_internal_index": index,
                    "before": _state_record(before),
                    "after": _state_record(sequential),
                }
            )
    direct = propagate_key_and_swap(initial, SIMON32)
    expected = BDPTState(
        width=32,
        k=frozenset({EXPECTED_K}),
        l=frozenset({L5}),
    )
    return {
        "name": "Q_(1,16)",
        "before_key_xor": _state_record(initial),
        "rule4_raw_additions": raw_additions,
        "k_before_reduce0": _vectors(raw_k),
        "k_after_reduce0": _vectors(k_after_reduce0),
        "l_before_reduce1": _vectors(l_before_reduce1),
        "l_after_reduce1": _vectors(l_after_reduce1),
        "before_swap": _state_record(before_swap),
        "after_swap": _state_record(staged_final),
        "sequential_rule4_changes": rule4_steps,
        "direct_core_output": _state_record(direct),
        "expected": _state_record(expected),
        "checks": {
            "single_rule4_addition": len(raw_additions) == 1,
            "generated_vector_exact": {
                item["generated_k"]["internal_hex"] for item in raw_additions
            }
            == {_vector_record(L4)["internal_hex"]},
            "reduce0_exact": k_after_reduce0 == frozenset({L4}),
            "reduce1_exact": l_after_reduce1 == frozenset({L3}),
            "staged_final_exact": staged_final == expected,
            "direct_final_exact": direct == expected,
            "staged_equals_direct": staged_final == direct,
        },
    }


def local_goldens() -> dict[str, Any]:
    first = q_1_15_golden()
    second = q_1_16_golden()
    return {
        "bit_mapping": paper_bit_mapping(),
        "q_1_15": first,
        "q_1_16": second,
        "passed": all(first["checks"].values()) and all(second["checks"].values()),
    }


def _initial_state() -> BDPTState:
    return theoretical_unknown_constant_cube_state(
        SIMON32.block_size,
        set(range(SIMON32.block_size)) - {15},
    )


def _query_record(vector: int, reachable: bool) -> dict[str, Any]:
    return {"vector": _vector_record(vector), "reachable": reachable}


def _new_round_stats(round_number: int) -> dict[str, Any]:
    return {
        "round": round_number,
        "k_pruned": 0,
        "l_pruned": 0,
        "scbdp_reachable": 0,
        "scbdp_unreachable": 0,
        "stopping_rule": None,
    }


def run_pruned_target(
    target_index: int,
    *,
    rounds: int = 14,
    time_limit: float | None = None,
    gurobi_log: bool = False,
) -> dict[str, Any]:
    """按 Algorithm 2 原顺序执行，并保留测试入口需要的完整状态。"""
    initial = _initial_state()
    parts = simon_search_parts(SIMON32, rounds)
    oracle = CachedSuffixOracle(
        SimonGurobiOracle(
            SIMON32,
            rounds,
            time_limit=time_limit,
            output_flag=gurobi_log,
        )
    )
    current = initial.normalized()
    part_records: list[dict[str, Any]] = []
    raw_round_outputs: list[dict[str, Any]] = []
    paper_checkpoints = [{"round": 0, "state": _state_record(current), "source": "initial"}]
    round_stats = {index: _new_round_stats(index + 1) for index in range(rounds)}
    parity = Parity.ONE
    reason = StopReason.FINAL_ONE
    terminal_round: int | None = None

    for part in parts:
        boundary = part.boundary
        stats = round_stats[boundary.round_index]
        record: dict[str, Any] = {
            "i": boundary.round_index + 1,
            "j": boundary.part_index,
            "input": _state_record(current),
        }

        k_results = []
        decisive_k: int | None = None
        for vector in sorted(current.k):
            reachable = oracle(boundary, vector, target_index)
            k_results.append(_query_record(vector, reachable))
            stats["scbdp_reachable" if reachable else "scbdp_unreachable"] += 1
            if reachable:
                decisive_k = vector
                break
            stats["k_pruned"] += 1
        record["k_scbdp"] = k_results
        if decisive_k is not None:
            record["stopping_rule"] = 1
            record["decisive_vector"] = _vector_record(decisive_k)
            part_records.append(record)
            stats["stopping_rule"] = 1
            parity = Parity.UNKNOWN
            reason = StopReason.K_REACHABLE
            terminal_round = boundary.round_index + 1
            break

        survivors = set()
        l_results = []
        for vector in sorted(current.l):
            reachable = oracle(boundary, vector, target_index)
            l_results.append(_query_record(vector, reachable))
            stats["scbdp_reachable" if reachable else "scbdp_unreachable"] += 1
            if reachable:
                survivors.add(vector)
            else:
                stats["l_pruned"] += 1
        record["l_scbdp"] = l_results
        record["pruned_l_prime"] = _vectors(survivors)
        if not survivors:
            empty = BDPTState(width=32)
            record["stopping_rule"] = 2
            record["propagated"] = None
            part_records.append(record)
            stats["stopping_rule"] = 2
            parity = Parity.ZERO
            reason = StopReason.L_EMPTY
            terminal_round = (
                boundary.round_index
                if boundary.part_index == 0
                else boundary.round_index + 1
            )
            paper_checkpoints.append(
                {
                    "round": terminal_round,
                    "state": _state_record(empty),
                    "source": f"stopping_rule_2_at_Q_({boundary.round_index + 1},{boundary.part_index})",
                }
            )
            break

        pruned = BDPTState(width=32, l=frozenset(survivors))
        if boundary.part_index == 0 and boundary.round_index > 0:
            paper_checkpoints.append(
                {
                    "round": boundary.round_index,
                    "state": _state_record(pruned),
                    "source": f"after_pruning_at_Q_({boundary.round_index + 1},0)",
                }
            )
        singleton_outputs = []
        l_occurrences: Counter[int] = Counter()
        for vector in sorted(survivors):
            singleton_output = part.propagate(
                BDPTState(width=32, l=frozenset({vector}))
            )
            l_occurrences.update(singleton_output.l)
            singleton_outputs.append(
                {
                    "source_l": _vector_record(vector),
                    "output": _state_record(singleton_output),
                }
            )
        record["per_survivor_propagation"] = singleton_outputs
        record["l_output_occurrences_before_mod2"] = [
            {"vector": _vector_record(vector), "count": count}
            for vector, count in sorted(l_occurrences.items())
        ]
        current = part.propagate(pruned)
        record["stopping_rule"] = None
        record["propagated"] = _state_record(current)
        part_records.append(record)
        if boundary.part_index == SIMON32.word_size:
            raw_round_outputs.append(
                {
                    "round": boundary.round_index + 1,
                    "state": _state_record(current),
                }
            )
    else:
        terminal_round = rounds
        round_stats[rounds - 1]["stopping_rule"] = 3

    diagnostic_calls = oracle.calls
    diagnostic_cache_hits = oracle.cache_hits
    reference = search_bdpt(initial, target_index, parts, oracle)
    reference_match = reference.parity is parity and reference.reason is reason

    checkpoint_by_round = {entry["round"]: entry for entry in paper_checkpoints}
    comparison = []
    first_divergence: dict[str, Any] | None = None
    for round_index, (expected_k, expected_l) in enumerate(
        zip(PAPER_K_SIZES, PAPER_L_SIZES, strict=True)
    ):
        checkpoint = checkpoint_by_round.get(round_index)
        if checkpoint is not None:
            actual_k = checkpoint["state"]["k_size"]
            actual_l = checkpoint["state"]["l_size"]
            source = checkpoint["source"]
        elif reason is StopReason.L_EMPTY and terminal_round is not None and round_index > terminal_round:
            actual_k = 0
            actual_l = 0
            source = "inferred_after_stopping_rule_2"
        else:
            actual_k = None
            actual_l = None
            source = "missing_checkpoint"
        matches = actual_k == expected_k and actual_l == expected_l
        row = {
            "round": round_index,
            "expected_k": expected_k,
            "expected_l": expected_l,
            "actual_k": actual_k,
            "actual_l": actual_l,
            "source": source,
            "matches": matches,
        }
        comparison.append(row)
        if not matches and first_divergence is None:
            first_divergence = row

    return {
        "target_index": target_index,
        "result": {"parity": parity.value, "reason": reason.value},
        "reference_algorithm": {
            "parity": reference.parity.value,
            "reason": reference.reason.value,
            "matches_diagnostic_runner": reference_match,
        },
        "oracle": {
            "diagnostic_calls": diagnostic_calls,
            "diagnostic_cache_hits": diagnostic_cache_hits,
            "calls_after_reference_replay": oracle.calls,
            "cache_hits_after_reference_replay": oracle.cache_hits,
        },
        "paper_checkpoints": paper_checkpoints,
        "raw_round_outputs_before_next_round_pruning": raw_round_outputs,
        "round_stats": [round_stats[index] for index in range(rounds)],
        "part_records": part_records,
        "paper_size_comparison": comparison,
        "FIRST_DIVERGENCE": first_divergence,
    }


def _paper_position_for_internal(index: int) -> int:
    return SIMON32.paper_print_indices.index(index)


def run_all_targets(
    *,
    rounds: int = 14,
    time_limit: float | None = None,
    gurobi_log: bool = False,
) -> dict[str, Any]:
    initial = _initial_state()
    parts = simon_search_parts(SIMON32, rounds)
    results = []
    parities: dict[int, str] = {}
    for target_index in range(SIMON32.block_size):
        oracle = CachedSuffixOracle(
            SimonGurobiOracle(
                SIMON32,
                rounds,
                time_limit=time_limit,
                output_flag=gurobi_log,
            )
        )
        result = search_bdpt(initial, target_index, parts, oracle)
        parities[target_index] = result.parity.value
        results.append(
            {
                "internal_m": target_index,
                "paper_position": _paper_position_for_internal(target_index),
                "parity": result.parity.value,
                "reason": result.reason.value,
                "oracle_calls": oracle.calls,
                "cache_hits": oracle.cache_hits,
            }
        )

    symbols = {"zero": "b", "one": "1", "unknown": "?"}
    printed = "".join(symbols[parities[index]] for index in SIMON32.paper_print_indices)
    left = printed[:16]
    right = printed[16:]
    balanced = sorted(index for index, parity in parities.items() if parity == "zero")
    return {
        "results_by_internal_m": results,
        "balanced_internal_positions": balanced,
        "paper_output": {"left": left, "right": right},
        "expected_output": {
            "left": PAPER_EXPECTED_LEFT,
            "right": PAPER_EXPECTED_RIGHT,
        },
        "exact_pattern_match": left == PAPER_EXPECTED_LEFT and right == PAPER_EXPECTED_RIGHT,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solver", action="store_true", help="运行 14 轮 Table 3 目标位")
    parser.add_argument(
        "--all-targets",
        action="store_true",
        help="Table 3 通过后继续运行全部 32 个输出位",
    )
    parser.add_argument("--time-limit", type=float, default=None)
    parser.add_argument("--gurobi-log", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload: dict[str, Any] = {"local_goldens": local_goldens()}
    if not payload["local_goldens"]["passed"]:
        raise AssertionError("SIMON32 局部论文黄金测试失败")
    if args.all_targets and not args.solver:
        raise ValueError("--all-targets 必须与 --solver 一起使用")

    if args.solver:
        table3 = run_pruned_target(
            16,
            time_limit=args.time_limit,
            gurobi_log=args.gurobi_log,
        )
        payload["table3_rightmost"] = table3
        table3_passed = (
            table3["FIRST_DIVERGENCE"] is None
            and table3["result"] == {"parity": "zero", "reason": "l_empty"}
            and table3["reference_algorithm"]["matches_diagnostic_runner"]
        )
        payload["table3_passed"] = table3_passed
        if args.all_targets:
            if not table3_passed:
                raise AssertionError("Table 3 黄金测试失败，不继续运行全部输出位")
            payload["all_targets"] = run_all_targets(
                time_limit=args.time_limit,
                gurobi_log=args.gurobi_log,
            )

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"结果已写入: {args.output}")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
