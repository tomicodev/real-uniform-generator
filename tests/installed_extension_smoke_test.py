"""Smoke test after installing and enabling the packaged Blender extension."""

from pathlib import Path
import bpy


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    root = Path.cwd()
    output_dir = root / 'runtime-output' / 'installed'
    output_dir.mkdir(parents=True, exist_ok=True)
    assert_true(hasattr(bpy.types.Scene, 'rug_settings'), 'Extension is not registered')
    assert_true(hasattr(bpy.ops.rug, 'generate_skirt'), 'Generate operator missing')

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
    required = {'RUG_SkirtOuter', 'RUG_WaistbandShell', 'RUG_Lining', 'RUG_ZipperTapeA', 'RUG_ZipperTapeB'}
    assert_true(not (required - names), f'Missing installed objects: {sorted(required - names)}')
    skirt = bpy.data.objects['RUG_SkirtOuter']
    assert_true(len(skirt.data.vertices) > 6000 and bool(skirt.data.uv_layers), 'Installed skirt geometry invalid')

    result = bpy.ops.rug.prepare_preview()
    assert_true('FINISHED' in result, 'Preview studio failed')
    preview_path = output_dir / 'installed_preview.png'
    result = bpy.ops.rug.render_front('EXEC_DEFAULT', filepath=str(preview_path))
    assert_true('FINISHED' in result and preview_path.exists() and preview_path.stat().st_size > 4096, 'Installed preview failed')

    settings.export_format = 'GLB'
    glb_path = output_dir / 'installed_test.glb'
    result = bpy.ops.rug.export_skirt('EXEC_DEFAULT', filepath=str(glb_path))
    assert_true('FINISHED' in result and glb_path.exists() and glb_path.stat().st_size > 1024, 'Installed GLB failed')

    blend_path = output_dir / 'installed_test.blend'
    result = bpy.ops.rug.save_blend_copy('EXEC_DEFAULT', filepath=str(blend_path))
    assert_true('FINISHED' in result and blend_path.exists(), 'Installed BLEND failed')
    print('RUG_INSTALLED_EXTENSION_TEST_OK')


if __name__ == '__main__':
    main()
