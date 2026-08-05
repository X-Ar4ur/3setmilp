import json
from pathlib import Path

from three_set_milp.core.bdpt import Parity
from three_set_milp.core.bitvector import unit_vector
from experiments.followup_common import build_initial_state


def test_auxiliary_bits_are_appended_as_known_zero() -> None:
    state, semantics = build_initial_state(
        "ac",
        (1, 0),
        4,
        None,
    )
    assert semantics == {"mode": "unknown"}
    assert state.width == 4
    assert state.parity(unit_vector(2, 4)) is Parity.ZERO
    assert state.parity(unit_vector(3, 4)) is Parity.ZERO


def test_table1_records_platform_and_non_direct_round_extension() -> None:
    config = json.loads(
        Path("configs/secret_keys/table1.json").read_text(encoding="utf-8")
    )
    assert config["paper_platform"]["gurobi"] == "8.1.0"
    assert config["round_extension"] == {
        "reference": "[WLV+14]",
        "families": ["SPECK", "SIMON(102)"],
        "added_rounds_before_distinguisher": 1,
        "directly_searchable_by_k_bdpt": False,
    }
    assert len(config["rows"]) == 16
    assert all("rounds_reported" in row for row in config["rows"])
