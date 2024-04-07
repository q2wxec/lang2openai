from langchain_core.utils._merge import merge_dicts
from langchain_core.utils import _merge
from typing import Any, Dict



def do_merge_dicts(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dicts, handling specific scenarios where a key exists in both
    dictionaries but has a value of None in 'left'. In such cases, the method uses the
    value from 'right' for that key in the merged dictionary.

    Example:
        If left = {"function_call": {"arguments": None}} and
        right = {"function_call": {"arguments": "{\n"}}
        then, after merging, for the key "function_call",
        the value from 'right' is used,
        resulting in merged = {"function_call": {"arguments": "{\n"}}.
    """
    merged = left.copy()
    for k, v in right.items():
        if k not in merged:
            merged[k] = v
        elif v is not None and merged[k] is None:
            merged[k] = v
        elif v is None or merged[k] == v:
            continue
        elif type(merged[k]) != type(v):
            raise TypeError(
                f'additional_kwargs["{k}"] already exists in this message,'
                " but with a different type."
            )
        elif isinstance(merged[k], str):
            merged[k] += v
        elif isinstance(merged[k], int):
            merged[k] += v
        elif isinstance(merged[k], dict):
            merged[k] = do_merge_dicts(merged[k], v)
        elif isinstance(merged[k], list):
            merged[k] = merged[k] + v
        else:
            raise TypeError(
                f"Additional kwargs key {k} already exists in left dict and value has "
                f"unsupported type {type(merged[k])}."
            )
    return merged


def mk():
    _merge.merge_dicts = do_merge_dicts
    merge_dicts = do_merge_dicts