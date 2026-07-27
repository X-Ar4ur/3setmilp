from experiments.reproduce_table3 import (
    PAPER_K,
    PAPER_L,
    build_round_summary,
    compare_table3_prefix,
)
from three_set_milp.core.bdpt import BDPTState, Parity
from three_set_milp.milp.simon import SimonBoundary
from three_set_milp.search.bdpt_search import (
    SearchResult,
    StopReason,
    TraceEntry,
)


def _trace_entry(round_index: int, part_index: int, survivors: int) -> TraceEntry:
    return TraceEntry(
        boundary=SimonBoundary(round_index, part_index),
        k_before=0,
        l_before=max(survivors, 1),
        k_queries=0,
        l_queries=max(survivors, 1),
        l_survivors=survivors,
        k_after_propagation=None if survivors == 0 else 0,
        l_after_propagation=None if survivors == 0 else survivors,
    )


def test_table3_summary_records_l_empty_at_round_output() -> None:
    initial = BDPTState(width=32, k=frozenset({1}), l=frozenset({2}))
    trace = (
        _trace_entry(1, 0, 1),
        _trace_entry(2, 0, 1),
        _trace_entry(3, 0, 2),
        _trace_entry(4, 0, 2),
        _trace_entry(4, 14, 0),
    )
    result = SearchResult(
        parity=Parity.ZERO,
        reason=StopReason.L_EMPTY,
        trace=trace,
    )

    summary = build_round_summary(initial, result)
    assert [entry["k"] for entry in summary] == PAPER_K
    assert [entry["l"] for entry in summary] == PAPER_L
    assert compare_table3_prefix(summary)["matches"] is True


def test_table3_summary_does_not_advance_part_zero_stop() -> None:
    initial = BDPTState(width=32, k=frozenset({1}), l=frozenset({2}))
    result = SearchResult(
        parity=Parity.ZERO,
        reason=StopReason.L_EMPTY,
        trace=(_trace_entry(5, 0, 0),),
    )

    assert build_round_summary(initial, result)[-1] == {
        "round": 5,
        "k": 0,
        "l": 0,
    }
