from pathlib import Path
import traceback

import bpy
from bpy.props import StringProperty
from bpy.types import Operator

from .exporter import export_skirt
from .geometry import clear_generated, generate_uniform_skirt, generated_objects
from .materials import build_materials
from .preview import clear_preview, create_preview_scene


class RUG_OT_generate(Operator):
    bl_idname = 'rug.generate_skirt'
    bl_label = '制服スカートを生成'
    bl_description = '現在の設定から制服プリーツスカート一式を生成します'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.rug_settings
        try:
            materials = build_materials(settings)
            created = generate_uniform_skirt(settings, materials)
            bpy.ops.object.select_all(action='DESELECT')
            root = created['root']
            root.select_set(True)
            context.view_layer.objects.active = root
            self.report(
                {'INFO'},
                f'制服スカートを生成しました（{settings.pleat_count}プリーツ）',
            )
            return {'FINISHED'}
        except Exception as exc:
            traceback.print_exc()
            self.report({'ERROR'}, f'生成に失敗しました: {exc}')
            return {'CANCELLED'}


class RUG_OT_delete(Operator):
    bl_idname = 'rug.delete_skirt'
    bl_label = '生成物を削除'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(generated_objects(include_root=True))

    def execute(self, context):
        clear_generated()
        self.report({'INFO'}, '生成した制服スカートを削除しました')
        return {'FINISHED'}


class RUG_OT_prepare_preview(Operator):
    bl_idname = 'rug.prepare_preview'
    bl_label = '確認用スタジオを作成'
    bl_description = '照明、床、カメラを自動配置して質感を確認しやすくします'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(generated_objects())

    def execute(self, context):
        try:
            create_preview_scene(context.scene.rug_settings)
            self.report({'INFO'}, '確認用スタジオを作成しました')
            return {'FINISHED'}
        except Exception as exc:
            traceback.print_exc()
            self.report({'ERROR'}, f'プレビュー作成に失敗しました: {exc}')
            return {'CANCELLED'}


class RUG_OT_clear_preview(Operator):
    bl_idname = 'rug.clear_preview'
    bl_label = '確認用スタジオを削除'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        clear_preview()
        self.report({'INFO'}, '確認用スタジオを削除しました')
        return {'FINISHED'}


class RUG_OT_render_preview(Operator):
    bl_idname = 'rug.render_preview'
    bl_label = 'プレビュー画像を書き出す'
    filepath: StringProperty(subtype='FILE_PATH')

    @classmethod
    def poll(cls, context):
        return bool(generated_objects())

    def invoke(self, context, event):
        self.filepath = str(Path.home() / 'real_uniform_skirt_preview.png')
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        try:
            create_preview_scene(context.scene.rug_settings)
            path = Path(self.filepath).expanduser().with_suffix('.png')
            path.parent.mkdir(parents=True, exist_ok=True)
            context.scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            self.report({'INFO'}, f'プレビューを書き出しました: {path}')
            return {'FINISHED'}
        except Exception as exc:
            traceback.print_exc()
            self.report({'ERROR'}, f'レンダリングに失敗しました: {exc}')
            return {'CANCELLED'}


class RUG_OT_export(Operator):
    bl_idname = 'rug.export_skirt'
    bl_label = '生成物を書き出す'
    filepath: StringProperty(subtype='FILE_PATH')

    @classmethod
    def poll(cls, context):
        return bool(generated_objects())

    def invoke(self, context, event):
        extension = context.scene.rug_settings.export_format.lower()
        self.filepath = str(Path.home() / f'real_uniform_skirt.{extension}')
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        try:
            path = export_skirt(self.filepath, context.scene.rug_settings)
            self.report({'INFO'}, f'書き出しました: {path}')
            return {'FINISHED'}
        except Exception as exc:
            traceback.print_exc()
            self.report({'ERROR'}, f'書き出しに失敗しました: {exc}')
            return {'CANCELLED'}


class RUG_OT_save_blend_copy(Operator):
    bl_idname = 'rug.save_blend_copy'
    bl_label = 'BLENDコピーを保存'
    filepath: StringProperty(subtype='FILE_PATH')

    @classmethod
    def poll(cls, context):
        return bool(generated_objects())

    def invoke(self, context, event):
        self.filepath = str(Path.home() / 'real_uniform_skirt.blend')
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        try:
            path = Path(self.filepath).expanduser().with_suffix('.blend')
            path.parent.mkdir(parents=True, exist_ok=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(path), copy=True)
            self.report({'INFO'}, f'BLENDコピーを保存しました: {path}')
            return {'FINISHED'}
        except Exception as exc:
            traceback.print_exc()
            self.report({'ERROR'}, f'BLEND保存に失敗しました: {exc}')
            return {'CANCELLED'}


CLASSES = (
    RUG_OT_generate,
    RUG_OT_delete,
    RUG_OT_prepare_preview,
    RUG_OT_clear_preview,
    RUG_OT_render_preview,
    RUG_OT_export,
    RUG_OT_save_blend_copy,
)
