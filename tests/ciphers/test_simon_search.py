from three_set_milp.ciphers.simon import SIMON32
from three_set_milp.milp.simon import SimonBoundary
from three_set_milp.search.simon import simon_search_parts


def test_simon_search_part_boundaries() -> None:
    parts = simon_search_parts(SIMON32, rounds=2)
    assert len(parts) == 2 * 17
    assert parts[0].boundary == SimonBoundary(0, 0)
    assert parts[15].boundary == SimonBoundary(0, 15)
    assert parts[16].boundary == SimonBoundary(0, 16)
    assert parts[17].boundary == SimonBoundary(1, 0)
    assert parts[-1].boundary == SimonBoundary(1, 16)

