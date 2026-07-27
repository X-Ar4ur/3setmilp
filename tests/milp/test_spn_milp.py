import pytest

from three_set_milp.ciphers.spn import SPNParameters, propagate_sbox_part
from three_set_milp.core.bdpt import BDPTState, Parity
from three_set_milp.milp import GurobiModel, GurobiUnavailableError, SolveStatus
from three_set_milp.milp.spn import SPNBoundary, SPNSuffixModel


TINY_SPN = SPNParameters(
    name="tiny",
    block_size=4,
    sbox_table=(0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
                0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2),
    sbox_groups=((0, 1, 2, 3),),
    permutation=(0, 1, 2, 3),
)


def _require_gurobi() -> None:
    try:
        model = GurobiModel("spn_license_check")
        variable = model.add_binary_vector("x", 1)
        model.fix_vector(variable, 0)
        model.solve()
    except GurobiUnavailableError as error:
        pytest.skip(str(error))


@pytest.mark.parametrize("input_vector", [0b0001, 0b0011, 0b1111])
def test_reusable_spn_model_matches_exact_one_sbox(input_vector: int) -> None:
    _require_gurobi()
    expected = propagate_sbox_part(
        BDPTState(width=4, k=frozenset({input_vector})),
        TINY_SPN,
        0,
    )
    suffix = SPNSuffixModel(TINY_SPN, 1, SPNBoundary(0, 0))
    for target_index in range(4):
        status = suffix.check_trail(input_vector, target_index)
        assert status is not SolveStatus.UNDETERMINED
        assert (status is SolveStatus.FEASIBLE) == (
            expected.parity(1 << target_index) is Parity.UNKNOWN
        )


def test_terminal_spn_boundary_is_identity() -> None:
    _require_gurobi()
    suffix = SPNSuffixModel(TINY_SPN, 1, SPNBoundary(1, 0))

    for target_index in range(4):
        status = suffix.check_trail(1 << target_index, target_index)
        assert status is SolveStatus.FEASIBLE
