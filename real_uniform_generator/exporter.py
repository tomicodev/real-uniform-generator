from pathlib import Path

import bpy

from .constants import EXPORT_COLLECTION
from .geometry import generated_objects


def _remove_collection(name):
    collection = bpy.data.collections.get(name)
    if collection is None:
        return
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(collection)


def _make_temp_collection():
    _remove_collection(EXPORT_COLLECTION)
    collection = bpy.data.collections.new(EXPORT_COLLECTION)
    bpy.context.scene.collection.children.link(collection)
    return collection


def _eligible_object(obj, settings):
    part = obj.get('rug_part', 'outer')
    if part == 'lining' and not settings.export_lining:
        return False
    if part == 'hardware' and not settings.export_hardware:
        return False
    return obj.type in {'MESH', 'CURVE'}


def _duplicate_for_export(settings):
    collection = _make_temp_collection()
    duplicates = []
    source_objects = [obj for obj in generated_objects() if _eligible_object(obj, settings)]

    for source in source_objects:
        duplicate = source.copy()
        if source.data is not None:
            duplicate.data = source.data.copy()
        duplicate.animation_data_clear()
        duplicate.parent = None
        duplicate.matrix_world = source.matrix_world.copy()
        collection.objects.link(duplicate)
        duplicates.append(duplicate)

    for duplicate in list(duplicates):
        if duplicate.type != 'CURVE':
            continue
        bpy.ops.object.select_all(action='DESELECT')
        duplicate.select_set(True)
        bpy.context.view_layer.objects.active = duplicate
        bpy.ops.object.convert(target='MESH')

    duplicates = [obj for obj in collection.objects if obj.type == 'MESH']
    if settings.apply_modifiers:
        for duplicate in duplicates:
            bpy.ops.object.select_all(action='DESELECT')
            duplicate.select_set(True)
            bpy.context.view_layer.objects.active = duplicate
            for modifier in list(duplicate.modifiers):
                try:
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
                except RuntimeError:
                    pass
    return collection, duplicates


def _select_only(objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.select_set(True)
    if objects:
        bpy.context.view_layer.objects.active = objects[0]


def export_skirt(filepath, settings):
    path = Path(filepath).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    collection = None

    try:
        collection, duplicates = _duplicate_for_export(settings)
        if not duplicates:
            raise RuntimeError('書き出し対象のメッシュがありません')
        _select_only(duplicates)

        if settings.export_format == 'GLB':
            path = path.with_suffix('.glb')
            bpy.ops.export_scene.gltf(
                filepath=str(path),
                export_format='GLB',
                use_selection=True,
                export_apply=True,
                export_materials='EXPORT',
                export_yup=True,
            )
        elif settings.export_format == 'FBX':
            path = path.with_suffix('.fbx')
            bpy.ops.export_scene.fbx(
                filepath=str(path),
                use_selection=True,
                apply_unit_scale=True,
                bake_space_transform=False,
                add_leaf_bones=False,
                mesh_smooth_type='FACE',
                path_mode='AUTO',
            )
        else:
            path = path.with_suffix('.obj')
            if hasattr(bpy.ops.wm, 'obj_export'):
                bpy.ops.wm.obj_export(
                    filepath=str(path),
                    export_selected_objects=True,
                    export_materials=True,
                    apply_modifiers=True,
                )
            else:
                bpy.ops.export_scene.obj(
                    filepath=str(path),
                    use_selection=True,
                    use_materials=True,
                    use_mesh_modifiers=True,
                )
        return path
    finally:
        bpy.ops.object.select_all(action='DESELECT')
        if collection is not None:
            _remove_collection(EXPORT_COLLECTION)
