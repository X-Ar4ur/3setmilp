from dataclasses import dataclass

from three_set_milp.core.bdpt import BDPTState, Parity
from three_set_milp.search.bdpt_search import (
    CachedSuffixOracle,
    SearchPart,
    StopReason,
    search_bdpt,
)


@dataclass(frozen=True)
class Boundary:
    index: int


def _identity(state: BDPTState) -> BDPTState:
    return state


def test_stopping_rule_1_returns_unknown() -> None:
    initial = BDPTState(width=2, k=frozenset({0b11}), l=frozenset({0b10}))
    part = SearchPart(Boundary(0), _identity)
    result = search_bdpt(initial, 0, [part], lambda boundary, vector, target: True)

    assert result.parity is Parity.UNKNOWN
    assert result.reason is StopReason.K_REACHABLE


def test_stopping_rule_2_returns_zero() -> None:
    initial = BDPTState(width=2, l=frozenset({0b10}))
    part = SearchPart(Boundary(0), _identity)
    result = search_bdpt(initial, 0, [part], lambda boundary, vector, target: False)

    assert result.parity is Parity.ZERO
    assert result.reason is StopReason.L_EMPTY


def test_full_propagation_returns_one() -> None:
    initial = BDPTState(width=2, l=frozenset({0b10}))
    parts = [SearchPart(Boundary(0), _identity), SearchPart(Boundary(1), _identity)]
    result = search_bdpt(initial, 0, parts, lambda boundary, vector, target: True)

    assert result.parity is Parity.ONE
    assert result.reason is StopReason.FINAL_ONE
    assert len(result.trace) == 2


def test_k_generated_by_one_part_is_checked_at_next_boundary() -> None:
    initial = BDPTState(width=2, l=frozenset({0b10}))

    def generate_k(state: BDPTState) -> BDPTState:
        return BDPTState(width=2, k=frozenset({0b11}), l=state.l)

    parts = [SearchPart(Boundary(0), generate_k), SearchPart(Boundary(1), _identity)]

    def oracle(boundary: object, vector: int, target: int) -> bool:
        return boundary == Boundary(0) or vector == 0b11

    result = search_bdpt(initial, 0, parts, oracle)
    assert result.parity is Parity.UNKNOWN
    assert result.reason is StopReason.K_REACHABLE


def test_cached_oracle_avoids_duplicate_underlying_queries() -> None:
    underlying_calls = 0

    def underlying(boundary: object, vector: int, target: int) -> bool:
        nonlocal underlying_calls
        underlying_calls += 1
        return True

    oracle = CachedSuffixOracle(underlying)
    boundary = Boundary(0)
    assert oracle(boundary, 1, 0)
    assert oracle(boundary, 1, 0)
    assert underlying_calls == 1
    assert oracle.calls == 2
    assert oracle.cache_hits == 1

