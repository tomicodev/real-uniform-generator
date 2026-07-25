from __future__ import annotations

from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, StringProperty
from bpy.types import PropertyGroup


class RUG_Settings(PropertyGroup):
    waist_circumference: FloatProperty(name="ウエスト仕上がり", default=0.68, min=0.50, max=1.20, unit='LENGTH')
    hip_circumference: FloatProperty(name="ヒップ仕上がり", default=0.92, min=0.70, max=1.40, unit='LENGTH')
    skirt_length: FloatProperty(name="スカート丈", default=0.48, min=0.30, max=0.90, unit='LENGTH')
    hip_line: FloatProperty(name="ヒップライン", default=0.18, min=0.10, max=0.30, unit='LENGTH')
    body_depth_ratio: FloatProperty(name="体型奥行比", default=0.78, min=0.60, max=1.0, subtype='FACTOR')
    hem_ease: FloatProperty(name="裾回りゆとり", default=0.04, min=0.0, max=0.30, unit='LENGTH')

    pleat_count: IntProperty(name="ナイフプリーツ数", default=20, min=8, max=32)
    pleat_depth: FloatProperty(name="奥プリーツ深さ", default=0.028, min=0.012, max=0.060, unit='LENGTH')
    pleat_stitch_length: FloatProperty(name="縫い止め長さ", default=0.105, min=0.04, max=0.22, unit='LENGTH')
    pleat_release_length: FloatProperty(name="プリーツ解放長さ", default=0.055, min=0.02, max=0.12, unit='LENGTH')
    vertical_segments: IntProperty(name="縦分割", default=64, min=32, max=160)
    wrinkle_strength: FloatProperty(name="自然な揺らぎ", default=0.0015, min=0.0, max=0.008, unit='LENGTH')
    back_drop: FloatProperty(name="後ろ裾の落ち", default=0.006, min=0.0, max=0.025, unit='LENGTH')

    fabric_thickness: FloatProperty(name="表地厚", default=0.00125, min=0.0005, max=0.004, unit='LENGTH')
    hem_turnup: FloatProperty(name="裾折り返し", default=0.04, min=0.02, max=0.08, unit='LENGTH')
    waistband_height: FloatProperty(name="ベルト幅", default=0.035, min=0.025, max=0.060, unit='LENGTH')
    waistband_overlap: FloatProperty(name="ベルト持出し", default=0.025, min=0.0, max=0.06, unit='LENGTH')

    create_lining: BoolProperty(name="裏地付き", default=True)
    lining_length: FloatProperty(name="裏地丈", default=0.37, min=0.20, max=0.55, unit='LENGTH')
    zipper_length: FloatProperty(name="コンシールファスナー長", default=0.18, min=0.12, max=0.28, unit='LENGTH')
    zipper_position: EnumProperty(name="ファスナー位置", items=(('LEFT', '左脇', ''), ('BACK', '後中心', ''), ('RIGHT', '右脇', '')), default='LEFT')
    create_stitches: BoolProperty(name="縫製線を作成", default=True)
    create_simulation: BoolProperty(name="布シミュレーション設定", default=False)

    use_external_pbr: BoolProperty(name="外部PBRを使用", default=False)
    texture_directory: StringProperty(name="PBRフォルダ", subtype='DIR_PATH', default='')
    normal_format: EnumProperty(name="法線形式", items=(('AUTO', '自動', ''), ('OPENGL', 'OpenGL', ''), ('DIRECTX', 'DirectX', '')), default='AUTO')
    pack_external_textures: BoolProperty(name="画像をBLENDへパック", default=True)
    texture_tile_cm: FloatProperty(name="テクスチャ実幅 (cm)", default=10.0, min=0.5, max=100.0)
    weave_size_cm: FloatProperty(name="織り目サイズ (cm)", default=0.12, min=0.02, max=1.0)
    normal_strength: FloatProperty(name="Normal強度", default=0.28, min=0.0, max=1.0, subtype='FACTOR')
    height_strength: FloatProperty(name="Height強度", default=0.06, min=0.0, max=0.35, subtype='FACTOR')
    ao_strength: FloatProperty(name="AO強度", default=0.22, min=0.0, max=1.0, subtype='FACTOR')

    render_engine: EnumProperty(name="レンダー", items=(('BLENDER_EEVEE', 'Eevee', ''), ('CYCLES', 'Cycles', '')), default='BLENDER_EEVEE')
    export_format: EnumProperty(name="形式", items=(('GLB', 'GLB', ''), ('FBX', 'FBX', ''), ('OBJ', 'OBJ', '')), default='GLB')
    apply_modifiers: BoolProperty(name="モディファイアを適用", default=True)
    export_lining: BoolProperty(name="裏地も書き出す", default=True)
    export_hardware: BoolProperty(name="ファスナーも書き出す", default=True)
    output_directory: StringProperty(name="出力フォルダ", subtype='DIR_PATH', default='//test_outputs/')


CLASSES = (RUG_Settings,)
