from __future__ import annotations

from pathlib import Path
import bpy
from .geometry import generated_objects


def _select_for_export(settings):
    bpy.ops.object.select_all(action='DESELECT')
    selected = []
    for obj in generated_objects():
        part = obj.get('rug_part', '')
        if part == 'lining' and not settings.export_lining:
            continue
        if part in {'hardware', 'zipper'} and not settings.export_hardware:
            continue
        if obj.type in {'MESH', 'CURVE'}:
            obj.select_set(True)
            selected.append(obj)
    if selected:
        bpy.context.view_layer.objects.active = selected[0]
    return selected


def export_skirt(filepath, settings):
    path = Path(bpy.path.abspath(str(filepath)))
    fmt = settings.export_format
    suffix = {'GLB': '.glb', 'FBX': '.fbx', 'OBJ': '.obj'}[fmt]
    path = path.with_suffix(suffix)
    path.parent.mkdir(parents=True, exist_ok=True)
    selected = _select_for_export(settings)
    if not selected:
        raise RuntimeError('書き出す生成物がありません')
    if fmt == 'GLB':
        bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', use_selection=True, export_apply=settings.apply_modifiers)
    elif fmt == 'FBX':
        bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, apply_unit_scale=True, use_mesh_modifiers=settings.apply_modifiers)
    else:
        if hasattr(bpy.ops.wm, 'obj_export'):
            bpy.ops.wm.obj_export(filepath=str(path), export_selected_objects=True, apply_modifiers=settings.apply_modifiers)
        else:
            bpy.ops.export_scene.obj(filepath=str(path), use_selection=True, use_mesh_modifiers=settings.apply_modifiers)
    return path
