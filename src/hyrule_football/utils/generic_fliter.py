from typing import Callable, TypeVar, Iterable, List, Mapping, Dict

T = TypeVar("T")


def list_filter(
    items: Iterable[T],
    *conditions: Callable[[T], bool],
) -> List[T]:
    """对序列中的元素应用多个条件，所有条件为 True 的元素会被保留。"""
    return [x for x in items if all(cond(x) for cond in conditions)]


K = TypeVar("K")
V = TypeVar("V")


def dict_filter(
    d: Mapping[K, V],
    *conditions: Callable[[K, V], bool],
) -> Dict[K, V]:
    """对字典的 (key, value) 项应用多个条件，所有条件为 True 的项会被保留。"""
    return {k: v for k, v in d.items() if all(cond(k, v) for cond in conditions)}
