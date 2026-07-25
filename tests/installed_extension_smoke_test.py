"""Executed after installing and enabling the packaged extension."""

from pathlib import Path
import os
import tempfile

import bpy

GENERATED_COLLECTION = 'RUG_UniformSkirt'
FABRIC_MATERIAL = 'RUG_UniformFabric'


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def output_directory(prefix):
    configured = os.environ.get('RUG_TEST_OUTPUT_DIR')
    if configured:
        path = Path(configured).expanduser().resolve() / prefix
        path.mkdir(parents=True, exist_ok=True)
        return path
    return Path(tempfile.mkdtemp(prefix=f'{prefix}_'))


def main():
    assert_true(hasattr(bpy.types.Scene, 'rug_settings'), 'Extension is not registered')
    assert_true(hasattr(bpy.ops.rug, 'generate_skirt'), 'Generate operator is missing')

    settings = bpy.context.scene.rug_settings
    settings.pleat_count = 18
    settings.vertical_segments = 48
    settings.texture_resolution = '512'
    settings.show_internal_construction = False

    result = bpy.ops.rug.generate_skirt()
    assert_true('FINISHED' in result, f'Generate failed: {result}')

    collection = bpy.data.collections.get(GENERATED_COLLECTION)
    assert_true(collection is not None, 'Generated collection is missing')
    names = {obj.name for obj in collection.objects}
    required = {
        'RUG_SkirtOuter', 'RUG_Waistband', 'RUG_HemFacingInner', 'RUG_Lining',
        'RUG_ZipperTape_L', 'RUG_ZipperTape_R', 'RUG_ZipperCoil_L', 'RUG_ZipperCoil_R',
    }
    assert_true(not (required - names), f'Missing installed objects: {sorted(required - names)}')

    # Internal zipper construction is generated but hidden in normal exterior view.
    for name in ('RUG_ZipperTape_L', 'RUG_ZipperTape_R', 'RUG_ZipperCoil_L', 'RUG_ZipperCoil_R'):
        obj = bpy.data.objects[name]
        assert_true(obj.hide_render, f'{name} should be hidden from exterior renders by default')

    skirt = bpy.data.objects['RUG_SkirtOuter']
    assert_true(len(skirt.data.vertices) > 3000, 'Installed skirt is unexpectedly simple')
    assert_true(bool(skirt.data.uv_layers), 'Installed skirt UV is missing')

    fabric = bpy.data.materials.get(FABRIC_MATERIAL)
    assert_true(fabric is not None, 'Installed fabric material is missing')
    assert_true(bool(fabric.get('rug_exportable_textures')), 'Installed PBR maps are missing')

    output_dir = output_directory('installed')
    preview_path = output_dir / 'installed_preview.png'
    result = bpy.ops.rug.render_preview('EXEC_DEFAULT', filepath=str(preview_path))
    assert_true('FINISHED' in result, f'Installed preview failed: {result}')
    assert_true(preview_path.exists() and preview_path.stat().st_size > 4096, 'Installed preview missing')

    settings.export_format = 'GLB'
    glb_path = output_dir / 'installed_test.glb'
    result = bpy.ops.rug.export_skirt('EXEC_DEFAULT', filepath=str(glb_path))
    assert_true('FINISHED' in result, f'Installed GLB export failed: {result}')
    assert_true(glb_path.exists() and glb_path.stat().st_size > 1024, 'Installed GLB missing')

    blend_path = output_dir / 'installed_test.blend'
    result = bpy.ops.rug.save_blend_copy('EXEC_DEFAULT', filepath=str(blend_path))
    assert_true('FINISHED' in result, f'Installed BLEND save failed: {result}')
    assert_true(blend_path.exists(), 'Installed BLEND missing')

    print('RUG_INSTALLED_EXTENSION_TEST_OK')
    print(f'Objects: {len(collection.objects)}')
    print(f'Preview: {preview_path}')
    print(f'GLB: {glb_path}')
    print(f'BLEND: {blend_path}')


if __name__ == '__main__':
    main()
