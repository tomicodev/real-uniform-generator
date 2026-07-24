import bpy

from .constants import FABRIC_MATERIAL, LINING_MATERIAL, METAL_MATERIAL, THREAD_MATERIAL


def _set_input(node, name, value):
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def _new_material(name):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    material.node_tree.nodes.clear()
    return material


def _fabric_preset(settings):
    presets = {
        'WINTER_NAVY': {
            'base': (0.010, 0.018, 0.042, 1.0),
            'light': (0.020, 0.038, 0.082, 1.0),
            'roughness': 0.82,
            'sheen': 0.28,
        },
        'SUMMER_NAVY': {
            'base': (0.014, 0.028, 0.066, 1.0),
            'light': (0.032, 0.060, 0.118, 1.0),
            'roughness': 0.70,
            'sheen': 0.18,
        },
        'CHARCOAL': {
            'base': (0.022, 0.026, 0.034, 1.0),
            'light': (0.070, 0.076, 0.090, 1.0),
            'roughness': 0.79,
            'sheen': 0.24,
        },
        'BLACK': {
            'base': (0.006, 0.007, 0.010, 1.0),
            'light': (0.026, 0.030, 0.036, 1.0),
            'roughness': 0.76,
            'sheen': 0.20,
        },
    }
    return presets[settings.fabric]


def create_fabric_material(settings):
    preset = _fabric_preset(settings)
    mat = _new_material(FABRIC_MATERIAL)
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (900, 40)
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (620, 40)
    _set_input(principled, 'Roughness', preset['roughness'])
    _set_input(principled, 'IOR', 1.46)
    _set_input(principled, 'Sheen Weight', preset['sheen'])
    _set_input(principled, 'Sheen Roughness', 0.66)

    texcoord = nodes.new('ShaderNodeTexCoord')
    texcoord.location = (-1000, 40)
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-820, 40)

    macro_noise = nodes.new('ShaderNodeTexNoise')
    macro_noise.location = (-620, 230)
    _set_input(macro_noise, 'Scale', 7.0)
    _set_input(macro_noise, 'Detail', 3.0)
    _set_input(macro_noise, 'Roughness', 0.68)

    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (-350, 245)
    color_ramp.color_ramp.elements[0].position = 0.22
    color_ramp.color_ramp.elements[0].color = preset['base']
    color_ramp.color_ramp.elements[1].position = 0.82
    color_ramp.color_ramp.elements[1].color = preset['light']

    warp = nodes.new('ShaderNodeTexNoise')
    warp.location = (-620, -20)
    _set_input(warp, 'Scale', 38.0)
    _set_input(warp, 'Detail', 2.0)
    _set_input(warp, 'Roughness', 0.62)

    wave_x = nodes.new('ShaderNodeTexWave')
    wave_x.location = (-390, -120)
    wave_x.wave_type = 'BANDS'
    wave_x.bands_direction = 'X'
    _set_input(wave_x, 'Scale', settings.weave_scale)
    _set_input(wave_x, 'Distortion', 2.2)
    _set_input(wave_x, 'Detail', 2.0)
    _set_input(wave_x, 'Detail Scale', 1.5)

    wave_y = nodes.new('ShaderNodeTexWave')
    wave_y.location = (-390, -300)
    wave_y.wave_type = 'BANDS'
    wave_y.bands_direction = 'Y'
    _set_input(wave_y, 'Scale', settings.weave_scale * 0.92)
    _set_input(wave_y, 'Distortion', 2.0)
    _set_input(wave_y, 'Detail', 2.0)
    _set_input(wave_y, 'Detail Scale', 1.4)

    weave_mix = nodes.new('ShaderNodeMixRGB')
    weave_mix.location = (-100, -190)
    weave_mix.blend_type = 'MULTIPLY'
    weave_mix.inputs[0].default_value = 1.0

    fiber_noise = nodes.new('ShaderNodeTexNoise')
    fiber_noise.location = (-120, -390)
    _set_input(fiber_noise, 'Scale', settings.weave_scale * 1.75)
    _set_input(fiber_noise, 'Detail', 1.0)
    _set_input(fiber_noise, 'Roughness', 0.72)

    height_mix = nodes.new('ShaderNodeMixRGB')
    height_mix.location = (130, -210)
    height_mix.blend_type = 'MULTIPLY'
    height_mix.inputs[0].default_value = 0.72

    bump = nodes.new('ShaderNodeBump')
    bump.location = (370, -170)
    _set_input(bump, 'Strength', settings.weave_strength)
    _set_input(bump, 'Distance', 0.0011)

    rough_noise = nodes.new('ShaderNodeTexNoise')
    rough_noise.location = (110, 120)
    _set_input(rough_noise, 'Scale', 24.0)
    _set_input(rough_noise, 'Detail', 2.0)
    rough_ramp = nodes.new('ShaderNodeValToRGB')
    rough_ramp.location = (360, 145)
    rough_ramp.color_ramp.elements[0].color = (preset['roughness'] - 0.05,) * 3 + (1.0,)
    rough_ramp.color_ramp.elements[1].color = (min(1.0, preset['roughness'] + 0.08),) * 3 + (1.0,)

    links.new(texcoord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], macro_noise.inputs['Vector'])
    links.new(mapping.outputs['Vector'], warp.inputs['Vector'])
    links.new(mapping.outputs['Vector'], wave_x.inputs['Vector'])
    links.new(mapping.outputs['Vector'], wave_y.inputs['Vector'])
    links.new(mapping.outputs['Vector'], fiber_noise.inputs['Vector'])
    links.new(mapping.outputs['Vector'], rough_noise.inputs['Vector'])
    links.new(macro_noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
    links.new(wave_x.outputs['Color'], weave_mix.inputs[1])
    links.new(wave_y.outputs['Color'], weave_mix.inputs[2])
    links.new(weave_mix.outputs['Color'], height_mix.inputs[1])
    links.new(fiber_noise.outputs['Fac'], height_mix.inputs[2])
    links.new(height_mix.outputs['Color'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    links.new(rough_noise.outputs['Fac'], rough_ramp.inputs['Fac'])
    links.new(rough_ramp.outputs['Color'], principled.inputs['Roughness'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_lining_material():
    mat = _new_material(LINING_MATERIAL)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    bump = nodes.new('ShaderNodeBump')
    texcoord = nodes.new('ShaderNodeTexCoord')

    _set_input(principled, 'Base Color', (0.018, 0.024, 0.040, 1.0))
    _set_input(principled, 'Roughness', 0.42)
    _set_input(principled, 'Sheen Weight', 0.32)
    _set_input(noise, 'Scale', 180.0)
    _set_input(noise, 'Detail', 1.0)
    _set_input(bump, 'Strength', 0.035)
    _set_input(bump, 'Distance', 0.0005)

    links.new(texcoord.outputs['Generated'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_thread_material():
    mat = _new_material(THREAD_MATERIAL)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    _set_input(principled, 'Base Color', (0.035, 0.045, 0.072, 1.0))
    _set_input(principled, 'Roughness', 0.92)
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def create_metal_material():
    mat = _new_material(METAL_MATERIAL)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    _set_input(principled, 'Base Color', (0.18, 0.20, 0.23, 1.0))
    _set_input(principled, 'Metallic', 0.82)
    _set_input(principled, 'Roughness', 0.28)
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat


def build_materials(settings):
    return {
        'fabric': create_fabric_material(settings),
        'lining': create_lining_material(),
        'thread': create_thread_material(),
        'metal': create_metal_material(),
    }
