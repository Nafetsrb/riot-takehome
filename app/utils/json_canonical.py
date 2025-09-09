from typing import Any
import orjson

def canonicalize(data: Any) -> bytes:
    """Return deterministic JSON bytes (sorted keys, no whitespace)."""
    return orjson.dumps(data, option=orjson.OPT_SORT_KEYS)
