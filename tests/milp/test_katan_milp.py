import pytest

from three_set_milp.ciphers.katan import KatanParameters, propagate_clock
from three_set_milp.core.bdpt import BDPTState, Parity
from three_set_milp.milp import GurobiModel, GurobiUnavailableError, SolveStatus
from three_set_milp.milp.katan import KatanBoundary, KatanSuffixModel


TINY_KATAN = KatanParameters(
    block_size=11,
    l1_size=5,
    l2_size=6,
    x_taps=(4, 1, 2, 0, 3),
    y_taps=(5, 1, 4, 0, 3, 2),
    clocks_per_round=1,
)


def _require_gurobi() -> None:
    try:
        model = GurobiModel("katan_license_check")
        variable = model.add_binary_vector("x", 1)
        model.fix_vector(variable, 0)
        model.solve()
    except GurobiUnavailableError as error:
        pytest.skip(str(error))


@pytest.mark.parametrize("input_vector", [1, 1 << 3, 0b101011])
def test_katan_one_clock_model_matches_exact_public_bdpt(
    input_vector: int,
) -> None:
    _require_gurobi()
    expected = propagate_clock(
        BDPTState(width=TINY_KATAN.state_width, k=frozenset({input_vector})),
        TINY_KATAN,
        0,
        include_secret_key=False,
    )
    suffix = KatanSuffixModel(TINY_KATAN, 1, KatanBoundary(0, 0))
    for target_index in range(TINY_KATAN.block_size):
        status = suffix.check_trail(input_vector, target_index)
        assert status is not SolveStatus.UNDETERMINED
        assert (status is SolveStatus.FEASIBLE) == (
            expected.parity(1 << target_index) is Parity.UNKNOWN
        )
