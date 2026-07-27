"""BDPT 状态、三值语义和规范化。"""

from dataclasses import dataclass
from enum import Enum

from .bitvector import validate_vector, validate_width
from .order import dominates, reduce_k, reduce_l


class Parity(str, Enum):
    """BDPT 能表达的三种求和结果。"""

    ZERO = "zero"
    ONE = "one"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class BDPTState:
    """表示论文中的三子集可分性状态 ``D^1^n_{K,L}``。"""

    width: int
    k: frozenset[int] = frozenset()
    l: frozenset[int] = frozenset()

    def __post_init__(self) -> None:
        validate_width(self.width)
        object.__setattr__(self, "k", frozenset(self.k))
        object.__setattr__(self, "l", frozenset(self.l))
        for vector in self.k | self.l:
            validate_vector(vector, self.width)

    def parity(self, exponent: int) -> Parity:
        """根据 BDPT 定义返回指定单项式指数的求和结果。"""
        validate_vector(exponent, self.width)
        if any(dominates(exponent, k) for k in self.k):
            return Parity.UNKNOWN
        if exponent in self.l:
            return Parity.ONE
        return Parity.ZERO

    def normalized(self) -> "BDPTState":
        """执行 Reduce0 和 Reduce1，返回语义等价的规范状态。"""
        reduced_k = reduce_k(self.k, self.width)
        reduced_l = reduce_l(reduced_k, self.l, self.width)
        return BDPTState(width=self.width, k=reduced_k, l=reduced_l)

    def parity_table(self) -> tuple[Parity, ...]:
        """枚举所有指数向量的三值语义，仅用于小维度验证。"""
        return tuple(self.parity(exponent) for exponent in range(1 << self.width))

