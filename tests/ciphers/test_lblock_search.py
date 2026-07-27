from three_set_milp.milp.lblock import LBlockBoundary
from three_set_milp.search.lblock import lblock_search_parts


def test_lblock_search_parts_follow_paper_boundary_order() -> None:
    parts = lblock_search_parts(2)
    assert len(parts) == 18
    assert parts[0].boundary == LBlockBoundary(0, 0)
    assert parts[8].boundary == LBlockBoundary(0, 8)
    assert parts[9].boundary == LBlockBoundary(1, 0)
    assert parts[-1].boundary == LBlockBoundary(1, 8)
