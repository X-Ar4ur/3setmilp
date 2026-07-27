import pytest

from three_set_milp.ciphers.lblock import propagate_public_round
from three_set_milp.core.bdpt import BDPTState, Parity
from three_set_milp.milp import GurobiModel, GurobiUnavailableError, SolveStatus
from three_set_milp.milp.lblock import LBlockBoundary, LBlockSuffixModel


def _require_gurobi() -> None:
    try:
        model = GurobiModel("lblock_license_check")
        variable = model.add_binary_vector("x", 1)
        model.fix_vector(variable, 0)
        model.solve()
    except GurobiUnavailableError as error:
        pytest.skip(str(error))


@pytest.mark.parametrize("input_vector", [1, 1 << 32])
def test_lblock_one_round_model_matches_exact_public_bdpt(input_vector: int) -> None:
    _require_gurobi()
    expected = propagate_public_round(
        BDPTState(width=64, k=frozenset({input_vector}))
    )
    suffix = LBlockSuffixModel(1, LBlockBoundary(0, 0))
    for target_index in range(64):
        status = suffix.check_trail(input_vector, target_index)
        assert status is not SolveStatus.UNDETERMINED
        assert (status is SolveStatus.FEASIBLE) == (
            expected.parity(1 << target_index) is Parity.UNKNOWN
        )
