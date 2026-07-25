"""Real Uniform Generator v0.5.0 runtime loader.

The implementation is stored as a compressed source payload.  The loader
normalises line wrapping and trailing newlines before strict Base64 decoding,
which keeps packages produced by GitHub, PowerShell and Blender's extension
builder interoperable.
"""

from __future__ import annotations

import base64
import binascii
import io
import importlib.util
from pathlib import Path
import sys
import types
from zipfile import BadZipFile, ZipFile

import bpy
from bpy.props import PointerProperty

bl_info = {
    "name": "Real Uniform Generator",
    "author": "tomicodev / OpenAI",
    "version": (0, 5, 0),
    "blender": (4, 3, 0),
    "location": "View3D > Sidebar > 制服",
    "description": "Generate pattern-based realistic Japanese school pleated skirts",
    "category": "Add Mesh",
}

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


def _decode_payload(payload_path: Path) -> bytes:
    """Decode a Base64 payload while tolerating harmless text formatting.

    GitHub's Contents API and some ZIP/build tools preserve a final newline or
    wrap long text lines.  ``base64.b64decode(..., validate=True)`` rejects
    those whitespace characters unless they are removed first.
    """
    encoded_text = payload_path.read_text(encoding="utf-8-sig")
    encoded_text = "".join(encoded_text.split())
    if not encoded_text:
        raise RuntimeError("runtime payload is empty")

    # Restore optional Base64 padding when an editor/build step removed it.
    encoded_text += "=" * (-len(encoded_text) % 4)
    try:
        return base64.b64decode(encoded_text, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise RuntimeError(
            f"runtime payload Base64 is invalid (characters={len(encoded_text)}): {exc}"
        ) from exc


def _read_runtime_sources(payload_path: Path) -> dict[str, str]:
    payload = _decode_payload(payload_path)
    try:
        with ZipFile(io.BytesIO(payload)) as archive:
            bad_member = archive.testzip()
            if bad_member is not None:
                raise RuntimeError(f"runtime ZIP member is corrupt: {bad_member}")

            available = set(archive.namelist())
            required = {f"{name}.py" for name in _MODULE_ORDER}
            missing = sorted(required - available)
            if missing:
                raise RuntimeError(
                    "runtime ZIP is missing modules: " + ", ".join(missing)
                )

            return {
                name: archive.read(f"{name}.py").decode("utf-8-sig")
                for name in _MODULE_ORDER
            }
    except BadZipFile as exc:
        raise RuntimeError(
            f"runtime payload is not a valid ZIP (decoded_bytes={len(payload)}): {exc}"
        ) from exc


def _load_runtime_modules() -> None:
    payload_path = Path(__file__).with_name("v05_runtime_payload.b64")
    if not payload_path.is_file():
        raise RuntimeError(
            f"Real Uniform Generator runtime payload is missing: {payload_path}"
        )

    try:
        sources = _read_runtime_sources(payload_path)
    except Exception as exc:
        raise RuntimeError(
            "Real Uniform Generator v0.5 runtime payload is invalid: "
            f"{type(exc).__name__}: {exc}"
        ) from exc

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

        source = sources[short_name]
        exec(compile(source, module.__file__, "exec"), module.__dict__)


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
