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
    search_k_bdpt_literal,
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
    assert result.trace[-1].decisive_vector == 0b11


def test_stopping_rule_1_checks_k_until_any_vector_reaches() -> None:
    initial = BDPTState(
        width=2,
        k=frozenset({0b01, 0b10}),
        l=frozenset({0b00}),
    )
    queried: list[int] = []

    def oracle(boundary: object, vector: int, target: int) -> bool:
        queried.append(vector)
        return vector == 0b10

    result = search_bdpt(
        initial,
        0,
        [SearchPart(Boundary(0), _identity)],
        oracle,
    )

    assert result.parity is Parity.UNKNOWN
    assert result.reason is StopReason.K_REACHABLE
    assert result.trace[-1].decisive_vector == 0b10
    assert queried == [0b01, 0b10]


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


def test_algorithm_2_returns_one_after_last_propagation() -> None:
    initial = BDPTState(width=2, l=frozenset({0b01}))

    def cancel_last_vector(state: BDPTState) -> BDPTState:
        return BDPTState(width=2)

    part = SearchPart(Boundary(0), cancel_last_vector)
    result = search_bdpt(initial, 0, [part], lambda boundary, vector, target: True)

    assert result.parity is Parity.ONE
    assert result.reason is StopReason.FINAL_ONE


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

    literal = search_k_bdpt_literal(initial, 0, parts, oracle)
    assert literal.parity is Parity.UNKNOWN
    assert literal.trace[0].key_bypassed is False


def test_k_bdpt_uses_semantic_final_state_for_paper_example_style_bypass() -> None:
    initial = BDPTState(width=2, l=frozenset({0b10}))
    key_part = SearchPart(
        Boundary(0),
        lambda state: xor_secret_key(state, 0),
        secret_key_index=0,
    )

    result = search_k_bdpt(
        initial,
        0,
        [key_part],
        lambda boundary, vector, target: True,
        record_bypass_provenance=True,
    )

    assert result.parity is Parity.ZERO
    assert result.trace[0].key_bypassed is True
    assert result.trace[0].bypass_parity == "zero"
    assert result.trace[0].bypass_reason == "final_zero"
    assert result.trace[0].bypass_l_prime is None
    assert result.trace[0].bypass_obstruction_vector is None


def test_k_bdpt_literal_mode_keeps_algorithm_2_terminal_return_one() -> None:
    initial = BDPTState(width=2, l=frozenset({0b10}))
    key_part = SearchPart(
        Boundary(0),
        lambda state: xor_secret_key(state, 0),
        secret_key_index=0,
    )

    result = search_k_bdpt_literal(
        initial,
        0,
        [key_part],
        lambda boundary, vector, target: True,
    )

    assert result.parity is Parity.ONE
    assert result.trace[0].key_bypassed is False
    assert result.trace[0].k_after_propagation == 1
    assert result.trace[0].bypass_reason == "final_one"


def test_k_bdpt_records_failed_bypass_provenance() -> None:
    key_boundary = Boundary(0)
    child_boundary = Boundary(1)
    obstruction_boundary = Boundary(2)

    def promote_l_to_k(state: BDPTState) -> BDPTState:
        return BDPTState(width=3, k=state.l, l=state.l)

    parts = [
        SearchPart(
            key_boundary,
            lambda state: xor_secret_key(state, 0),
            secret_key_index=0,
        ),
        SearchPart(child_boundary, promote_l_to_k),
        SearchPart(obstruction_boundary, _identity),
    ]

    def oracle(boundary: object, vector: int, target: int) -> bool:
        return boundary == key_boundary or vector == 0b011

    result = search_k_bdpt(
        BDPTState(width=3, l=frozenset({0b010, 0b101})),
        0,
        parts,
        oracle,
        record_bypass_provenance=True,
    )

    key_trace = result.trace[0]
    assert key_trace.secret_key_index == 0
    assert key_trace.key_bypassed is False
    assert key_trace.decisive_vector is None
    assert key_trace.bypass_l_count == 1
    assert key_trace.bypass_parity == "unknown"
    assert key_trace.bypass_reason == "k_reachable"
    assert key_trace.bypass_l_prime == (0b011,)
    assert key_trace.bypass_obstruction_boundary == obstruction_boundary
    assert key_trace.bypass_obstruction_vector == 0b011


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
