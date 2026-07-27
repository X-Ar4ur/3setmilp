"""论文中 ``a/c/?/b`` 状态模式的解析与格式化。"""

from collections.abc import Mapping

from .bdpt import Parity


def compact_pattern(pattern: str) -> str:
    """移除论文模式中的括号、逗号和空白。"""
    return "".join(
        char for char in pattern if char not in "()[], \t\r\n"
    )


def active_indices_from_pattern(pattern: str, width: int) -> frozenset[int]:
    """解析按高位到低位打印的 ``a/c`` 输入模式。"""
    compact = compact_pattern(pattern).lower()
    if len(compact) != width or any(char not in "ac" for char in compact):
        raise ValueError("输入模式长度或字符不合法")
    return frozenset(
        width - 1 - printed_index
        for printed_index, char in enumerate(compact)
        if char == "a"
    )


def active_indices_from_index_pattern(
    pattern: str, width: int
) -> frozenset[int]:
    """解析论文按 ``x0,x1,...`` 打印的 ``a/c`` 输入模式。"""
    compact = compact_pattern(pattern).lower()
    if len(compact) != width or any(char not in "ac" for char in compact):
        raise ValueError("输入模式长度或字符不合法")
    return frozenset(
        index for index, char in enumerate(compact) if char == "a"
    )


def active_indices_from_layout_pattern(
    pattern: str, printed_indices: tuple[int, ...]
) -> frozenset[int]:
    """按显式的“打印位置到内部索引”排列解析 ``a/c`` 模式。"""
    width = len(printed_indices)
    if sorted(printed_indices) != list(range(width)):
        raise ValueError("打印 layout 必须恰好包含全部内部索引")
    compact = compact_pattern(pattern).lower()
    if len(compact) != width or any(char not in "ac" for char in compact):
        raise ValueError("输入模式长度或字符不合法")
    return frozenset(
        internal_index
        for char, internal_index in zip(
            compact, printed_indices, strict=True
        )
        if char == "a"
    )


def format_parity_pattern(
    results: Mapping[int, Parity],
    width: int,
    *,
    group_size: int | None = None,
) -> str:
    """按高位到低位格式化已完成目标位，缺失位显示为 ``-``。"""
    symbols = {Parity.ZERO: "b", Parity.ONE: "1", Parity.UNKNOWN: "?"}
    compact = "".join(
        "-" if index not in results else symbols[results[index]]
        for index in reversed(range(width))
    )
    if group_size is None:
        return compact
    if group_size <= 0 or width % group_size:
        raise ValueError("分组长度必须为状态宽度的正因数")
    return ",".join(
        compact[offset : offset + group_size]
        for offset in range(0, width, group_size)
    )


def format_parity_index_pattern(
    results: Mapping[int, Parity],
    width: int,
    *,
    group_size: int | None = None,
) -> str:
    """按 ``x0,x1,...`` 顺序格式化三值输出模式。"""
    symbols = {Parity.ZERO: "b", Parity.ONE: "1", Parity.UNKNOWN: "?"}
    compact = "".join(
        "-" if index not in results else symbols[results[index]]
        for index in range(width)
    )
    if group_size is None:
        return compact
    if group_size <= 0 or width % group_size:
        raise ValueError("分组长度必须为状态宽度的正因数")
    return ",".join(
        compact[offset : offset + group_size]
        for offset in range(0, width, group_size)
    )


def format_parity_layout_pattern(
    results: Mapping[int, Parity],
    printed_indices: tuple[int, ...],
    *,
    group_size: int | None = None,
) -> str:
    """按显式密码 layout 格式化三值输出模式。"""
    width = len(printed_indices)
    if sorted(printed_indices) != list(range(width)):
        raise ValueError("打印 layout 必须恰好包含全部内部索引")
    symbols = {Parity.ZERO: "b", Parity.ONE: "1", Parity.UNKNOWN: "?"}
    compact = "".join(
        "-" if index not in results else symbols[results[index]]
        for index in printed_indices
    )
    if group_size is None:
        return compact
    if group_size <= 0 or width % group_size:
        raise ValueError("分组长度必须为状态宽度的正因数")
    return ",".join(
        compact[offset : offset + group_size]
        for offset in range(0, width, group_size)
    )
