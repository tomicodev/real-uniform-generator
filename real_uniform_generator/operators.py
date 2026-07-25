from __future__ import annotations

from pathlib import Path
import traceback
import bpy
from bpy.props import StringProperty
from bpy.types import Operator

from .exporter import export_skirt
from .geometry import clear_generated, generate_uniform_skirt
from .material_io import find_pbr_files
from .materials import build_materials
from .preview import clear_preview, create_preview_scene, render_view


class RUG_OT_generate(Operator):
    bl_idname = 'rug.generate_skirt'
    bl_label = '制服スカートを生成'
    bl_description = '設定値から縫製構造を持つ制服プリーツスカートを再生成します'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            settings = context.scene.rug_settings
            created = generate_uniform_skirt(settings, build_materials(settings))
            bpy.ops.object.select_all(action='DESELECT')
            created['root'].select_set(True)
            context.view_layer.objects.active = created['root']
            self.report({'INFO'}, f'{settings.pleat_count}本の制服スカートを生成しました')
            return {'FINISHED'}
        except Exception as exc:
            traceback.print_exc()
            self.report({'ERROR'}, f'生成に失敗しました: {exc}')
            return {'CANCELLED'}


class RUG_OT_delete(Operator):
    bl_idname = 'rug.delete_skirt'
    bl_label = '生成物を削除'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        clear_generated()
        return {'FINISHED'}


class RUG_OT_scan_pbr(Operator):
    bl_idname = 'rug.scan_pbr'
    bl_label = 'PBR画像を確認'

    def execute(self, context):
        try:
            files = find_pbr_files(context.scene.rug_settings.texture_directory)
            self.report({'INFO'}, ' / '.join(f'{key}: {path.name}' for key, path in files.items()))
            return {'FINISHED'}
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}


class RUG_OT_prepare_preview(Operator):
    bl_idname = 'rug.prepare_preview'
    bl_label = '確認用スタジオを作成'

    def execute(self, context):
        create_preview_scene(context.scene.rug_settings)
        return {'FINISHED'}


class RUG_OT_clear_preview(Operator):
    bl_idname = 'rug.clear_preview'
    bl_label = '確認用スタジオを削除'

    def execute(self, context):
        clear_preview()
        return {'FINISHED'}


class RUG_OT_render_front(Operator):
    bl_idname = 'rug.render_front'
    bl_label = '正面プレビューを書き出す'
    filepath: StringProperty(subtype='FILE_PATH')

    def invoke(self, context, event):
        self.filepath = str(Path(bpy.path.abspath(context.scene.rug_settings.output_directory)) / 'preview_front.png')
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        render_view('FRONT', self.filepath, context.scene.rug_settings)
        return {'FINISHED'}


class RUG_OT_export(Operator):
    bl_idname = 'rug.export_skirt'
    bl_label = '生成物を書き出す'
    filepath: StringProperty(subtype='FILE_PATH')

    def invoke(self, context, event):
        ext = context.scene.rug_settings.export_format.lower()
        self.filepath = str(Path(bpy.path.abspath(context.scene.rug_settings.output_directory)) / f'generated_skirt.{ext}')
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        try:
            export_skirt(self.filepath, context.scene.rug_settings)
            return {'FINISHED'}
        except Exception as exc:
            traceback.print_exc()
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}


class RUG_OT_save_blend_copy(Operator):
    bl_idname = 'rug.save_blend_copy'
    bl_label = 'BLENDコピーを保存'
    filepath: StringProperty(subtype='FILE_PATH')

    def invoke(self, context, event):
        self.filepath = str(Path(bpy.path.abspath(context.scene.rug_settings.output_directory)) / 'generated_skirt.blend')
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        path = Path(bpy.path.abspath(self.filepath)).with_suffix('.blend')
        path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(path), copy=True)
        return {'FINISHED'}


CLASSES = (
    RUG_OT_generate,
    RUG_OT_delete,
    RUG_OT_scan_pbr,
    RUG_OT_prepare_preview,
    RUG_OT_clear_preview,
    RUG_OT_render_front,
    RUG_OT_export,
    RUG_OT_save_blend_copy,
)
