import json
from pathlib import Path

from three_set_milp.ciphers.katan import (
    IR_SEQUENCE,
    KATAN32,
    KATAN48,
    KATAN64,
    KatanParameters,
    clock_function,
    decode_state,
    encode_state,
    ir_for_clock,
    propagate_clock,
    shift_permutation,
)
from three_set_milp.core.bdpt import Parity
from three_set_milp.core.bitvector import unit_vector
from three_set_milp.core.oracle import (
    cube_multiset,
    exact_state_from_multiset,
    monomial_parity,
    theoretical_unknown_constant_cube_state,
)
from three_set_milp.core.patterns import active_indices_from_layout_pattern
from three_set_milp.search.katan import katan_search_parts


def test_ir_sequence_matches_original_paper_prefix_and_length() -> None:
    assert len(IR_SEQUENCE) == 254
    assert IR_SEQUENCE[:20] == tuple(int(bit) for bit in "11111110001101010101")


def test_small_katan_circuit_matches_exact_multiset() -> None:
    parameters = KatanParameters(
        block_size=11,
        l1_size=5,
        l2_size=6,
        x_taps=(4, 1, 2, 0, 3),
        y_taps=(5, 1, 4, 0, 3, 2),
        clocks_per_round=1,
    )
    inputs = ((0, 0), (1, 2), (3, 5), (31, 63))
    input_points = tuple(
        encode_state(l1, l2, parameters) for l1, l2 in inputs
    )
    output_points = tuple(
        encode_state(
            *clock_function(l1, l2, 0, 0, 1, parameters),
            parameters,
        )
        for l1, l2 in inputs
    )
    propagated = propagate_clock(
        exact_state_from_multiset(input_points, parameters.state_width),
        parameters,
        0,
        include_secret_key=False,
    )
    expected = exact_state_from_multiset(
        output_points,
        parameters.state_width,
    )
    assert propagated.parity_table() == expected.parity_table()
    assert parameters.state_width == parameters.block_size


def test_katan_in_place_feedback_matches_unknown_constant_cube() -> None:
    parameters = KatanParameters(
        block_size=11,
        l1_size=5,
        l2_size=6,
        x_taps=(4, 1, 2, 0, 3),
        y_taps=(5, 1, 4, 0, 3, 2),
        clocks_per_round=1,
    )
    active = tuple(range(parameters.block_size - 1))
    output_families: list[tuple[int, ...]] = []
    for constant in (0, 1):
        inputs = cube_multiset(
            parameters.block_size,
            active,
            {parameters.block_size - 1: constant},
        )
        output_families.append(
            tuple(
                encode_state(
                    *clock_function(
                        *decode_state(value, parameters),
                        0,
                        0,
                        1,
                        parameters,
                    ),
                    parameters,
                )
                for value in inputs
            )
        )

    propagated = propagate_clock(
        theoretical_unknown_constant_cube_state(
            parameters.block_size,
            active,
        ),
        parameters,
        0,
        include_secret_key=False,
    )
    for exponent in range(1 << parameters.block_size):
        observed = {
            monomial_parity(multiset, exponent, parameters.state_width)
            for multiset in output_families
        }
        expected = (
            Parity.ONE
            if observed == {1}
            else Parity.ZERO
            if observed == {0}
            else Parity.UNKNOWN
        )
        assert propagated.parity(exponent) is expected


def test_katan_shift_is_permutation_and_reuses_round_ir() -> None:
    assert sorted(shift_permutation(KATAN64)) == list(range(KATAN64.state_width))
    assert ir_for_clock(KATAN64, 0) == IR_SEQUENCE[0]
    assert ir_for_clock(KATAN64, 1) == IR_SEQUENCE[0]
    assert ir_for_clock(KATAN64, 2) == IR_SEQUENCE[0]
    assert ir_for_clock(KATAN64, 3) == IR_SEQUENCE[1]


def test_katan_key_labels_repeat_within_wide_round() -> None:
    parts = katan_search_parts(KATAN64, 4)
    labels = [part.secret_key_label for part in parts if part.secret_key_label]
    assert labels == [
        "ka^0", "kb^0", "ka^0", "kb^0", "ka^0", "kb^0", "ka^1", "kb^1"
    ]
    for offset in range(0, len(parts), 4):
        assert len({part.boundary for part in parts[offset + 1 : offset + 4]}) == 1


def test_table3_configs_encode_fractional_round_as_clock_count() -> None:
    parameters_by_name = {
        "katan32": KATAN32,
        "katan48": KATAN48,
        "katan64": KATAN64,
    }
    for path in Path("configs/secret_keys/table3").glob("*.json"):
        config = json.loads(path.read_text(encoding="utf-8"))
        parameters = parameters_by_name[config["cipher"]]
        active = active_indices_from_layout_pattern(
            config["input_pattern"],
            parameters.paper_print_indices,
        )
        assert active == frozenset(
            index for index in range(parameters.block_size)
            if index != parameters.l1_size
        )
        if config["cipher"] == "katan64":
            assert config["round_notation"] == "73.6"
            assert config["total_clocks"] == 73 * 3 + 2
