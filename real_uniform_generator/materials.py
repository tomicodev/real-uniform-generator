import bpy

from .constants import FABRIC_MATERIAL, LINING_MATERIAL, METAL_MATERIAL, THREAD_MATERIAL
from .textures import generate_fabric_textures


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
        'WINTER_NAVY': {'roughness': 0.82, 'sheen': 0.28, 'fallback': (0.010, 0.018, 0.042, 1.0)},
        'SUMMER_NAVY': {'roughness': 0.70, 'sheen': 0.18, 'fallback': (0.014, 0.028, 0.066, 1.0)},
        'CHARCOAL': {'roughness': 0.79, 'sheen': 0.24, 'fallback': (0.022, 0.026, 0.034, 1.0)},
        'BLACK': {'roughness': 0.76, 'sheen': 0.20, 'fallback': (0.006, 0.007, 0.010, 1.0)},
    }
    return presets[settings.fabric]


def _create_fallback_fabric_nodes(material, settings, preset):
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    texcoord = nodes.new('ShaderNodeTexCoord')
    wave = nodes.new('ShaderNodeTexWave')
    noise = nodes.new('ShaderNodeTexNoise')
    bump = nodes.new('ShaderNodeBump')

    _set_input(principled, 'Base Color', preset['fallback'])
    _set_input(principled, 'Roughness', preset['roughness'])
    _set_input(principled, 'IOR', 1.46)
    _set_input(principled, 'Sheen Weight', preset['sheen'])
    _set_input(principled, 'Sheen Roughness', 0.66)
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'X'
    _set_input(wave, 'Scale', settings.weave_scale)
    _set_input(wave, 'Distortion', 2.0)
    _set_input(noise, 'Scale', settings.weave_scale * 0.65)
    _set_input(noise, 'Detail', 2.0)
    _set_input(bump, 'Strength', settings.weave_strength)
    _set_input(bump, 'Distance', 0.0010)

    links.new(texcoord.outputs['Generated'], wave.inputs['Vector'])
    links.new(texcoord.outputs['Generated'], noise.inputs['Vector'])
    links.new(wave.outputs['Color'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    material['rug_exportable_textures'] = False
    return material


def create_fabric_material(settings):
    preset = _fabric_preset(settings)
    material = _new_material(FABRIC_MATERIAL)
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    try:
        maps = generate_fabric_textures(settings)
    except Exception as exc:
        print(f'Real Uniform Generator: PBR texture generation failed, using fallback nodes: {exc}')
        return _create_fallback_fabric_nodes(material, settings, preset)

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (680, 40)
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (390, 40)
    _set_input(principled, 'Roughness', preset['roughness'])
    _set_input(principled, 'IOR', 1.46)
    _set_input(principled, 'Sheen Weight', preset['sheen'])
    _set_input(principled, 'Sheen Roughness', 0.66)

    uv = nodes.new('ShaderNodeUVMap')
    uv.location = (-720, 20)
    uv.uv_map = 'UVMap'

    base = nodes.new('ShaderNodeTexImage')
    base.location = (-480, 230)
    base.label = 'Packed Base Color'
    base.image = maps['base_color']
    base.interpolation = 'Linear'
    base.extension = 'REPEAT'

    roughness = nodes.new('ShaderNodeTexImage')
    roughness.location = (-480, 20)
    roughness.label = 'Packed Roughness'
    roughness.image = maps['roughness']
    roughness.interpolation = 'Linear'
    roughness.extension = 'REPEAT'

    normal_texture = nodes.new('ShaderNodeTexImage')
    normal_texture.location = (-480, -210)
    normal_texture.label = 'Packed Normal'
    normal_texture.image = maps['normal']
    normal_texture.interpolation = 'Linear'
    normal_texture.extension = 'REPEAT'

    normal_map = nodes.new('ShaderNodeNormalMap')
    normal_map.location = (80, -170)
    normal_map.space = 'TANGENT'
    normal_map.uv_map = 'UVMap'
    _set_input(normal_map, 'Strength', 0.72 + settings.weave_strength * 1.8)

    links.new(uv.outputs['UV'], base.inputs['Vector'])
    links.new(uv.outputs['UV'], roughness.inputs['Vector'])
    links.new(uv.outputs['UV'], normal_texture.inputs['Vector'])
    links.new(base.outputs['Color'], principled.inputs['Base Color'])
    links.new(roughness.outputs['Color'], principled.inputs['Roughness'])
    links.new(normal_texture.outputs['Color'], normal_map.inputs['Color'])
    links.new(normal_map.outputs['Normal'], principled.inputs['Normal'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])

    material['rug_exportable_textures'] = True
    material['rug_texture_resolution'] = int(settings.texture_resolution)
    return material


def create_lining_material():
    material = _new_material(LINING_MATERIAL)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
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
    return material


def create_thread_material():
    material = _new_material(THREAD_MATERIAL)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    _set_input(principled, 'Base Color', (0.035, 0.045, 0.072, 1.0))
    _set_input(principled, 'Roughness', 0.92)
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return material


def create_metal_material():
    material = _new_material(METAL_MATERIAL)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    _set_input(principled, 'Base Color', (0.18, 0.20, 0.23, 1.0))
    _set_input(principled, 'Metallic', 0.82)
    _set_input(principled, 'Roughness', 0.28)
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return material


def build_materials(settings):
    return {
        'fabric': create_fabric_material(settings),
        'lining': create_lining_material(),
        'thread': create_thread_material(),
        'metal': create_metal_material(),
    }
