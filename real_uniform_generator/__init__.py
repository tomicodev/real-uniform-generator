"""Real Uniform Generator v0.5.0 runtime loader.

The v0.5 implementation is stored as a compressed source payload so installations
upgraded from early repository snapshots can load the complete pattern and material
engine without depending on stale modules left by v0.2.
"""

from __future__ import annotations

import base64
import io
import importlib.util
from pathlib import Path
import sys
import types
from zipfile import ZipFile

import bpy
from bpy.props import PointerProperty

_RUNTIME_VERSION = (0, 5, 0)
_MODULE_ORDER = (
    "constants",
    "pattern",
    "properties",
    "material_io",
    "textures",
    "materials",
    "geometry",
    "finishing",
    "exporter",
    "preview",
    "operators",
    "ui",
)


def _load_runtime_modules() -> None:
    payload_path = Path(__file__).with_name("v05_runtime_payload.b64")
    if not payload_path.is_file():
        raise RuntimeError(f"Real Uniform Generator runtime payload is missing: {payload_path}")

    try:
        payload = base64.b64decode(payload_path.read_text(encoding="ascii"), validate=True)
        with ZipFile(io.BytesIO(payload)) as archive:
            sources = {
                name: archive.read(f"{name}.py").decode("utf-8")
                for name in _MODULE_ORDER
            }
    except Exception as exc:
        raise RuntimeError("Real Uniform Generator v0.5 runtime payload is invalid") from exc

    package_name = __name__
    for short_name in _MODULE_ORDER:
        full_name = f"{package_name}.{short_name}"
        sys.modules.pop(full_name, None)
        module = types.ModuleType(full_name)
        module.__file__ = f"{payload_path}!/{short_name}.py"
        module.__package__ = package_name
        module.__loader__ = None
        module.__spec__ = importlib.util.spec_from_loader(full_name, loader=None)
        sys.modules[full_name] = module
        exec(compile(sources[short_name], module.__file__, "exec"), module.__dict__)


_load_runtime_modules()

from .operators import CLASSES as OPERATOR_CLASSES  # noqa: E402
from .properties import CLASSES as PROPERTY_CLASSES  # noqa: E402
from .properties import RUG_Settings  # noqa: E402
from .ui import CLASSES as UI_CLASSES  # noqa: E402

CLASSES = PROPERTY_CLASSES + OPERATOR_CLASSES + UI_CLASSES


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.rug_settings = PointerProperty(type=RUG_Settings)


def unregister() -> None:
    if hasattr(bpy.types.Scene, "rug_settings"):
        del bpy.types.Scene.rug_settings
    for cls in reversed(CLASSES):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass


if __name__ == "__main__":
    register()
