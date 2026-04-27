from __future__ import annotations

from typing import Any


def run_macro(*args: Any, **kwargs: Any) -> Any:
    from .macro_engine import run_macro as _run_macro

    return _run_macro(*args, **kwargs)


__all__ = ["run_macro"]
