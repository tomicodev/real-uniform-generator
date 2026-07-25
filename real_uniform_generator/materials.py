from __future__ import annotations

import bpy
from .material_io import load_external_pbr


def _set(node, name, value):
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def _material(name):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.node_tree.nodes.clear()
    return mat


def _principled(nodes):
    node = nodes.new('ShaderNodeBsdfPrincipled')
    _set(node, 'Metallic', 0.0)
    _set(node, 'Roughness', 0.78)
    _set(node, 'IOR', 1.46)
    _set(node, 'Coat Weight', 0.0)
    _set(node, 'Clearcoat', 0.0)
    _set(node, 'Sheen Weight', 0.08)
    _set(node, 'Sheen Roughness', 0.72)
    return node


def _image_node(nodes, image, label, location):
    node = nodes.new('ShaderNodeTexImage')
    node.image = image
    node.label = label
    node.location = location
    node.interpolation = 'Linear'
    node.extension = 'REPEAT'
    return node


def _normal_color(nodes, links, texture, directx):
    if not directx:
        return texture.outputs['Color']
    separate = nodes.new('ShaderNodeSeparateColor')
    separate.mode = 'RGB'
    invert = nodes.new('ShaderNodeMath')
    invert.operation = 'SUBTRACT'
    invert.inputs[0].default_value = 1.0
    combine = nodes.new('ShaderNodeCombineColor')
    combine.mode = 'RGB'
    links.new(texture.outputs['Color'], separate.inputs['Color'])
    links.new(separate.outputs['Red'], combine.inputs['Red'])
    links.new(separate.outputs['Green'], invert.inputs[1])
    links.new(invert.outputs[0], combine.inputs['Green'])
    links.new(separate.outputs['Blue'], combine.inputs['Blue'])
    return combine.outputs['Color']


