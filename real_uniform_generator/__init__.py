"""Real Uniform Generator v0.5.0 runtime loader.

The implementation is stored as a compressed source payload. The loader
normalises harmless text formatting and can recover a valid ZIP when an archive
or text transport inserted stray non-Base64 separator characters.
"""

from __future__ import annotations

import base64
import binascii
import io
import importlib.util
from pathlib import Path
import re
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
_BASE64_FRAGMENT = re.compile(r"[A-Za-z0-9+/=]+")
_BASE64_INVALID = re.compile(r"[^A-Za-z0-9+/=]+")


def _pad_base64(value: str) -> str:
    return value + "=" * (-len(value) % 4)


def _encoded_candidates(payload_path: Path):
    """Yield conservative Base64 repair candidates in priority order."""
    raw_text = payload_path.read_text(encoding="utf-8-sig")
    compact = "".join(raw_text.split())
    if not compact:
        raise RuntimeError("runtime payload is empty")

    seen: set[str] = set()

    def emit(label: str, value: str):
        value = _pad_base64(value)
        if value and value not in seen:
            seen.add(value)
            return label, value
        return None

    candidate = emit("normalised", compact)
    if candidate:
        yield candidate

    # Some transports accidentally substitute URL-safe Base64 characters.
    urlsafe = compact.translate(str.maketrans("-_", "+/"))
    candidate = emit("urlsafe-normalised", urlsafe)
    if candidate:
        yield candidate

    # Remove only characters that can never belong to standard Base64.
    filtered = _BASE64_INVALID.sub("", compact)
    candidate = emit("non-base64-filtered", filtered)
    if candidate:
        yield candidate

    # If a transport inserted a textual marker between chunks, retain only
    # substantial Base64 runs. Short words such as 'truncated' are discarded.
    fragments = _BASE64_FRAGMENT.findall(compact)
    long_joined = "".join(fragment for fragment in fragments if len(fragment) >= 24)
    candidate = emit("long-fragments", long_joined)
    if candidate:
        yield candidate


def _decode_candidates(payload_path: Path):
    errors: list[str] = []
    for label, encoded_text in _encoded_candidates(payload_path):
        try:
            yield label, base64.b64decode(encoded_text, validate=True)
        except (binascii.Error, ValueError) as exc:
            errors.append(f"{label}: {exc}")
    if errors:
        raise RuntimeError("; ".join(errors))
    raise RuntimeError("no Base64 candidates were produced")


def _read_runtime_sources(payload_path: Path) -> dict[str, str]:
    required = {f"{name}.py" for name in _MODULE_ORDER}
    errors: list[str] = []

    for label, payload in _decode_candidates(payload_path):
        try:
            with ZipFile(io.BytesIO(payload)) as archive:
                bad_member = archive.testzip()
                if bad_member is not None:
                    raise RuntimeError(f"ZIP member is corrupt: {bad_member}")

                available = set(archive.namelist())
                missing = sorted(required - available)
                if missing:
                    raise RuntimeError("ZIP is missing modules: " + ", ".join(missing))

                sources = {
                    name: archive.read(f"{name}.py").decode("utf-8-sig")
                    for name in _MODULE_ORDER
                }
                for name, source in sources.items():
                    compile(source, f"{payload_path}!/{name}.py", "exec")
                return sources
        except (BadZipFile, RuntimeError, UnicodeDecodeError, SyntaxError) as exc:
            errors.append(f"{label}: {type(exc).__name__}: {exc}")

    raise RuntimeError("payload recovery failed; " + " | ".join(errors))


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
