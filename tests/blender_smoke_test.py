"""Run with Blender 4.3+ / 5.2:

blender --background --factory-startup --python-exit-code 1 \
  --python tests/blender_smoke_test.py
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
    output_path = output_dir / f'smoke_test.{export_format.lower()}'
    result = bpy.ops.rug.export_skirt('EXEC_DEFAULT', filepath=str(output_path))
    assert_true('FINISHED' in result, f'{export_format} export failed: {result}')
    assert_true(output_path.exists(), f'{export_format} was not created: {output_path}')
    assert_true(output_path.stat().st_size > 1024, f'{export_format} is unexpectedly small')
    return output_path


def main():
    real_uniform_generator.register()
    try:
        settings = bpy.context.scene.rug_settings
        settings.pleat_count = 20
        settings.vertical_segments = 48
        settings.texture_resolution = '512'
        settings.show_internal_construction = True
        settings.material_source = 'PROCEDURAL'

        result = bpy.ops.rug.generate_skirt()
        assert_true('FINISHED' in result, f'Generate operator failed: {result}')

        collection = bpy.data.collections.get(GENERATED_COLLECTION)
        assert_true(collection is not None, 'Generated collection was not created')
        names = {obj.name for obj in collection.objects}
        required = {
            'RUG_SkirtOuter',
            'RUG_Waistband',
            'RUG_HemFacingInner',
            'RUG_Lining',
            'RUG_ZipperSeamAllowance_L',
            'RUG_ZipperSeamAllowance_R',
            'RUG_ZipperTape_L',
            'RUG_ZipperTape_R',
            'RUG_ZipperCoil_L',
            'RUG_ZipperCoil_R',
            'RUG_ZipperSlider',
            'RUG_ZipperPull',
            'RUG_ZipperBottomStop',
            'RUG_WaistHook',
            'RUG_HookEye',
        }
        missing = required - names
        assert_true(not missing, f'Missing objects: {sorted(missing)}')
        assert_true('RUG_HemFacing' not in names, 'Legacy exterior hem ring still exists')

        skirt = bpy.data.objects['RUG_SkirtOuter']
        assert_true(skirt.type == 'MESH', 'Outer skirt is not a mesh')
        assert_true(len(skirt.data.vertices) > 4000, 'Outer skirt is unexpectedly simple')
        assert_true(bool(skirt.data.uv_layers), 'Outer skirt UV is missing')
        assert_true(skirt.data.attributes.get('rug_fold_role') is not None, 'Fold role attribute is missing')
        sharp_edges = sum(1 for edge in skirt.data.edges if edge.use_edge_sharp)
        assert_true(sharp_edges >= settings.pleat_count, f'Pleat sharp edges missing: {sharp_edges}')

        hem = bpy.data.objects['RUG_HemFacingInner']
        outer_radius = max((vertex.co.x ** 2 + vertex.co.y ** 2) ** 0.5 for vertex in skirt.data.vertices)
        hem_radius = max((vertex.co.x ** 2 + vertex.co.y ** 2) ** 0.5 for vertex in hem.data.vertices)
        assert_true(hem_radius < outer_radius, 'Hem facing is not inside the skirt')

        fabric = bpy.data.materials.get(FABRIC_MATERIAL)
        assert_true(fabric is not None, 'Fabric material is missing')
        assert_true(bool(fabric.get('rug_exportable_textures')), 'Generated PBR material is missing')
        maps = [image for image in bpy.data.images if image.get('rug_map_type')]
        map_types = {image.get('rug_map_type') for image in maps}
        assert_true({'base_color', 'roughness', 'normal', 'height'} <= map_types, f'PBR maps missing: {map_types}')
        assert_true(all(image.packed_file for image in maps if image.get('rug_generated')), 'Generated maps are not packed')

        output_dir = output_directory('source')
        preview_path = output_dir / 'preview.png'
        result = bpy.ops.rug.render_preview('EXEC_DEFAULT', filepath=str(preview_path))
        assert_true('FINISHED' in result, f'Preview render failed: {result}')
        assert_true(preview_path.exists() and preview_path.stat().st_size > 4096, 'Preview is missing')

        glb_path = export_and_check(settings, output_dir, 'GLB')
        fbx_path = export_and_check(settings, output_dir, 'FBX')
        obj_path = export_and_check(settings, output_dir, 'OBJ')
        assert_true(obj_path.with_suffix('.mtl').exists(), 'OBJ MTL is missing')
        texture_dir = output_dir / f'{obj_path.stem}_textures'
        assert_true(len(list(texture_dir.glob('*.png'))) >= 4, 'External PBR textures are missing')

        blend_path = output_dir / 'smoke_test.blend'
        result = bpy.ops.rug.save_blend_copy('EXEC_DEFAULT', filepath=str(blend_path))
        assert_true('FINISHED' in result, f'BLEND save failed: {result}')
        assert_true(blend_path.exists(), 'BLEND copy is missing')

        print('RUG_SMOKE_TEST_OK')
        print(f'Objects: {len(collection.objects)}')
        print(f'Sharp edges: {sharp_edges}')
        print(f'Preview: {preview_path}')
        print(f'GLB: {glb_path}')
        print(f'FBX: {fbx_path}')
        print(f'OBJ: {obj_path}')
        print(f'BLEND: {blend_path}')
    finally:
        real_uniform_generator.unregister()


if __name__ == '__main__':
    main()
