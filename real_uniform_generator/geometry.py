from __future__ import annotations

import bpy

from .hem import build_hem_rows
from .pattern import build_row

GENERATED_COLLECTION = 'RUG_Generated'
ROOT_OBJECT = 'RUG_UniformSkirt'


def ensure_collection():
    collection = bpy.data.collections.get(GENERATED_COLLECTION)
    if collection is None:
        collection = bpy.data.collections.new(GENERATED_COLLECTION)
        bpy.context.scene.collection.children.link(collection)
    return collection


def clear_generated():
    collection = bpy.data.collections.get(GENERATED_COLLECTION)
    if collection is None:
        return
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(collection)


def link_object(obj):
    collection = ensure_collection()
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def set_parent(obj, parent):
    obj.parent = parent
    obj.matrix_parent_inverse = parent.matrix_world.inverted()


def create_mesh_object(name, vertices, faces, vertex_uvs=None):
    mesh = bpy.data.meshes.new(name + '_Mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    if vertex_uvs:
        uv_layer = mesh.uv_layers.new(name='UVMap')
        for polygon in mesh.polygons:
            for loop_index in polygon.loop_indices:
                vi = mesh.loops[loop_index].vertex_index
                uv_layer.data[loop_index].uv = vertex_uvs[vi]
    obj = bpy.data.objects.new(name, mesh)
    link_object(obj)
    return obj


def shade_smooth(obj):
    if obj.type == 'MESH':
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    return obj


def add_solidify(obj, thickness, offset=-0.5):
    modifier = obj.modifiers.new('Physical Fabric Thickness', 'SOLIDIFY')
    modifier.thickness = thickness
    modifier.offset = offset
    # Even-offset miters explode at acute real pleat valleys; physical cloth
    # thickness is applied along surface normals instead.
    modifier.use_even_offset = False
    if hasattr(modifier, 'use_quality_normals'):
        modifier.use_quality_normals = True
    return modifier


def add_bevel(obj, width=0.0005, segments=2):
    modifier = obj.modifiers.new('Sewn Edge Softening', 'BEVEL')
    modifier.width = width
    modifier.segments = segments
    modifier.limit_method = 'ANGLE'
    return modifier


def create_root():
    root = bpy.data.objects.new(ROOT_OBJECT, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.10
    link_object(root)
    root['rug_version'] = '0.6.0'
    return root


def create_skirt_outer(settings, parent):
    rows = []
    for row_index in range(settings.vertical_segments + 1):
        rows.append(build_row(settings, row_index / settings.vertical_segments))
    rows.extend(build_hem_rows(settings, build_row))
    row_size = len(rows[0])
    vertices, uvs, faces = [], [], []
    for row in rows:
        vertices.extend(tuple(entry['point']) for entry in row)
        uvs.extend(entry['uv'] for entry in row)
    for r in range(len(rows) - 1):
        for c in range(row_size - 1):
            a = r * row_size + c
            b = a + 1
            d = (r + 1) * row_size + c
            e = d + 1
            faces.append((a, d, e, b))
    obj = create_mesh_object('RUG_SkirtOuter', vertices, faces, uvs)
    add_solidify(obj, settings.fabric_thickness, -0.5)
    shade_smooth(obj)
    set_parent(obj, parent)
    obj['rug_part'] = 'outer'
    obj['rug_construction'] = 'continuous_cloth_with_integrated_hem'
    obj['rug_uv_tile_cm'] = settings.texture_tile_cm
    return obj


def create_seam_line(settings, parent):
    from .pattern import body_axes, ellipse_frame, zipper_u
    curve = bpy.data.curves.new('RUG_LeftSideSeam_Curve', 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.00024
    curve.bevel_resolution = 1
    spline = curve.splines.new('POLY')
    count = 40
    spline.points.add(count - 1)
    for index in range(count):
        v = index / (count - 1)
        a, b = body_axes(settings, v)
        pos, _, normal = ellipse_frame(a, b, zipper_u(settings))
        pos += normal * 0.0008
        pos.z = -settings.skirt_length * v
        spline.points[index].co = (*pos, 1.0)
    obj = bpy.data.objects.new('RUG_LeftSideSeam', curve)
    link_object(obj)
    set_parent(obj, parent)
    obj['rug_part'] = 'stitch'
    return obj


def generate_uniform_skirt(settings, materials):
    clear_generated()
    root = create_root()
    created = {'root': root, 'outer': [], 'lining': [], 'stitch': [], 'hardware': [], 'internal': []}
    skirt = create_skirt_outer(settings, root)
    created['outer'].append(skirt)
    from .waistband import create_waistband
    from .lining import create_lining
    from .zipper import create_concealed_zipper
    waistband_parts = create_waistband(settings, root)
    created['outer'].extend(waistband_parts['outer'])
    created['internal'].extend(waistband_parts['internal'])
    if settings.create_lining:
        created['lining'].append(create_lining(settings, root))
    zipper_parts = create_concealed_zipper(settings, root)
    created['hardware'].extend(zipper_parts['hardware'])
    created['internal'].extend(zipper_parts['internal'])
    if settings.create_stitches:
        created['stitch'].append(create_seam_line(settings, root))
    if settings.create_simulation:
        from .simulation import configure_cloth
        configure_cloth(skirt, settings)
    for obj in created['outer']:
        if obj.type in {'MESH', 'CURVE'}:
            obj.data.materials.append(materials['fabric'])
    for obj in created['lining']:
        obj.data.materials.append(materials['lining'])
    for obj in created['stitch']:
        obj.data.materials.append(materials['thread'])
    for obj in created['hardware']:
        obj.data.materials.append(materials['metal'])
    for obj in created['internal']:
        part = obj.get('rug_part')
        if part == 'interfacing':
            material = materials['interfacing']
        elif part == 'seam_allowance':
            material = materials['fabric']
        else:
            material = materials['zipper']
        obj.data.materials.append(material)
    root['rug_pleat_count'] = settings.pleat_count
    root['rug_waist_cm'] = settings.waist_circumference * 100.0
    root['rug_hip_cm'] = settings.hip_circumference * 100.0
    return created


def generated_objects(include_root=False):
    collection = bpy.data.collections.get(GENERATED_COLLECTION)
    if collection is None:
        return []
    objects = list(collection.objects)
    if not include_root:
        objects = [obj for obj in objects if obj.type != 'EMPTY']
    return objects
