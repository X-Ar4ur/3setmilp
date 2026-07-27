import pytest

from three_set_milp.ciphers.simon import (
    SIMON32,
    propagate_core,
    propagate_public_swap,
)
from three_set_milp.core.bdpt import BDPTState, Parity
from three_set_milp.milp import GurobiModel, GurobiUnavailableError, SolveStatus
from three_set_milp.milp.simon import SimonBoundary, scbdp_simon


def _require_gurobi() -> None:
    try:
        model = GurobiModel("simon_license_check")
        variable = model.add_binary_vector("x", 1)
        model.fix_vector(variable, 0)
        model.solve()
    except GurobiUnavailableError as error:
        pytest.skip(str(error))


def _one_public_round(input_vector: int) -> BDPTState:
    state = BDPTState(width=32, k=frozenset({input_vector}))
    for output_index in range(16):
        state = propagate_core(state, SIMON32, output_index)
    return propagate_public_swap(state, SIMON32)


@pytest.mark.parametrize("input_vector", [1, 1 << 16])
def test_compact_one_round_model_matches_exact_bdpt(input_vector: int) -> None:
    _require_gurobi()
    expected = _one_public_round(input_vector)
    for target_index in range(32):
        status = scbdp_simon(
            SIMON32,
            rounds=1,
            boundary=SimonBoundary(0, 0),
            input_vector=input_vector,
            target_index=target_index,
        )
        reachable = status is SolveStatus.FEASIBLE
        assert status is not SolveStatus.UNDETERMINED
        assert reachable == (
            expected.parity(1 << target_index) is Parity.UNKNOWN
        )

