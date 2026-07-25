"""Real Uniform Generator - Blender 5.2 extension."""
from __future__ import annotations

import bpy
from bpy.props import PointerProperty

from . import operators, properties, ui

bl_info = {
    "name": "Real Uniform Generator",
    "author": "tomicodev / OpenAI",
    "version": (0, 6, 0),
    "blender": (5, 2, 0),
    "location": "View3D > Sidebar > 制服",
    "description": "Generate a construction-based Japanese uniform pleated skirt",
    "category": "Add Mesh",
}

CLASSES = properties.CLASSES + operators.CLASSES + ui.CLASSES


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.rug_settings = PointerProperty(type=properties.RUG_Settings)


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
