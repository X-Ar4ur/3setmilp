"""比特可分性使用的逐位偏序。"""

from collections.abc import Iterable

from .bitvector import validate_vector, validate_width


def dominates(upper: int, lower: int) -> bool:
    """判断 ``upper`` 是否逐位大于等于 ``lower``。"""
    if upper < 0 or lower < 0:
        raise ValueError("偏序只适用于非负整数向量")
    return (upper & lower) == lower


def strictly_dominates(upper: int, lower: int) -> bool:
    """判断 ``upper`` 是否支配且不等于 ``lower``。"""
    return upper != lower and dominates(upper, lower)


def reduce_k(vectors: Iterable[int], width: int) -> frozenset[int]:
    """删除 K 中被更小向量覆盖的冗余向量。"""
    validate_width(width)
    items = frozenset(vectors)
    for vector in items:
        validate_vector(vector, width)
    return frozenset(
        candidate
        for candidate in items
        if not any(
            candidate != other and dominates(candidate, other)
            for other in items
        )
    )


def reduce_l(
    k_vectors: Iterable[int], l_vectors: Iterable[int], width: int
) -> frozenset[int]:
    """删除 L 中已经落入 K 的 unknown 上闭包的向量。"""
    validate_width(width)
    k_items = frozenset(k_vectors)
    l_items = frozenset(l_vectors)
    for vector in k_items | l_items:
        validate_vector(vector, width)
    return frozenset(
        ell
        for ell in l_items
        if not any(dominates(ell, k) for k in k_items)
    )

