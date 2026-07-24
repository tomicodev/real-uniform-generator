from pathlib import Path
import re

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


def _safe_filename(value):
    cleaned = re.sub(r'[^A-Za-z0-9_.-]+', '_', value).strip('_')
    return cleaned or 'texture'


def _pbr_images():
    return [
        image for image in bpy.data.images
        if image.get('rug_map_type') in {'base_color', 'roughness', 'normal'}
    ]


def _write_external_images(export_path):
    texture_dir = export_path.parent / f'{export_path.stem}_textures'
    texture_dir.mkdir(parents=True, exist_ok=True)
    state = []

    for image in _pbr_images():
        old_path = image.filepath_raw
        old_format = image.file_format
        target = texture_dir / f'{_safe_filename(image.name)}.png'
        image.filepath_raw = str(target)
        image.file_format = 'PNG'
        image.save()
        state.append((image, old_path, old_format))
    return state, texture_dir


def _restore_image_paths(state):
    for image, old_path, old_format in state:
        image.filepath_raw = old_path
        image.file_format = old_format


def export_skirt(filepath, settings):
    path = Path(filepath).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    collection = None
    image_state = []

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
            image_state, _ = _write_external_images(path)
            bpy.ops.export_scene.fbx(
                filepath=str(path),
                use_selection=True,
                apply_unit_scale=True,
                bake_space_transform=False,
                add_leaf_bones=False,
                mesh_smooth_type='FACE',
                path_mode='COPY',
                embed_textures=True,
            )
        else:
            path = path.with_suffix('.obj')
            image_state, _ = _write_external_images(path)
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
                    path_mode='RELATIVE',
                )
        return path
    finally:
        _restore_image_paths(image_state)
        bpy.ops.object.select_all(action='DESELECT')
        if collection is not None:
            _remove_collection(EXPORT_COLLECTION)
