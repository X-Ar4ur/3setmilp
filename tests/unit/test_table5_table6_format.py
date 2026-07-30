import pytest

from experiments.reproduce_table5_spn import (
    PAPER_LAYOUTS,
    PARAMETERS,
    has_recorded_witness,
    load_config as load_table5_config,
    update_summary as update_table5_summary,
)
from experiments.reproduce_table6_lblock import (
    load_config as load_table6_config,
    update_summary as update_table6_summary,
)
from three_set_milp.core.patterns import (
    active_indices_from_layout_pattern,
    compact_pattern,
)


def _generic_results(
    expected: str, layout: tuple[int, ...]
) -> dict[str, dict[str, str]]:
    compact = compact_pattern(expected)
    return {
        str(internal_index): {
            "parity": "zero" if symbol == "b" else "unknown"
        }
        for internal_index, symbol in zip(layout, compact, strict=True)
    }


def _lblock_results(expected: str) -> dict[str, dict[str, str]]:
    compact = compact_pattern(expected)
    results: dict[str, dict[str, str]] = {}
    for printed_index, symbol in enumerate(compact):
        internal_index = (
            31 - printed_index
            if printed_index < 32
            else 63 - (printed_index - 32)
        )
        results[str(internal_index)] = {
            "parity": "zero" if symbol == "b" else "unknown"
        }
    return results


@pytest.mark.parametrize("experiment", ["present60", "present63", "rectangle60"])
def test_table5_expected_pattern_round_trip(experiment: str) -> None:
    config = load_table5_config(experiment)
    payload = {
        "config": config,
        "results": _generic_results(
            config["expected_output"], PAPER_LAYOUTS[config["cipher"]]
        ),
    }
    update_table5_summary(payload, PARAMETERS[config["cipher"]])
    assert payload["comparison"] == {"complete": True, "matches": True}


def test_present60_uses_the_specification_x63_to_x0_order() -> None:
    config = load_table5_config("present60")
    layout = PAPER_LAYOUTS["present"]
    active = active_indices_from_layout_pattern(config["input_pattern"], layout)
    balanced = {
        internal_index
        for internal_index, symbol in zip(
            layout,
            compact_pattern(config["expected_output"]),
            strict=True,
        )
        if symbol == "b"
    }

    assert config["state_order"] == "x63_to_x0"
    assert active == frozenset(range(4, 64))
    assert balanced == {0, 4, 8, 12}


def test_k_bdpt_resume_requires_bypass_provenance_when_recording_witness() -> None:
    assert not has_recorded_witness({}, "k-bdpt")
    assert not has_recorded_witness(
        {"decisive_cbdp_witness": None},
        "k-bdpt",
    )
    assert has_recorded_witness(
        {
            "decisive_cbdp_witness": None,
            "bypass_obstruction_witnesses": [],
        },
        "k-bdpt",
    )
    assert has_recorded_witness({"decisive_cbdp_witness": None}, "bdpt")


@pytest.mark.parametrize("experiment", ["lblock63", "lblock62"])
def test_table6_expected_pattern_round_trip(experiment: str) -> None:
    config = load_table6_config(experiment)
    payload = {"config": config, "results": _lblock_results(config["expected_output"])}
    update_table6_summary(payload)
    assert payload["comparison"] == {"complete": True, "matches": True}
