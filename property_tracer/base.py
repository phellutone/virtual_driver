from typing import Any, Callable
import bpy

_PROPTRACE_BASE_TYPE: bpy.types.bpy_struct = None
_PROPTRACE_BASE_PATHS: dict[str, bpy.props._PropertyDeferred] = dict()
_PROPTRACE_BASE_ACCESSES: dict[str, Callable[[Any], Any]] = dict()
