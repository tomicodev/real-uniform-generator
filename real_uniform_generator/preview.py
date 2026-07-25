from __future__ import annotations

from pathlib import Path
import bpy
from mathutils import Vector

PREVIEW_COLLECTION = 'RUG_PreviewStudio'


def _collection():
    collection = bpy.data.collections.get(PREVIEW_COLLECTION)
    if collection is None:
        collection = bpy.data.collections.new(PREVIEW_COLLECTION)
        bpy.context.scene.collection.children.link(collection)
    return collection


def clear_preview():
    collection = bpy.data.collections.get(PREVIEW_COLLECTION)
    if collection is None:
        return
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(collection)


def _link(obj):
    collection = _collection()
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def _aim(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def _area(name, location, energy, size, target=(0, 0, -0.22)):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = 'DISK'
    data.size = size
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    _aim(obj, target)
    _link(obj)
    return obj


def create_preview_scene(settings):
    clear_preview()
    scene = bpy.context.scene
    requested = settings.render_engine
    supported = {item.identifier for item in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items}
    if requested not in supported and requested == 'BLENDER_EEVEE_NEXT' and 'BLENDER_EEVEE' in supported:
        requested = 'BLENDER_EEVEE'
    scene.render.engine = requested if requested in supported else ('BLENDER_EEVEE' if 'BLENDER_EEVEE' in supported else next(iter(supported)))
    scene.render.resolution_x = 700
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False
    world = scene.world or bpy.data.worlds.new('RUG_World')
    scene.world = world
    world.use_nodes = True
    background = next((node for node in world.node_tree.nodes if node.bl_idname == 'ShaderNodeBackground'), None)
    if background is None:
        background = world.node_tree.nodes.new('ShaderNodeBackground')
        output = next((node for node in world.node_tree.nodes if node.bl_idname == 'ShaderNodeOutputWorld'), None)
        if output is None:
            output = world.node_tree.nodes.new('ShaderNodeOutputWorld')
        world.node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])
    background.inputs['Color'].default_value = (0.055, 0.065, 0.085, 1.0)
    background.inputs['Strength'].default_value = 0.28
    scene.view_settings.exposure = -0.75
    bpy.ops.mesh.primitive_plane_add(size=4.0, location=(0, 0, -settings.skirt_length - 0.045))
    floor = bpy.context.object
    floor.name = 'RUG_PreviewFloor'
    _link(floor)
    mat = bpy.data.materials.get('RUG_FloorMaterial') or bpy.data.materials.new('RUG_FloorMaterial')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    floor_bsdf = next((node for node in nodes if node.bl_idname == 'ShaderNodeBsdfPrincipled'), None)
    if floor_bsdf is None:
        nodes.clear()
        floor_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        floor_output = nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(floor_bsdf.outputs['BSDF'], floor_output.inputs['Surface'])
    floor_bsdf.inputs['Base Color'].default_value = (0.040, 0.045, 0.055, 1.0)
    floor_bsdf.inputs['Roughness'].default_value = 0.88
    floor.data.materials.append(mat)
    _area('RUG_Key', (-1.1, -1.4, 1.2), 180.0, 1.0)
    _area('RUG_Fill', (1.2, -0.5, 0.55), 70.0, 0.8)
    _area('RUG_Rim', (0.0, 1.3, 0.8), 125.0, 0.7)
    internal_fill = _area('RUG_InternalFill', (0.16, -0.18, 0.18), 22.0, 0.35, target=(-0.13, 0.0, -0.09))
    internal_fill.hide_render = True
    camera_data = bpy.data.cameras.new('RUG_PreviewCamera')
    camera = bpy.data.objects.new('RUG_PreviewCamera', camera_data)
    _link(camera)
    scene.camera = camera
    set_view('FRONT', settings)
    return camera


def set_view(view, settings):
    camera = bpy.data.objects.get('RUG_PreviewCamera')
    if camera is None:
        camera = create_preview_scene(settings)
    target = (0.0, 0.0, -0.22)
    positions = {
        'FRONT': ((0.0, -1.45, 0.02), 62.0),
        'SIDE': ((-1.35, -0.02, 0.02), 64.0),
        'BACK': ((0.0, 1.45, 0.02), 62.0),
        'INSIDE': ((0.42, -1.12, -0.12), 58.0),
        'ZIPPER': ((0.22, -0.02, -0.09), 62.0),
    }
    position, lens = positions[view]
    camera.location = position
    camera.data.lens = lens
    camera.data.clip_start = 0.01 if view == 'ZIPPER' else 0.05
    if view == 'INSIDE':
        target = (0.0, 0.0, -0.19)
    elif view == 'ZIPPER':
        target = (-0.13, 0.0, -0.09)
    _aim(camera, target)
    floor = bpy.data.objects.get('RUG_PreviewFloor')
    if floor:
        floor.hide_render = view in {'INSIDE', 'ZIPPER'}
    internal_fill = bpy.data.objects.get('RUG_InternalFill')
    if internal_fill:
        internal_fill.hide_render = view not in {'INSIDE', 'ZIPPER'}
    return camera


def render_view(view, filepath, settings):
    set_view(view, settings)
    path = Path(bpy.path.abspath(str(filepath))).with_suffix('.png')
    path.parent.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.render.filepath = str(path)

    changed = {}

    def set_hidden(name, state):
        obj = bpy.data.objects.get(name)
        if obj is not None:
            changed[name] = obj.hide_render
            obj.hide_render = state

    if view == 'INSIDE':
        set_hidden('RUG_SkirtOuter', True)
        set_hidden('RUG_LeftSideSeam', True)
    elif view == 'ZIPPER':
        set_hidden('RUG_SkirtOuter', True)
        set_hidden('RUG_Lining', True)
        set_hidden('RUG_LeftSideSeam', True)

    try:
        bpy.ops.render.render(write_still=True, scene=scene.name)
    finally:
        for name, state in changed.items():
            obj = bpy.data.objects.get(name)
            if obj is not None:
                obj.hide_render = state
    return path
