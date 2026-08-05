import pytest

from three_set_milp.ciphers.speck import SpeckParameters, propagate_round
from three_set_milp.core.bdpt import BDPTState, Parity
from three_set_milp.milp import GurobiModel, GurobiUnavailableError, SolveStatus
from three_set_milp.milp.speck import SpeckBoundary, SpeckSuffixModel


TINY_SPECK = SpeckParameters(word_size=3, alpha=1, beta=1)


def _require_gurobi() -> None:
    try:
        model = GurobiModel("speck_license_check")
        variable = model.add_binary_vector("x", 1)
        model.fix_vector(variable, 0)
        model.solve()
    except GurobiUnavailableError as error:
        pytest.skip(str(error))


@pytest.mark.parametrize("input_vector", [1, 1 << 3, 0b101011])
def test_speck_one_round_model_matches_exact_public_bdpt(
    input_vector: int,
) -> None:
    _require_gurobi()
    expected = propagate_round(
        BDPTState(width=TINY_SPECK.state_width, k=frozenset({input_vector})),
        TINY_SPECK,
        include_secret_key=False,
    )
    suffix = SpeckSuffixModel(TINY_SPECK, 1, SpeckBoundary(0, 0))
    for target_index in range(TINY_SPECK.block_size):
        status = suffix.check_trail(input_vector, target_index)
        assert status is not SolveStatus.UNDETERMINED
        assert (status is SolveStatus.FEASIBLE) == (
            expected.parity(1 << target_index) is Parity.UNKNOWN
        )

