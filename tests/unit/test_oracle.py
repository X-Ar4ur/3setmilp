from itertools import product

from three_set_milp.core.bdpt import Parity
from three_set_milp.core.oracle import (
    cube_multiset,
    exact_state_from_multiset,
    state_matches_family,
    theoretical_known_constant_cube_state,
    theoretical_unknown_constant_cube_state,
    unknown_constant_cube_state,
)


def test_exact_state_from_concrete_cube_has_no_unknown() -> None:
    multiset = cube_multiset(
        width=3,
        active_indices={1, 2},
        constants={0: 1},
    )
    state = exact_state_from_multiset(multiset, width=3)

    assert state.k == frozenset()
    assert Parity.UNKNOWN not in state.parity_table()
    assert state.parity(0b110) is Parity.ONE
    assert state.parity(0b111) is Parity.ONE


def test_unknown_single_constant_matches_paper_initial_state() -> None:
    state = unknown_constant_cube_state(width=3, active_indices={1, 2})

    assert state.k == frozenset({0b111})
    assert state.l == frozenset({0b110})


def test_theoretical_initial_state_matches_exhaustive_oracle() -> None:
    exhaustive = unknown_constant_cube_state(width=4, active_indices={1, 2})
    theoretical = theoretical_unknown_constant_cube_state(
        width=4, active_indices={1, 2}
    )

    assert theoretical == exhaustive
    assert theoretical.k == frozenset({0b0111, 0b1110})
    assert theoretical.l == frozenset({0b0110})


def test_initial_state_exactly_describes_all_constant_assignments() -> None:
    width = 4
    active = {1, 2}
    inactive = [0, 3]
    multisets = []
    for bits in product((0, 1), repeat=len(inactive)):
        constants = dict(zip(inactive, bits, strict=True))
        multisets.append(cube_multiset(width, active, constants))

    state = theoretical_unknown_constant_cube_state(width, active)
    assert state_matches_family(state, multisets)


def test_known_constant_initial_state_matches_exact_cube() -> None:
    constants = {0: 1, 3: 0}
    exact = exact_state_from_multiset(
        cube_multiset(
            width=4,
            active_indices={1, 2},
            constants=constants,
        ),
        width=4,
    )
    theoretical = theoretical_known_constant_cube_state(
        width=4,
        active_indices={1, 2},
        constants=constants,
    )

    assert theoretical == exact
    assert theoretical.k == frozenset()
    assert theoretical.l == frozenset({0b0110, 0b0111})
