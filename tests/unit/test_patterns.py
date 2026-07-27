import pytest

from three_set_milp.core.bdpt import Parity
from three_set_milp.core.patterns import (
    active_indices_from_pattern,
    compact_pattern,
    format_parity_pattern,
)


def test_activity_pattern_uses_high_to_low_print_order() -> None:
    assert active_indices_from_pattern("(ac,ca)", 4) == frozenset({3, 0})


def test_parity_pattern_format_and_grouping() -> None:
    results = {3: Parity.ZERO, 2: Parity.UNKNOWN, 1: Parity.ONE}
    assert format_parity_pattern(results, 4, group_size=2) == "b?,1-"
    assert compact_pattern("(b?, 1-)") == "b?1-"


@pytest.mark.parametrize("pattern", ["aaa", "aacx", ""])
def test_activity_pattern_rejects_invalid_input(pattern: str) -> None:
    with pytest.raises(ValueError):
        active_indices_from_pattern(pattern, 4)
