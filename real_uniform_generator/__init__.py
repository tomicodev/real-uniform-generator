bl_info = {
    "name": "Real Uniform Generator",
    "author": "tomicodev / OpenAI",
    "version": (0, 1, 0),
    "blender": (4, 3, 0),
    "location": "View3D > Sidebar > Uniform",
    "description": "Generate and export a configurable Japanese school pleated skirt",
    "category": "Add Mesh",
}

import bpy
import math
from pathlib import Path
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup

ADDON_COLLECTION = "RUG_UniformSkirt"


def _smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


def _collection():
    col = bpy.data.collections.get(ADDON_COLLECTION)
    if col is None:
        col = bpy.data.collections.new(ADDON_COLLECTION)
        bpy.context.scene.collection.children.link(col)
    return col


def _clear_generated():
    col = bpy.data.collections.get(ADDON_COLLECTION)
    if not col:
        return
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def _link_object(obj):
    col = _collection()
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)


def _make_fabric_material(name, color, roughness, weave_strength):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tex = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    wave_a = nt.nodes.new("ShaderNodeTexWave")
    wave_b = nt.nodes.new("ShaderNodeTexWave")
    mix = nt.nodes.new("ShaderNodeMixRGB")
    bump = nt.nodes.new("ShaderNodeBump")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["IOR"].default_value = 1.46
    if "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = 0.22
        bsdf.inputs["Sheen Roughness"].default_value = 0.62
    wave_a.wave_type = 'BANDS'
    wave_a.bands_direction = 'X'
    wave_a.inputs["Scale"].default_value = 320.0
    wave_a.inputs["Distortion"].default_value = 1.0
    wave_a.inputs["Detail"].default_value = 2.0
    wave_b.wave_type = 'BANDS'
    wave_b.bands_direction = 'Y'
    wave_b.inputs["Scale"].default_value = 360.0
    wave_b.inputs["Distortion"].default_value = 0.8
    wave_b.inputs["Detail"].default_value = 2.0
    mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = 1.0
    bump.inputs["Strength"].default_value = weave_strength
    bump.inputs["Distance"].default_value = 0.0025
    nt.links.new(tex.outputs["Generated"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], wave_a.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], wave_b.inputs["Vector"])
    nt.links.new(wave_a.outputs["Color"], mix.inputs[1])
    nt.links.new(wave_b.outputs["Color"], mix.inputs[2])
    nt.links.new(mix.outputs["Color"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def _make_simple_material(name, color, roughness=0.75, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.roughness = roughness
    mat.metallic = metallic
    return mat


def _shade(obj):
    if obj.type == 'MESH':
        for poly in obj.data.polygons:
            poly.use_smooth = True


def _add_bevel(obj, width, segments=2):
    mod = obj.modifiers.new("Micro Bevel", 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'


def _create_skirt(settings):
    facets = 8
    around = settings.pleat_count * facets
    rows = settings.vertical_segments
    row_size = around + 1
    verts, faces = [], []
    fold_profile = (0.0, 0.45, 0.90, 1.0, 0.55, 0.0, -0.30, -0.14)

    def point(i, v):
        theta = (i % around) / around * math.tau
        fold = fold_profile[i % facets]
        eased = _smoothstep(v)
        rx = settings.waist_width + (settings.hem_width - settings.waist_width) * eased
        ry = settings.waist_depth + (settings.hem_depth - settings.waist_depth) * eased
        amp = (0.004 + settings.pleat_depth * (v ** 1.30)) * fold
        scale = 1.0 + amp
        back = settings.back_drop * max(0.0, -math.sin(theta)) * (v ** 1.75)
        irregular = 0.006 * math.sin(theta * 3.0 + 0.5) * (v ** 1.25)
        return (
            math.cos(theta) * rx * scale,
            math.sin(theta) * ry * scale,
            -settings.skirt_length * v - back - irregular,
        )

    for j in range(rows + 1):
        v = j / rows
        for i in range(around + 1):
            verts.append(point(i, v))
    for j in range(rows):
        for i in range(around):
            a = j * row_size + i
            b = a + 1
            c = a + row_size + 1
            d = a + row_size
            faces.append((a, d, c, b))

    mesh = bpy.data.meshes.new("RUG_PleatedSkirt_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("RUG_PleatedSkirt", mesh)
    _link_object(obj)
    solid = obj.modifiers.new("Fabric Thickness", 'SOLIDIFY')
    solid.thickness = settings.fabric_thickness
    solid.offset = -0.6
    solid.use_even_offset = True
    solid.use_quality_normals = True
    _add_bevel(obj, min(settings.fabric_thickness * 0.32, 0.006), 2)
    _shade(obj)
    return obj


def _create_waistband(settings):
    bpy.ops.mesh.primitive_cylinder_add(vertices=192, radius=1.0, depth=settings.waistband_height)
    obj = bpy.context.object
    obj.name = "RUG_Waistband"
    obj.scale = (settings.waist_width * 1.018, settings.waist_depth * 1.018, 1.0)
    obj.location.z = settings.waistband_height * 0.5 + 0.006
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    _link_object(obj)
    _add_bevel(obj, 0.010, 3)
    _shade(obj)
    return obj


def _create_curve_ring(name, rx, ry, z, bevel):
    curve = bpy.data.curves.new(name + "_Curve", type='CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 2
    curve.bevel_depth = bevel
    curve.bevel_resolution = 2
    spline = curve.splines.new('POLY')
    count = 192
    spline.points.add(count)
    for i in range(count + 1):
        angle = i / count * math.tau
        spline.points[i].co = (math.cos(angle) * rx, math.sin(angle) * ry, z, 1.0)
    spline.use_cyclic_u = True
    obj = bpy.data.objects.new(name, curve)
    _link_object(obj)
    return obj


def _create_zipper(settings):
    bpy.ops.mesh.primitive_cube_add()
    track = bpy.context.object
    track.name = "RUG_SideZipper"
    track.location = (settings.waist_width * 0.99, 0.01, -0.22)
    track.scale = (0.009, 0.015, 0.30)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    _link_object(track)
    _add_bevel(track, 0.002, 2)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.028, minor_radius=0.005, major_segments=32, minor_segments=8,
        location=(settings.waist_width * 1.01, 0.02, 0.035), rotation=(math.radians(90), 0, 0),
    )
    pull = bpy.context.object
    pull.name = "RUG_ZipperPull"
    _link_object(pull)
    return track, pull


def _apply_export_modifiers(objects):
    for obj in objects:
        if obj.type != 'MESH':
            continue
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        for mod in list(obj.modifiers):
            try:
                bpy.ops.object.modifier_apply(modifier=mod.name)
            except RuntimeError:
                pass
        obj.select_set(False)


class RUG_Settings(PropertyGroup):
    pleat_count: IntProperty(name="プリーツ数", default=18, min=8, max=32)
    skirt_length: FloatProperty(name="丈", default=0.48, min=0.30, max=0.90, unit='LENGTH')
    waist_width: FloatProperty(name="ウエスト半幅", default=0.185, min=0.12, max=0.30, unit='LENGTH')
    waist_depth: FloatProperty(name="ウエスト奥行", default=0.140, min=0.09, max=0.24, unit='LENGTH')
    hem_width: FloatProperty(name="裾半幅", default=0.310, min=0.20, max=0.50, unit='LENGTH')
    hem_depth: FloatProperty(name="裾奥行", default=0.245, min=0.15, max=0.40, unit='LENGTH')
    pleat_depth: FloatProperty(name="プリーツ深さ", default=0.105, min=0.03, max=0.20)
    fabric_thickness: FloatProperty(name="生地厚", default=0.0022, min=0.0008, max=0.006, unit='LENGTH')
    waistband_height: FloatProperty(name="ベルト幅", default=0.035, min=0.02, max=0.08, unit='LENGTH')
    back_drop: FloatProperty(name="後ろ裾の落ち", default=0.010, min=0.0, max=0.04, unit='LENGTH')
    vertical_segments: IntProperty(name="縦分割", default=48, min=16, max=128)
    fabric: EnumProperty(name="生地", items=(
        ('WINTER_NAVY', "冬服・濃紺", "厚手ウール混"),
        ('SUMMER_NAVY', "夏服・濃紺", "薄手ポリエステル混"),
        ('CHARCOAL', "チャコール", "濃灰色"),
    ), default='WINTER_NAVY')
    export_format: EnumProperty(name="形式", items=(('GLB', "GLB", ""), ('FBX', "FBX", ""), ('OBJ', "OBJ", "")), default='GLB')
    apply_modifiers: BoolProperty(name="書き出し時にモディファイア適用", default=True)


class RUG_OT_generate(Operator):
    bl_idname = "rug.generate_skirt"
    bl_label = "制服スカートを生成"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.rug_settings
        _clear_generated()
        skirt = _create_skirt(settings)
        band = _create_waistband(settings)
        top = _create_curve_ring("RUG_WaistTopStitch", settings.waist_width * 1.022, settings.waist_depth * 1.022, settings.waistband_height + 0.004, 0.0008)
        bottom = _create_curve_ring("RUG_WaistBottomStitch", settings.waist_width * 1.022, settings.waist_depth * 1.022, 0.010, 0.0007)
        hem = _create_curve_ring("RUG_HemStitch", settings.hem_width * 0.997, settings.hem_depth * 0.997, -settings.skirt_length + 0.018, 0.0007)
        zipper, pull = _create_zipper(settings)
        if settings.fabric == 'WINTER_NAVY':
            color, roughness, weave = (0.012, 0.022, 0.050), 0.80, 0.18
        elif settings.fabric == 'SUMMER_NAVY':
            color, roughness, weave = (0.018, 0.032, 0.072), 0.70, 0.10
        else:
            color, roughness, weave = (0.035, 0.040, 0.050), 0.78, 0.14
        fabric = _make_fabric_material("RUG_UniformFabric", color, roughness, weave)
        thread = _make_simple_material("RUG_Thread", (0.075, 0.085, 0.11), 0.92)
        metal = _make_simple_material("RUG_ZipperMetal", (0.24, 0.27, 0.30), 0.30, 0.82)
        skirt.data.materials.append(fabric)
        band.data.materials.append(fabric)
        for obj in (top, bottom, hem):
            obj.data.materials.append(thread)
        zipper.data.materials.append(thread)
        pull.data.materials.append(metal)
        bpy.context.view_layer.objects.active = skirt
        skirt.select_set(True)
        self.report({'INFO'}, "制服プリーツスカートを生成しました")
        return {'FINISHED'}


class RUG_OT_export(Operator):
    bl_idname = "rug.export_skirt"
    bl_label = "生成物を書き出す"
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def invoke(self, context, event):
        ext = context.scene.rug_settings.export_format.lower()
        self.filepath = str(Path.home() / f"real_uniform_skirt.{ext}")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        settings = context.scene.rug_settings
        col = bpy.data.collections.get(ADDON_COLLECTION)
        objects = list(col.objects) if col else []
        if not objects:
            self.report({'ERROR'}, "先にスカートを生成してください")
            return {'CANCELLED'}
        bpy.ops.object.select_all(action='DESELECT')
        for obj in list(objects):
            obj.select_set(True)
            if obj.type == 'CURVE':
                context.view_layer.objects.active = obj
                bpy.ops.object.convert(target='MESH')
        mesh_objects = [obj for obj in objects if obj.type == 'MESH']
        if settings.apply_modifiers:
            _apply_export_modifiers(mesh_objects)
        path = Path(self.filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            if settings.export_format == 'GLB':
                path = path.with_suffix('.glb')
                bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', use_selection=True, export_apply=True)
            elif settings.export_format == 'FBX':
                path = path.with_suffix('.fbx')
                bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, apply_unit_scale=True, add_leaf_bones=False)
            else:
                path = path.with_suffix('.obj')
                bpy.ops.wm.obj_export(filepath=str(path), export_selected_objects=True, export_materials=True, apply_modifiers=True)
        except Exception as exc:
            self.report({'ERROR'}, f"書き出しに失敗しました: {exc}")
            return {'CANCELLED'}
        self.report({'INFO'}, f"書き出しました: {path}")
        return {'FINISHED'}


class RUG_PT_panel(Panel):
    bl_label = "Real Uniform Generator"
    bl_idname = "RUG_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Uniform'

    def draw(self, context):
        settings = context.scene.rug_settings
        layout = self.layout
        box = layout.box()
        box.label(text="形状", icon='MESH_DATA')
        box.prop(settings, "pleat_count")
        box.prop(settings, "skirt_length")
        row = box.row(align=True)
        row.prop(settings, "waist_width")
        row.prop(settings, "waist_depth")
        row = box.row(align=True)
        row.prop(settings, "hem_width")
        row.prop(settings, "hem_depth")
        box.prop(settings, "pleat_depth")
        box.prop(settings, "fabric_thickness")
        box.prop(settings, "waistband_height")
        box.prop(settings, "back_drop")
        box = layout.box()
        box.label(text="質感", icon='MATERIAL')
        box.prop(settings, "fabric")
        box.prop(settings, "vertical_segments")
        layout.operator("rug.generate_skirt", icon='OUTLINER_OB_MESH')
        box = layout.box()
        box.label(text="書き出し", icon='EXPORT')
        box.prop(settings, "export_format")
        box.prop(settings, "apply_modifiers")
        box.operator("rug.export_skirt", icon='FILE_TICK')


classes = (RUG_Settings, RUG_OT_generate, RUG_OT_export, RUG_PT_panel)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.rug_settings = PointerProperty(type=RUG_Settings)


def unregister():
    del bpy.types.Scene.rug_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
