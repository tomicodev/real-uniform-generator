bl_info = {
    'name': 'Real Uniform Generator',
    'author': 'tomicodev / OpenAI',
    'version': (0, 2, 0),
    'blender': (4, 3, 0),
    'location': 'View3D > Sidebar > Uniform',
    'description': 'Generate realistic configurable Japanese school pleated skirts',
    'category': 'Add Mesh',
}

import bpy
from bpy.props import PointerProperty

from .operators import CLASSES as OPERATOR_CLASSES
from .properties import CLASSES as PROPERTY_CLASSES
from .properties import RUG_Settings
from .ui import CLASSES as UI_CLASSES


CLASSES = PROPERTY_CLASSES + OPERATOR_CLASSES + UI_CLASSES


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.rug_settings = PointerProperty(type=RUG_Settings)


def unregister():
    if hasattr(bpy.types.Scene, 'rug_settings'):
        del bpy.types.Scene.rug_settings
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
