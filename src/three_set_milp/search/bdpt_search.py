"""与具体密码无关的主论文 Algorithm 2。"""

from collections.abc import Callable, Hashable, Sequence
from dataclasses import dataclass
from enum import Enum

from three_set_milp.core.bdpt import BDPTState, Parity
from three_set_milp.core.bitvector import unit_vector


class StopReason(str, Enum):
    """Algorithm 2 的停止原因。"""

    K_REACHABLE = "k_reachable"
    L_EMPTY = "l_empty"
    FINAL_ONE = "final_one"


@dataclass(frozen=True, slots=True)
class SearchPart:
    """一个局部函数及其输入边界。"""

    boundary: Hashable
    propagate: Callable[[BDPTState], BDPTState]


@dataclass(frozen=True, slots=True)
class TraceEntry:
    """一个局部边界上的剪枝统计。"""

    boundary: Hashable
    k_before: int
    l_before: int
    k_queries: int
    l_queries: int
    l_survivors: int
    k_after_propagation: int | None
    l_after_propagation: int | None


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Algorithm 2 的三值结果及可审计轨迹。"""

    parity: Parity
    reason: StopReason
    trace: tuple[TraceEntry, ...]


SuffixOracle = Callable[[Hashable, int, int], bool]


class CachedSuffixOracle:
    """缓存 ``(边界,输入向量,目标位)`` 的 CBDP 可达性。"""

    def __init__(self, oracle: SuffixOracle) -> None:
        self._oracle = oracle
        self._cache: dict[tuple[Hashable, int, int], bool] = {}
        self.calls = 0
        self.cache_hits = 0

    def __call__(self, boundary: Hashable, vector: int, target: int) -> bool:
        key = (boundary, vector, target)
        self.calls += 1
        if key in self._cache:
            self.cache_hits += 1
            return self._cache[key]
        result = self._oracle(boundary, vector, target)
        self._cache[key] = result
        return result


def search_bdpt(
    initial_state: BDPTState,
    target_index: int,
    parts: Sequence[SearchPart],
    suffix_oracle: SuffixOracle,
) -> SearchResult:
    """执行主论文 Algorithm 2，返回 zero、one 或 unknown。"""
    unit_vector(target_index, initial_state.width)
    if not parts:
        raise ValueError("BDPT 搜索至少需要一个局部函数")

    current = initial_state.normalized()
    trace: list[TraceEntry] = []
    for part in parts:
        k_queries = 0
        for vector in sorted(current.k):
            k_queries += 1
            if suffix_oracle(part.boundary, vector, target_index):
                trace.append(
                    TraceEntry(
                        boundary=part.boundary,
                        k_before=len(current.k),
                        l_before=len(current.l),
                        k_queries=k_queries,
                        l_queries=0,
                        l_survivors=0,
                        k_after_propagation=None,
                        l_after_propagation=None,
                    )
                )
                return SearchResult(
                    parity=Parity.UNKNOWN,
                    reason=StopReason.K_REACHABLE,
                    trace=tuple(trace),
                )

        survivors: set[int] = set()
        l_queries = 0
        for vector in sorted(current.l):
            l_queries += 1
            if suffix_oracle(part.boundary, vector, target_index):
                survivors.add(vector)

        if not survivors:
            trace.append(
                TraceEntry(
                    boundary=part.boundary,
                    k_before=len(current.k),
                    l_before=len(current.l),
                    k_queries=k_queries,
                    l_queries=l_queries,
                    l_survivors=0,
                    k_after_propagation=None,
                    l_after_propagation=None,
                )
            )
            return SearchResult(
                parity=Parity.ZERO,
                reason=StopReason.L_EMPTY,
                trace=tuple(trace),
            )

        pruned = BDPTState(
            width=current.width,
            l=frozenset(survivors),
        )
        propagated = part.propagate(pruned)
        if propagated.width != current.width:
            raise ValueError("局部函数传播改变了密码状态宽度")
        trace.append(
            TraceEntry(
                boundary=part.boundary,
                k_before=len(current.k),
                l_before=len(current.l),
                k_queries=k_queries,
                l_queries=l_queries,
                l_survivors=len(survivors),
                k_after_propagation=len(propagated.k),
                l_after_propagation=len(propagated.l),
            )
        )
        current = propagated

    return SearchResult(
        parity=Parity.ONE,
        reason=StopReason.FINAL_ONE,
        trace=tuple(trace),
    )

