from experiments.reproduce_table4_simon import paper_pattern
from three_set_milp.ciphers.simon import SIMON32, SIMON64


def _results_for_pattern(left: str, right: str) -> dict[str, dict[str, str]]:
    symbols = {"b": "zero", "1": "one", "?": "unknown"}
    width = len(left)
    results: dict[str, dict[str, str]] = {}
    for printed_index, symbol in enumerate(left):
        internal = width - 1 - printed_index
        results[str(internal)] = {"parity": symbols[symbol]}
    for printed_index, symbol in enumerate(right):
        internal = width + width - 1 - printed_index
        results[str(internal)] = {"parity": symbols[symbol]}
    return results


def test_simon32_paper_pattern_mapping() -> None:
    left = "????????????????"
    right = "?b??????b??????b"
    results = _results_for_pattern(left, right)
    assert paper_pattern(results, SIMON32) == (left, right)
    assert {index for index, value in results.items() if value["parity"] == "zero"} == {
        "16",
        "23",
        "30",
    }


def test_simon64_paper_pattern_mapping() -> None:
    left = "????????????????????????????????"
    right = "bbbbbbbbbbb??b??b?????bbbbbbbbbb"
    results = _results_for_pattern(left, right)
    assert paper_pattern(results, SIMON64) == (left, right)
    assert sum(value["parity"] == "zero" for value in results.values()) == 23

