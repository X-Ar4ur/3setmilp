import json
from pathlib import Path

from three_set_milp.ciphers.speck import (
    FULL_ADDER_TABLE,
    SPECK32,
    SPECK48,
    SPECK64,
    SPECK96,
    SpeckParameters,
    decode_state,
    encode_state,
    propagate_round,
    round_function,
)
from three_set_milp.core.bdpt import Parity
from three_set_milp.core.bitvector import unit_vector
from three_set_milp.core.oracle import (
    append_known_zero_bits,
    cube_multiset,
    exact_state_from_multiset,
    monomial_parity,
    theoretical_unknown_constant_cube_state,
)
from three_set_milp.core.patterns import active_indices_from_layout_pattern
from three_set_milp.search.speck import speck_search_parts


def test_full_adder_truth_table_preserves_second_input() -> None:
    for value, output in enumerate(FULL_ADDER_TABLE):
        first = value & 1
        second = (value >> 1) & 1
        carry = (value >> 2) & 1
        total = first + second + carry
        assert (output & 1) == (total & 1)
        assert ((output >> 1) & 1) == second
        assert ((output >> 2) & 1) == (total >> 1)


def test_small_speck_circuit_matches_exact_multiset() -> None:
    parameters = SpeckParameters(word_size=3, alpha=1, beta=1)
    inputs = ((0, 0), (1, 2), (3, 5), (7, 7))
    input_points = tuple(
        encode_state(first, second, parameters) for first, second in inputs
    )
    output_points = tuple(
        encode_state(
            *round_function(first, second, 0, parameters),
            parameters,
        )
        for first, second in inputs
    )
    propagated = propagate_round(
        exact_state_from_multiset(input_points, parameters.state_width),
        parameters,
        include_secret_key=False,
    )
    expected = exact_state_from_multiset(
        output_points,
        parameters.state_width,
    )
    assert propagated.parity_table() == expected.parity_table()
    assert propagated.parity(
        unit_vector(parameters.carry_index, parameters.state_width)
    ) is Parity.ZERO


def test_speck_auxiliary_carry_preserves_unknown_constant_cube() -> None:
    parameters = SpeckParameters(word_size=3, alpha=1, beta=1)
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
                _run_public_speck_rounds(value, parameters, rounds=3)
                for value in inputs
            )
        )

    initial = append_known_zero_bits(
        theoretical_unknown_constant_cube_state(
            parameters.block_size,
            active,
        ),
        1,
    )
    propagated = initial
    for _ in range(3):
        propagated = propagate_round(
            propagated,
            parameters,
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


def _run_public_speck_rounds(
    value: int,
    parameters: SpeckParameters,
    *,
    rounds: int,
) -> int:
    first, second = decode_state(value, parameters)
    for _ in range(rounds):
        first, second = round_function(first, second, 0, parameters)
    return encode_state(first, second, parameters)


def test_speck_key_parts_record_paper_key_labels() -> None:
    parts = speck_search_parts(SPECK32, 1)
    key_parts = [part for part in parts if part.secret_key_label is not None]
    assert len(parts) == SPECK32.parts_per_round
    assert [part.secret_key_label for part in key_parts] == [
        f"k^0_{index}" for index in range(16)
    ]
    assert key_parts[7].secret_key_index == SPECK32.word_size + 7
    assert len({part.boundary for part in key_parts}) == 1
    assert parts[2 * SPECK32.word_size + 1].boundary == key_parts[0].boundary


def test_table2_config_patterns_match_cipher_layouts() -> None:
    parameters_by_name = {
        "speck32": SPECK32,
        "speck48": SPECK48,
        "speck64": SPECK64,
        "speck96": SPECK96,
    }
    root = Path("configs/secret_keys/table2")
    for path in root.glob("*.json"):
        config = json.loads(path.read_text(encoding="utf-8"))
        parameters = parameters_by_name[config["cipher"]]
        for case in config["cases"]:
            active = active_indices_from_layout_pattern(
                case["input_pattern"],
                parameters.paper_print_indices,
            )
            assert len(active) in {
                parameters.block_size - 2,
                parameters.block_size - 3,
            }
            assert len(
                case["expected_output"].replace(",", "")
            ) == parameters.block_size
