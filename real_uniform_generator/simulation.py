from __future__ import annotations


def configure_cloth(obj, settings):
    modifier = obj.modifiers.new('Optional Cloth Relaxation', 'CLOTH')
    cloth = modifier.settings
    if hasattr(cloth, 'quality'):
        cloth.quality = 8
    for name, value in (
        ('tension_stiffness', 35.0),
        ('compression_stiffness', 35.0),
        ('shear_stiffness', 18.0),
        ('bending_stiffness', 1.2),
        ('air_damping', 2.0),
    ):
        if hasattr(cloth, name):
            setattr(cloth, name, value)
    modifier.show_viewport = False
    modifier.show_render = False
    obj['rug_simulation_ready'] = True
    return modifier
