"""Run with:

blender --background --factory-startup --python tests/blender_smoke_test.py
"""

from pathlib import Path
import os
import sys
import tempfile

import bpy


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import real_uniform_generator
from real_uniform_generator.constants import FABRIC_MATERIAL, GENERATED_COLLECTION


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


def export_and_check(settings, output_dir, export_format):
    settings.export_format = export_format
    extension = export_format.lower()
    output_path = output_dir / f'smoke_test.{extension}'
    result = bpy.ops.rug.export_skirt('EXEC_DEFAULT', filepath=str(output_path))
    assert_true('FINISHED' in result, f'{export_format} export operator failed: {result}')
    assert_true(output_path.exists(), f'{export_format} was not created: {output_path}')
    assert_true(output_path.stat().st_size > 1024, f'{export_format} output is unexpectedly small')
    return output_path


def main():
    real_uniform_generator.register()
    try:
        scene = bpy.context.scene
        settings = scene.rug_settings
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
        required_names = {'RUG_SkirtOuter', 'RUG_Waistband', 'RUG_Lining'}
        missing = required_names - names
        assert_true(not missing, f'Missing generated objects: {sorted(missing)}')

        skirt = bpy.data.objects.get('RUG_SkirtOuter')
        assert_true(skirt is not None and skirt.type == 'MESH', 'Outer skirt mesh is missing')
        assert_true(len(skirt.data.vertices) > 1000, 'Outer skirt mesh is unexpectedly simple')
        assert_true(bool(skirt.data.uv_layers), 'Outer skirt UV map is missing')
        assert_true(bool(skirt.data.materials), 'Outer skirt material is missing')

        fabric = bpy.data.materials.get(FABRIC_MATERIAL)
        assert_true(fabric is not None, 'Fabric material is missing')
        assert_true(bool(fabric.get('rug_exportable_textures')), 'Packed PBR material was not created')
        packed_maps = [
            image for image in bpy.data.images
            if image.get('rug_map_type') in {'base_color', 'roughness', 'normal'}
        ]
        assert_true(len(packed_maps) == 3, f'Expected 3 packed maps, found {len(packed_maps)}')
        assert_true(all(image.packed_file for image in packed_maps), 'One or more PBR maps are not packed')

        output_dir = output_directory('source')
        glb_path = export_and_check(settings, output_dir, 'GLB')
        fbx_path = export_and_check(settings, output_dir, 'FBX')
        obj_path = export_and_check(settings, output_dir, 'OBJ')

        mtl_path = obj_path.with_suffix('.mtl')
        assert_true(mtl_path.exists(), 'OBJ material file was not created')
        texture_dir = output_dir / f'{obj_path.stem}_textures'
        texture_files = list(texture_dir.glob('*.png'))
        assert_true(len(texture_files) == 3, f'Expected 3 OBJ texture files, found {len(texture_files)}')

        blend_path = output_dir / 'smoke_test.blend'
        result = bpy.ops.rug.save_blend_copy('EXEC_DEFAULT', filepath=str(blend_path))
        assert_true('FINISHED' in result, f'BLEND save operator failed: {result}')
        assert_true(blend_path.exists(), 'BLEND copy was not created')

        print('RUG_SMOKE_TEST_OK')
        print(f'Generated objects: {len(collection.objects)}')
        print(f'Packed maps: {[image.name for image in packed_maps]}')
        print(f'GLB: {glb_path}')
        print(f'FBX: {fbx_path}')
        print(f'OBJ: {obj_path}')
        print(f'BLEND: {blend_path}')
    finally:
        real_uniform_generator.unregister()


if __name__ == '__main__':
    main()