def _external_fabric(mat, settings, maps):
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (760, 40)
    bsdf = _principled(nodes)
    bsdf.location = (490, 40)
    uv = nodes.new('ShaderNodeUVMap')
    uv.uv_map = 'UVMap'
    uv.location = (-850, 40)
    base = _image_node(nodes, maps['base_color'], 'Base Color', (-600, 260))
    links.new(uv.outputs['UV'], base.inputs['Vector'])
    base_output = base.outputs['Color']
    if 'ao' in maps:
        ao = _image_node(nodes, maps['ao'], 'Ambient Occlusion', (-600, 90))
        mix = nodes.new('ShaderNodeMixRGB')
        mix.blend_type = 'MULTIPLY'
        mix.inputs[0].default_value = settings.ao_strength
        links.new(uv.outputs['UV'], ao.inputs['Vector'])
        links.new(base_output, mix.inputs[1])
        links.new(ao.outputs['Color'], mix.inputs[2])
        base_output = mix.outputs['Color']
    links.new(base_output, bsdf.inputs['Base Color'])
    if 'roughness' in maps:
        rough = _image_node(nodes, maps['roughness'], 'Roughness', (-600, -80))
        links.new(uv.outputs['UV'], rough.inputs['Vector'])
        links.new(rough.outputs['Color'], bsdf.inputs['Roughness'])
    normal_output = None
    if 'normal' in maps:
        normal_tex = _image_node(nodes, maps['normal'], 'Normal', (-600, -260))
        links.new(uv.outputs['UV'], normal_tex.inputs['Vector'])
        normal_map = nodes.new('ShaderNodeNormalMap')
        normal_map.space = 'TANGENT'
        normal_map.uv_map = 'UVMap'
        _set(normal_map, 'Strength', settings.normal_strength)
        links.new(_normal_color(nodes, links, normal_tex, maps.get('_normal_directx', False)), normal_map.inputs['Color'])
        normal_output = normal_map.outputs['Normal']
    if 'height' in maps:
        height = _image_node(nodes, maps['height'], 'Height', (-600, -440))
        bump = nodes.new('ShaderNodeBump')
        _set(bump, 'Strength', settings.height_strength)
        _set(bump, 'Distance', 0.00045)
        links.new(uv.outputs['UV'], height.inputs['Vector'])
        links.new(height.outputs['Color'], bump.inputs['Height'])
        if normal_output is not None:
            links.new(normal_output, bump.inputs['Normal'])
        normal_output = bump.outputs['Normal']
    if normal_output is not None:
        links.new(normal_output, bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    mat['rug_external_pbr'] = True
    mat['rug_normal_directx'] = bool(maps.get('_normal_directx'))
    return mat


def _procedural_fabric(mat, settings):
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = _principled(nodes)
    _set(bsdf, 'Base Color', (0.0035, 0.0075, 0.0240, 1.0))
    _set(bsdf, 'Roughness', 0.80)
    uv = nodes.new('ShaderNodeUVMap')
    uv.uv_map = 'UVMap'
    mapping = nodes.new('ShaderNodeMapping')
    scale = settings.texture_tile_cm / max(settings.weave_size_cm, 0.01)
    mapping.inputs['Scale'].default_value = (scale, scale, 1.0)
    wave_x = nodes.new('ShaderNodeTexWave')
    wave_x.wave_type = 'BANDS'
    wave_x.bands_direction = 'X'
    _set(wave_x, 'Scale', 1.0)
    _set(wave_x, 'Distortion', 0.35)
    wave_y = nodes.new('ShaderNodeTexWave')
    wave_y.wave_type = 'BANDS'
    wave_y.bands_direction = 'Y'
    _set(wave_y, 'Scale', 1.0)
    _set(wave_y, 'Distortion', 0.35)
    weave = nodes.new('ShaderNodeMixRGB')
    weave.blend_type = 'MULTIPLY'
    weave.inputs[0].default_value = 1.0
    bump = nodes.new('ShaderNodeBump')
    _set(bump, 'Strength', min(0.22, settings.normal_strength * 0.42))
    _set(bump, 'Distance', 0.00025)
    links.new(uv.outputs['UV'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], wave_x.inputs['Vector'])
    links.new(mapping.outputs['Vector'], wave_y.inputs['Vector'])
    links.new(wave_x.outputs['Color'], weave.inputs[1])
    links.new(wave_y.outputs['Color'], weave.inputs[2])
    links.new(weave.outputs['Color'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    mat['rug_external_pbr'] = False
    mat['rug_normal_directx'] = False
    return mat


def create_fabric_material(settings):
    mat = _material('RUG_Fabric')
    if settings.use_external_pbr and settings.texture_directory:
        maps, files = load_external_pbr(settings)
        mat['rug_pbr_files'] = ';'.join(f'{key}:{path.name}' for key, path in files.items())
        return _external_fabric(mat, settings, maps)
    return _procedural_fabric(mat, settings)


def _simple(name, base, roughness, metallic=0.0, sheen=0.0):
    mat = _material(name)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = _principled(nodes)
    _set(bsdf, 'Base Color', base)
    _set(bsdf, 'Roughness', roughness)
    _set(bsdf, 'Metallic', metallic)
    _set(bsdf, 'Sheen Weight', sheen)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat


def build_materials(settings):
    return {
        'fabric': create_fabric_material(settings),
        'lining': _simple('RUG_LiningMaterial', (0.030, 0.040, 0.075, 1.0), 0.46, 0.0, 0.12),
        'thread': _simple('RUG_ThreadMaterial', (0.018, 0.028, 0.060, 1.0), 0.94),
        'metal': _simple('RUG_MetalMaterial', (0.15, 0.17, 0.20, 1.0), 0.30, 0.82),
        'zipper': _simple('RUG_ZipperMaterial', (0.020, 0.026, 0.050, 1.0), 0.72, 0.0, 0.03),
        'interfacing': _simple('RUG_InterfacingMaterial', (0.12, 0.13, 0.14, 1.0), 0.96),
    }
