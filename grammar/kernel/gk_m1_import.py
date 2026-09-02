"""Stable import shim for the on-disk GK-M1 package directory."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_PATH = Path(__file__).parent / "gk-m1" / "measurement" / "geometry.py"
_SPEC = spec_from_file_location("voxis_gk_m1_geometry", _PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load GK-M1 geometry module from {_PATH}")
_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

measure_point = _MODULE.measure_point

__all__ = ["measure_point"]
