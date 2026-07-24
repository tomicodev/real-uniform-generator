"""Executed after installing and enabling the extension in an isolated repo."""

from pathlib import Path
import tempfile

import bpy


GENERATED_COLLECTION = 'RUG_UniformSkirt'
FABRIC_MATERIAL = 'RUG_UniformFabric'


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def export_and_check(settings, output_dir, export_format):
    settings.export_format = export_format
    extension = export_format.lower()
    output_path = output_dir / f'installed_test.{extension}'
    result = bpy.ops.rug.export_skirt('EXEC_DEFAULT', filepath=str(output_path))
    assert_true('FINISHED' in result, f'{export_format} export failed: {result}')
    assert_true(output_path.exists(), f'{export_format} was not created: {output_path}')
    assert_true(output_path.stat().st_size > 1024, f'{export_format} output is unexpectedly small')
    return output_path


def main():
    assert_true(
        hasattr(bpy.types.Scene, 'rug_settings'),
        'Installed extension is not registered or enabled',
    )
    assert_true(
        hasattr(bpy.ops.rug, 'generate_skirt'),
        'Generate operator is not registered',
    )

    settings = bpy.context.scene.rug_settings
    settings.pleat_count = 18
    settings.skirt_length = 0.48
    settings.vertical_segments = 48
    settings.create_lining = True
    settings.create_stitches = True
    settings.create_hardware = True
    settings.texture_resolution = '512'

    result = bpy.ops.rug.generate_skirt()
    assert_true('FINISHED' in result, f'Generate operator failed: {result}')

    collection = bpy.data.collections.get(GENERATED_COLLECTION)
    assert_true(collection is not None, 'Generated collection was not created')
    names = {obj.name for obj in collection.objects}
    required = {
        'RUG_SkirtOuter',
        'RUG_Waistband',
        'RUG_Lining',
        'RUG_ZipperTape',
        'RUG_ZipperTeeth',
        'RUG_ZipperPull',
        'RUG_HookEye',
        'RUG_WaistHook',
    }
    missing = required - names
    assert_true(not missing, f'Missing installed-extension objects: {sorted(missing)}')

    skirt = bpy.data.objects.get('RUG_SkirtOuter')
    assert_true(skirt is not None and skirt.type == 'MESH', 'Outer skirt is missing')
    assert_true(len(skirt.data.vertices) > 1000, 'Outer skirt is unexpectedly simple')
    assert_true(bool(skirt.data.uv_layers), 'Outer skirt UV is missing')

    fabric = bpy.data.materials.get(FABRIC_MATERIAL)
    assert_true(fabric is not None, 'Fabric material is missing')
    assert_true(bool(fabric.get('rug_exportable_textures')), 'Packed PBR material is missing')
    maps = [
        image for image in bpy.data.images
        if image.get('rug_map_type') in {'base_color', 'roughness', 'normal'}
    ]
    assert_true(len(maps) == 3, f'Expected 3 packed PBR maps, found {len(maps)}')
    assert_true(all(image.packed_file for image in maps), 'PBR images are not packed')

    output_dir = Path(tempfile.mkdtemp(prefix='rug_installed_'))
    glb_path = export_and_check(settings, output_dir, 'GLB')
    fbx_path = export_and_check(settings, output_dir, 'FBX')
    obj_path = export_and_check(settings, output_dir, 'OBJ')

    assert_true(obj_path.with_suffix('.mtl').exists(), 'OBJ MTL was not created')
    texture_dir = output_dir / f'{obj_path.stem}_textures'
    assert_true(len(list(texture_dir.glob('*.png'))) == 3, 'OBJ PBR textures were not created')

    blend_path = output_dir / 'installed_test.blend'
    result = bpy.ops.rug.save_blend_copy('EXEC_DEFAULT', filepath=str(blend_path))
    assert_true('FINISHED' in result, f'BLEND copy failed: {result}')
    assert_true(blend_path.exists(), 'BLEND copy was not created')

    print('RUG_INSTALLED_EXTENSION_TEST_OK')
    print(f'Generated objects: {len(collection.objects)}')
    print(f'GLB: {glb_path}')
    print(f'FBX: {fbx_path}')
    print(f'OBJ: {obj_path}')
    print(f'BLEND: {blend_path}')


if __name__ == '__main__':
    main()
