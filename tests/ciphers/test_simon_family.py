import json
from pathlib import Path

from three_set_milp.ciphers.simon import (
    SIMON102_32,
    SIMON102_48,
    SIMON102_64,
    SIMECK32,
    SIMECK48,
    SIMECK64,
)
from three_set_milp.core.patterns import active_indices_from_layout_pattern
from three_set_milp.search.simon import simon_k_bdpt_parts


def test_simeck_and_simon102_family_parameters() -> None:
    assert [item.word_size for item in (SIMECK32, SIMECK48, SIMECK64)] == [
        16, 24, 32
    ]
    assert all(item.and_rotations == (0, 5) for item in (SIMECK32, SIMECK48, SIMECK64))
    assert all(item.xor_rotation == 1 for item in (SIMECK32, SIMECK48, SIMECK64))
    assert all(
        item.and_rotations == (1, 0)
        for item in (SIMON102_32, SIMON102_48, SIMON102_64)
    )


def test_simon_k_bdpt_splits_key_and_swap() -> None:
    parts = simon_k_bdpt_parts(SIMON102_32, 1)
    width = SIMON102_32.word_size
    assert len(parts) == 2 * width + 1
    key_parts = [part for part in parts if part.secret_key_label]
    assert [part.secret_key_label for part in key_parts] == [
        f"k^0_{index}" for index in range(width)
    ]
    assert [part.secret_key_index for part in key_parts] == [
        width + index for index in range(width)
    ]


def test_table5_simon102_configs_have_one_unknown_constant() -> None:
    parameters_by_name = {
        "simon10232": SIMON102_32,
        "simon10248": SIMON102_48,
        "simon10264": SIMON102_64,
    }
    for path in Path("configs/secret_keys/table5").glob("*.json"):
        config = json.loads(path.read_text(encoding="utf-8"))
        parameters = parameters_by_name[config["cipher"]]
        active = active_indices_from_layout_pattern(
            config["input_pattern"],
            parameters.paper_print_indices,
        )
        assert len(active) == parameters.block_size - 1
        assert len(config["previous_output"].replace(",", "")) == parameters.block_size
        assert len(config["expected_output"].replace(",", "")) == parameters.block_size
