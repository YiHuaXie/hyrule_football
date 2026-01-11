from typing import List, Optional, Any


def deep_get(d: dict, keys: List[str], default=None) -> Optional[Any]:
    """递归获取字典中的值"""
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d
