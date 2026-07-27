from dataclasses import dataclass

from three_set_milp.core.bdpt import BDPTState, Parity
from three_set_milp.core.bitvector import from_index_bits, unit_vector
from three_set_milp.core.propagation import propagate_sbox, xor_secret_key
from three_set_milp.search.bdpt_search import (
    CachedSuffixOracle,
    SearchPart,
    StopReason,
    search_bdpt,
    search_k_bdpt,
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
    result = search_bdpt(initial, 1, parts, lambda boundary, vector, target: True)

    assert result.parity is Parity.ONE
    assert result.reason is StopReason.FINAL_ONE
    assert len(result.trace) == 2


def test_final_state_is_checked_after_last_propagation() -> None:
    initial = BDPTState(width=2, l=frozenset({0b01}))

    def cancel_last_vector(state: BDPTState) -> BDPTState:
        return BDPTState(width=2)

    part = SearchPart(Boundary(0), cancel_last_vector)
    result = search_bdpt(initial, 0, [part], lambda boundary, vector, target: True)

    assert result.parity is Parity.ZERO
    assert result.reason is StopReason.FINAL_ZERO


def test_k_bdpt_reproduces_followup_paper_example_2() -> None:
    truth_table = []
    for value in range(16):
        x0 = (value >> 0) & 1
        x1 = (value >> 1) & 1
        x2 = (value >> 2) & 1
        x3 = (value >> 3) & 1
        truth_table.append(
            from_index_bits(
                [
                    (x0 & x1 & x2) ^ (x0 & x1 & x2 & x3),
                    x0,
                    x1,
                    x3,
                ]
            )
        )

    key_boundary = Boundary(0)
    sbox_boundary = Boundary(1)
    parts = [
        SearchPart(
            key_boundary,
            lambda state: xor_secret_key(state, 2),
            secret_key_index=2,
        ),
        SearchPart(
            sbox_boundary,
            lambda state: propagate_sbox(state, truth_table, 4),
        ),
    ]
    initial = BDPTState(
        width=4,
        l=frozenset(
            {
                from_index_bits([1, 1, 0, 1]),
                from_index_bits([1, 1, 0, 0]),
            }
        ),
    )

    def oracle(boundary: object, vector: int, target: int) -> bool:
        state = propagate_sbox(
            BDPTState(width=4, k=frozenset({vector})),
            truth_table,
            4,
        )
        return state.parity(unit_vector(target, 4)) is Parity.UNKNOWN

    assert search_bdpt(initial, 0, parts, oracle).parity is Parity.UNKNOWN
    improved = search_k_bdpt(initial, 0, parts, oracle)
    assert improved.parity is Parity.ZERO
    assert improved.trace[0].key_bypassed is True


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
