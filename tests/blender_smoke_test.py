"""Source-tree Blender 5.2 smoke test."""

from pathlib import Path
import sys
import bpy

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import real_uniform_generator
from real_uniform_generator.preview import create_preview_scene, render_view


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    output_dir = REPO_ROOT / 'runtime-output' / 'source'
    output_dir.mkdir(parents=True, exist_ok=True)
    real_uniform_generator.register()
    try:
        settings = bpy.context.scene.rug_settings
        settings.pleat_count = 20
        settings.vertical_segments = 48
        settings.use_external_pbr = False
        settings.output_directory = str(output_dir)

        result = bpy.ops.rug.generate_skirt()
        assert_true('FINISHED' in result, f'Generate failed: {result}')
        collection = bpy.data.collections.get('RUG_Generated')
        assert_true(collection is not None, 'Generated collection missing')
        names = {obj.name for obj in collection.objects}
        required = {
            'RUG_SkirtOuter', 'RUG_WaistbandShell', 'RUG_WaistbandInterfacing',
            'RUG_Lining', 'RUG_SeamAllowanceFront', 'RUG_SeamAllowanceBack',
            'RUG_ZipperTapeA', 'RUG_ZipperTapeB', 'RUG_ZipperCoilA',
            'RUG_ZipperCoilB', 'RUG_ConcealedSlider', 'RUG_InternalPullTab',
        }
        assert_true(not (required - names), f'Missing objects: {sorted(required - names)}')
        assert_true(not any('hem' in name.lower() for name in names), 'Hem must remain integrated into the outer cloth')

        skirt = bpy.data.objects['RUG_SkirtOuter']
        assert_true(len(skirt.data.vertices) > 6000, 'Outer skirt is unexpectedly simple')
        assert_true(bool(skirt.data.uv_layers), 'Outer skirt UV missing')
        assert_true(skirt.get('rug_construction') == 'continuous_cloth_with_integrated_hem', 'Construction metadata missing')
        assert_true(all(not modifier.use_even_offset for obj in collection.objects for modifier in obj.modifiers if modifier.type == 'SOLIDIFY'), 'Unsafe even-offset solidify found')
        assert_true(abs(next(m.thickness for m in skirt.modifiers if m.type == 'SOLIDIFY') - 0.00125) < 1e-6, 'Fabric thickness mismatch')

        create_preview_scene(settings)
        preview_path = render_view('FRONT', output_dir / 'preview_front.png', settings)
        assert_true(preview_path.exists() and preview_path.stat().st_size > 4096, 'Preview missing')

        settings.export_format = 'GLB'
        glb_path = output_dir / 'smoke_test.glb'
        result = bpy.ops.rug.export_skirt('EXEC_DEFAULT', filepath=str(glb_path))
        assert_true('FINISHED' in result and glb_path.exists() and glb_path.stat().st_size > 1024, 'GLB export failed')

        blend_path = output_dir / 'smoke_test.blend'
        result = bpy.ops.rug.save_blend_copy('EXEC_DEFAULT', filepath=str(blend_path))
        assert_true('FINISHED' in result and blend_path.exists(), 'BLEND copy failed')
        print('RUG_SMOKE_TEST_OK')
    finally:
        real_uniform_generator.unregister()


if __name__ == '__main__':
    main()
