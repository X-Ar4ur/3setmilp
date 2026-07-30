"""独立于传播规则和 MILP 的小规模穷举 oracle。"""

from collections.abc import Iterable, Mapping, Sequence
from itertools import product

from .bdpt import BDPTState, Parity
from .bitvector import unit_vector, validate_vector, validate_width
from .order import reduce_k


def monomial_value(value: int, exponent: int, width: int) -> int:
    """计算二进制点 ``value`` 上的单项式 ``x^exponent``。"""
    validate_vector(value, width)
    validate_vector(exponent, width)
    return int((value & exponent) == exponent)


def monomial_parity(
    multiset: Sequence[int], exponent: int, width: int
) -> int:
    """直接计算多重集上某个单项式取值的异或和。"""
    validate_vector(exponent, width)
    parity = 0
    for value in multiset:
        parity ^= monomial_value(value, exponent, width)
    return parity


def exact_state_from_multiset(
    multiset: Sequence[int], width: int
) -> BDPTState:
    """枚举全部单项式，构造无 unknown 的精确 BDPT 状态。"""
    validate_width(width)
    for value in multiset:
        validate_vector(value, width)
    one_exponents = frozenset(
        exponent
        for exponent in range(1 << width)
        if monomial_parity(multiset, exponent, width) == 1
    )
    return BDPTState(width=width, l=one_exponents)


def cube_multiset(
    width: int,
    active_indices: Iterable[int],
    constants: Mapping[int, int],
) -> tuple[int, ...]:
    """生成活动位遍历全部取值、其余位固定的明文集合。"""
    validate_width(width)
    active = tuple(sorted(set(active_indices)))
    for index in active:
        unit_vector(index, width)
    if set(active) & set(constants):
        raise ValueError("活动位不能同时指定为常量")
    if set(active) | set(constants) != set(range(width)):
        raise ValueError("常量映射必须覆盖所有非活动位")
    for index, bit in constants.items():
        unit_vector(index, width)
        if bit not in (0, 1) or isinstance(bit, bool):
            raise ValueError("常量位只能取整数 0 或 1")

    constant_value = sum(bit << index for index, bit in constants.items())
    values: list[int] = []
    for assignment in product((0, 1), repeat=len(active)):
        value = constant_value
        for index, bit in zip(active, assignment, strict=True):
            value |= bit << index
        values.append(value)
    return tuple(values)


def unknown_constant_cube_state(
    width: int, active_indices: Iterable[int]
) -> BDPTState:
    """穷举所有常量赋值，得到论文初始明文集合的三值状态。"""
    validate_width(width)
    active = tuple(sorted(set(active_indices)))
    for index in active:
        unit_vector(index, width)
    inactive = tuple(index for index in range(width) if index not in active)

    multisets: list[tuple[int, ...]] = []
    for constant_bits in product((0, 1), repeat=len(inactive)):
        constants = dict(zip(inactive, constant_bits, strict=True))
        multisets.append(cube_multiset(width, active, constants))

    return state_from_multiset_family(multisets, width)


def state_from_multiset_family(
    multisets: Sequence[Sequence[int]], width: int
) -> BDPTState:
    """穷举一族多重集，构造其可被 BDPT 精确表达的三值状态。"""
    validate_width(width)
    if not multisets:
        raise ValueError("多重集族不能为空")
    for multiset in multisets:
        for value in multiset:
            validate_vector(value, width)

    parity_sets: list[set[int]] = [set() for _ in range(1 << width)]
    for multiset in multisets:
        for exponent in range(1 << width):
            parity_sets[exponent].add(
                monomial_parity(multiset, exponent, width)
            )

    unknown = {
        exponent for exponent, values in enumerate(parity_sets) if values == {0, 1}
    }
    one = {
        exponent for exponent, values in enumerate(parity_sets) if values == {1}
    }

    # BDPT 用 K 的上闭包表示 unknown；先验证 oracle 的 unknown 集确实上闭。
    for exponent in unknown:
        for upper in range(1 << width):
            if (upper & exponent) == exponent and upper not in unknown:
                raise ValueError("该多重集族的 unknown 区域不能被 BDPT 精确表示")

    minimal_unknown = reduce_k(unknown, width)
    return BDPTState(width=width, k=minimal_unknown, l=frozenset(one)).normalized()


def theoretical_unknown_constant_cube_state(
    width: int, active_indices: Iterable[int]
) -> BDPTState:
    """按全活跃单项式和最小严格超集公式构造初始 BDPT。"""
    validate_width(width)
    active = tuple(sorted(set(active_indices)))
    active_mask = 0
    for index in active:
        active_mask |= unit_vector(index, width)
    inactive = tuple(index for index in range(width) if index not in active)
    minimal_unknown = frozenset(
        active_mask | unit_vector(index, width) for index in inactive
    )
    return BDPTState(
        width=width,
        k=minimal_unknown,
        l=frozenset({active_mask}),
    ).normalized()


def theoretical_known_constant_cube_state(
    width: int,
    active_indices: Iterable[int],
    constants: Mapping[int, int],
) -> BDPTState:
    """按后续论文的已知常量公式构造精确初始 BDPT。"""
    validate_width(width)
    active = frozenset(active_indices)
    for index in active:
        unit_vector(index, width)

    constant_indices = set(constants)
    if active & constant_indices:
        raise ValueError("活动位不能同时指定为常量")
    if active | constant_indices != set(range(width)):
        raise ValueError("常量映射必须覆盖所有非活动位")

    one_mask = 0
    for index, bit in constants.items():
        unit_vector(index, width)
        if bit not in (0, 1) or isinstance(bit, bool):
            raise ValueError("常量位只能取整数 0 或 1")
        if bit == 1:
            one_mask |= unit_vector(index, width)

    active_mask = sum(unit_vector(index, width) for index in active)
    l_vectors: set[int] = set()
    subset = one_mask
    while True:
        l_vectors.add(active_mask | subset)
        if subset == 0:
            break
        subset = (subset - 1) & one_mask

    return BDPTState(width=width, l=frozenset(l_vectors)).normalized()


def state_matches_family(
    state: BDPTState, multisets: Sequence[Sequence[int]]
) -> bool:
    """检查三值状态是否精确描述一族具体多重集的 parity。"""
    for exponent in range(1 << state.width):
        observed = {
            monomial_parity(multiset, exponent, state.width)
            for multiset in multisets
        }
        expected = state.parity(exponent)
        if expected is Parity.ZERO and observed != {0}:
            return False
        if expected is Parity.ONE and observed != {1}:
            return False
        if expected is Parity.UNKNOWN and observed != {0, 1}:
            return False
    return True
