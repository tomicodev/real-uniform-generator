import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty
from bpy.types import PropertyGroup


class RUG_Settings(PropertyGroup):
    pleat_count: IntProperty(
        name="プリーツ数",
        description="一周のナイフプリーツ数",
        default=20,
        min=8,
        max=32,
    )
    skirt_length: FloatProperty(
        name="スカート丈",
        default=0.48,
        min=0.30,
        max=0.90,
        unit='LENGTH',
    )
    waist_width: FloatProperty(
        name="ウエスト半幅",
        default=0.185,
        min=0.12,
        max=0.30,
        unit='LENGTH',
    )
    waist_depth: FloatProperty(
        name="ウエスト奥行",
        default=0.140,
        min=0.09,
        max=0.24,
        unit='LENGTH',
    )
    hem_width: FloatProperty(
        name="裾半幅",
        default=0.315,
        min=0.20,
        max=0.50,
        unit='LENGTH',
    )
    hem_depth: FloatProperty(
        name="裾奥行",
        default=0.250,
        min=0.15,
        max=0.40,
        unit='LENGTH',
    )
    pleat_depth: FloatProperty(
        name="プリーツ深さ",
        description="裾側で開く折りの深さ",
        default=0.105,
        min=0.025,
        max=0.20,
    )
    pleat_stitch_length: FloatProperty(
        name="プリーツ縫い止まり",
        description="ウエストからプリーツを縫い止める長さ",
        default=0.105,
        min=0.02,
        max=0.25,
        unit='LENGTH',
    )
    fabric_thickness: FloatProperty(
        name="生地厚",
        default=0.0022,
        min=0.0008,
        max=0.006,
        unit='LENGTH',
    )
    waistband_height: FloatProperty(
        name="ベルト幅",
        default=0.036,
        min=0.02,
        max=0.08,
        unit='LENGTH',
    )
    waistband_overlap: FloatProperty(
        name="ベルト重なり",
        default=0.030,
        min=0.0,
        max=0.08,
        unit='LENGTH',
    )
    back_drop: FloatProperty(
        name="後ろ裾の落ち",
        default=0.010,
        min=0.0,
        max=0.04,
        unit='LENGTH',
    )
    wrinkle_strength: FloatProperty(
        name="自然なしわ",
        default=0.0035,
        min=0.0,
        max=0.015,
        unit='LENGTH',
    )
    vertical_segments: IntProperty(
        name="縦分割",
        default=72,
        min=24,
        max=160,
    )
    create_lining: BoolProperty(
        name="裏地を作成",
        default=True,
    )
    lining_length_ratio: FloatProperty(
        name="裏地の丈",
        default=0.66,
        min=0.40,
        max=0.92,
        subtype='FACTOR',
    )
    create_hardware: BoolProperty(
        name="ファスナー・ホック",
        default=True,
    )
    create_stitches: BoolProperty(
        name="縫製ステッチ",
        default=True,
    )
    fabric: EnumProperty(
        name="生地プリセット",
        items=(
            ('WINTER_NAVY', "冬服・濃紺", "厚手のウール混生地"),
            ('SUMMER_NAVY', "夏服・濃紺", "薄手のポリエステル混生地"),
            ('CHARCOAL', "チャコール", "濃灰色のウール混生地"),
            ('BLACK', "ブラック", "黒色の制服生地"),
        ),
        default='WINTER_NAVY',
    )
    weave_scale: FloatProperty(
        name="織り目密度",
        default=380.0,
        min=80.0,
        max=900.0,
    )
    weave_strength: FloatProperty(
        name="織り目の凹凸",
        default=0.12,
        min=0.0,
        max=0.35,
        subtype='FACTOR',
    )
    texture_resolution: EnumProperty(
        name="PBRテクスチャ解像度",
        description="GLBにも埋め込みやすい生地テクスチャの解像度",
        items=(
            ('512', "512 px", "軽量・高速"),
            ('1024', "1024 px", "標準"),
            ('2048', "2048 px", "高精細・生成に時間がかかります"),
        ),
        default='1024',
    )
    export_format: EnumProperty(
        name="形式",
        items=(
            ('GLB', "GLB", "マテリアルを含む単一ファイル"),
            ('FBX', "FBX", "DCC・ゲームエンジン向け"),
            ('OBJ', "OBJ", "汎用メッシュ形式"),
        ),
        default='GLB',
    )
    apply_modifiers: BoolProperty(
        name="モディファイアを適用",
        default=True,
    )
    export_lining: BoolProperty(
        name="裏地も書き出す",
        default=True,
    )
    export_hardware: BoolProperty(
        name="金具も書き出す",
        default=True,
    )


CLASSES = (RUG_Settings,)
