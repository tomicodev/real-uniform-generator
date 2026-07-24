import math

import bpy
from mathutils import Vector

from .constants import PREVIEW_COLLECTION


def _ensure_collection():
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


def _link(obj, collection):
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    collection.objects.link(obj)


def _look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def _simple_material(name, color, roughness):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1.0)
    material.roughness = roughness
    return material


def _set_compatible_render_engine(scene):
    """Select the available Eevee identifier across Blender 4.x and 5.x."""
    engine_property = scene.render.bl_rna.properties.get('engine')
    available = (
        {item.identifier for item in engine_property.enum_items}
        if engine_property is not None
        else set()
    )

    for candidate in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT', 'BLENDER_WORKBENCH'):
        if candidate in available:
            scene.render.engine = candidate
            return candidate

    raise RuntimeError(
        '利用可能なレンダーエンジンが見つかりません: '
        + ', '.join(sorted(available))
    )


def create_preview_scene(settings):
    clear_preview()
    collection = _ensure_collection()

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=160,
        radius=max(settings.hem_width, settings.hem_depth) * 1.65,
        depth=0.035,
        location=(0.0, 0.0, -settings.skirt_length - 0.035),
    )
    stage = bpy.context.object
    stage.name = 'RUG_PreviewStage'
    _link(stage, collection)
    stage.data.materials.append(_simple_material('RUG_PreviewStageMaterial', (0.11, 0.125, 0.15), 0.88))

    bpy.ops.mesh.primitive_plane_add(
        size=10.0,
        location=(0.0, 0.0, -settings.skirt_length - 0.058),
    )
    floor = bpy.context.object
    floor.name = 'RUG_PreviewFloor'
    _link(floor, collection)
    floor.data.materials.append(_simple_material('RUG_PreviewFloorMaterial', (0.035, 0.042, 0.052), 0.94))

    lights = (
        ('RUG_KeyLight', (2.4, -2.8, 2.5), 850.0, 2.4),
        ('RUG_FillLight', (-2.6, -1.2, 1.3), 420.0, 3.2),
        ('RUG_RimLight', (0.7, 2.4, 2.0), 620.0, 2.0),
    )
    for name, location, energy, size in lights:
        bpy.ops.object.light_add(type='AREA', location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.shape = 'DISK'
        light.data.size = size
        _look_at(light, (0.0, 0.0, -settings.skirt_length * 0.48))
        _link(light, collection)

    bpy.ops.object.camera_add(location=(1.25, -1.55, 0.45))
    camera = bpy.context.object
    camera.name = 'RUG_PreviewCamera'
    camera.data.lens = 58
    camera.data.sensor_width = 36
    _look_at(camera, (0.0, 0.0, -settings.skirt_length * 0.48))
    _link(camera, collection)
    bpy.context.scene.camera = camera

    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new('RUG_World')
        bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get('Background')
    if background is not None:
        background.inputs['Color'].default_value = (0.028, 0.034, 0.045, 1.0)
        background.inputs['Strength'].default_value = 0.34

    scene = bpy.context.scene
    _set_compatible_render_engine(scene)
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1350
    scene.render.resolution_percentage = 70
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False

    for area in bpy.context.screen.areas if bpy.context.screen else []:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'MATERIAL'
            area.spaces.active.shading.light = 'STUDIO'
            area.spaces.active.shading.show_shadows = True
            area.spaces.active.shading.show_cavity = True
    return camera
