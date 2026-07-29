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
    FINAL_ZERO = "final_zero"
    FINAL_UNKNOWN = "final_unknown"


@dataclass(frozen=True, slots=True)
class SearchPart:
    """一个局部函数及其输入边界。"""

    boundary: Hashable
    propagate: Callable[[BDPTState], BDPTState]
    secret_key_index: int | None = None


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
    key_bypassed: bool | None = None
    decisive_vector: int | None = None


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

    return _search_bdpt(
        initial_state,
        target_index,
        parts,
        suffix_oracle,
        enable_key_bypass=False,
        check_final_state=False,
    )


def search_k_bdpt(
    initial_state: BDPTState,
    target_index: int,
    parts: Sequence[SearchPart],
    suffix_oracle: SuffixOracle,
) -> SearchResult:
    """执行后续论文 Algorithm 1，在满足定理 3 时旁路轮密钥。"""
    unit_vector(target_index, initial_state.width)
    if not parts:
        raise ValueError("K-BDPT 搜索至少需要一个局部函数")

    return _search_bdpt(
        initial_state,
        target_index,
        parts,
        suffix_oracle,
        enable_key_bypass=True,
        check_final_state=True,
    )


def _final_result(state: BDPTState, target_index: int) -> SearchResult:
    """执行主论文 Algorithm 2 第 22 行的终点规则。"""
    unit_vector(target_index, state.width)
    return SearchResult(
        parity=Parity.ONE,
        reason=StopReason.FINAL_ONE,
        trace=(),
    )


def _final_state_parity(state: BDPTState, target_index: int) -> Parity:
    """仅供 K-BDPT 旁路子问题读取已经位于输出端的状态。"""
    return state.parity(unit_vector(target_index, state.width))


def _final_state_result(
    state: BDPTState,
    target_index: int,
) -> SearchResult:
    """读取最终 BDPT；用于后续论文算法的内部旁路子问题。"""
    parity = _final_state_parity(state, target_index)
    reasons = {
        Parity.ZERO: StopReason.FINAL_ZERO,
        Parity.ONE: StopReason.FINAL_ONE,
        Parity.UNKNOWN: StopReason.FINAL_UNKNOWN,
    }
    return SearchResult(parity=parity, reason=reasons[parity], trace=())


def _search_bdpt(
    initial_state: BDPTState,
    target_index: int,
    parts: Sequence[SearchPart],
    suffix_oracle: SuffixOracle,
    *,
    enable_key_bypass: bool,
    check_final_state: bool,
) -> SearchResult:
    """共享主搜索循环；K-BDPT 的内层判定始终调用原始 BDPT。"""

    current = initial_state.normalized()
    trace: list[TraceEntry] = []
    for part_index, part in enumerate(parts):
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
                        decisive_vector=vector,
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
        key_bypassed: bool | None = None
        if enable_key_bypass and part.secret_key_index is not None:
            bit_mask = unit_vector(part.secret_key_index, current.width)
            shifted_l = frozenset(
                vector | bit_mask
                for vector in pruned.l
                if vector & bit_mask == 0
            )
            bypass_input = BDPTState(width=current.width, l=shifted_l)
            remaining_parts = parts[part_index + 1 :]
            if remaining_parts:
                bypass_result = _search_bdpt(
                    bypass_input,
                    target_index,
                    remaining_parts,
                    suffix_oracle,
                    enable_key_bypass=False,
                    check_final_state=True,
                )
                bypass_parity = bypass_result.parity
            else:
                bypass_parity = _final_state_parity(
                    bypass_input,
                    target_index,
                )
            key_bypassed = bypass_parity is Parity.ZERO
            propagated = pruned if key_bypassed else part.propagate(pruned)
        else:
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
                key_bypassed=key_bypassed,
            )
        )
        current = propagated

    final = (
        _final_state_result(current, target_index)
        if check_final_state
        else _final_result(current, target_index)
    )
    return SearchResult(
        parity=final.parity,
        reason=final.reason,
        trace=tuple(trace),
    )
