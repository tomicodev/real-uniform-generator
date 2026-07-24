import math

import bpy
from mathutils import Vector

from .constants import GENERATED_COLLECTION, ROOT_OBJECT


def smoothstep(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def ensure_collection(name=GENERATED_COLLECTION):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def clear_generated():
    collection = bpy.data.collections.get(GENERATED_COLLECTION)
    if collection is None:
        return
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def link_object(obj, collection=None):
    target = collection or ensure_collection()
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    target.objects.link(obj)
    return obj


def set_parent(obj, parent):
    obj.parent = parent
    obj.matrix_parent_inverse = parent.matrix_world.inverted()


def shade_smooth(obj):
    if obj.type != 'MESH':
        return
    for polygon in obj.data.polygons:
        polygon.use_smooth = True


def add_bevel(obj, width, segments=2):
    modifier = obj.modifiers.new('Construction Edge Softening', 'BEVEL')
    modifier.width = width
    modifier.segments = segments
    modifier.limit_method = 'ANGLE'
    modifier.angle_limit = math.radians(28.0)
    return modifier


def add_solidify(obj, thickness, offset=-0.55):
    modifier = obj.modifiers.new('Fabric Thickness', 'SOLIDIFY')
    modifier.thickness = thickness
    modifier.offset = offset
    modifier.use_even_offset = True
    modifier.use_quality_normals = True
    return modifier


def assign_uv_from_vertices(mesh, vertex_uvs, name='UVMap'):
    uv_layer = mesh.uv_layers.new(name=name)
    for polygon in mesh.polygons:
        for loop_index in polygon.loop_indices:
            vertex_index = mesh.loops[loop_index].vertex_index
            uv_layer.data[loop_index].uv = vertex_uvs[vertex_index]


def mesh_object(name, vertices, faces, vertex_uvs=None):
    mesh = bpy.data.meshes.new(name + '_Mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    if vertex_uvs:
        assign_uv_from_vertices(mesh, vertex_uvs)
    obj = bpy.data.objects.new(name, mesh)
    link_object(obj)
    return obj


def create_root():
    root = bpy.data.objects.new(ROOT_OBJECT, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.12
    link_object(root)
    return root


def skirt_point(settings, index, v, facets=10, radial_offset=0.0):
    around = settings.pleat_count * facets
    theta = (index % around) / around * math.tau
    fold_profile = (0.0, 0.30, 0.70, 1.0, 0.76, 0.34, 0.0, -0.42, -0.34, -0.15)
    fold = fold_profile[index % facets]

    eased = smoothstep(v)
    rx = settings.waist_width + (settings.hem_width - settings.waist_width) * eased
    ry = settings.waist_depth + (settings.hem_depth - settings.waist_depth) * eased

    stitch_ratio = min(0.82, settings.pleat_stitch_length / max(settings.skirt_length, 0.001))
    release = smoothstep((v - stitch_ratio) / max(0.001, 1.0 - stitch_ratio))
    pressed_depth = 0.010 + settings.pleat_depth * 0.16
    open_depth = settings.pleat_depth * (0.70 + 0.30 * v)
    fold_depth = pressed_depth * (1.0 - release) + open_depth * release

    gravity_back = settings.back_drop * max(0.0, -math.sin(theta)) * (v ** 1.65)
    hem_bias = 0.0025 * math.sin(theta * 2.0 + 0.45) * (v ** 1.40)

    wrinkle_gate = release * (v ** 1.45)
    wrinkle = settings.wrinkle_strength * wrinkle_gate * (
        0.58 * math.sin(theta * 3.0 + v * 9.0)
        + 0.26 * math.sin(theta * 7.0 - v * 13.0)
    )

    scale = 1.0 + fold * fold_depth + radial_offset
    x = math.cos(theta) * (rx * scale + wrinkle)
    y = math.sin(theta) * (ry * scale + wrinkle * 0.82)
    z = -settings.skirt_length * v - gravity_back - hem_bias
    return Vector((x, y, z))


def create_skirt_shell(settings, parent):
    facets = 10
    around = settings.pleat_count * facets
    rows = settings.vertical_segments
    row_size = around + 1
    vertices = []
    vertex_uvs = []
    faces = []

    for row in range(rows + 1):
        v = row / rows
        for index in range(around + 1):
            vertices.append(tuple(skirt_point(settings, index, v, facets)))
            vertex_uvs.append((index / around, 1.0 - v))

    for row in range(rows):
        for index in range(around):
            a = row * row_size + index
            b = a + 1
            c = a + row_size + 1
            d = a + row_size
            faces.append((a, d, c, b))

    obj = mesh_object('RUG_SkirtOuter', vertices, faces, vertex_uvs)
    add_solidify(obj, settings.fabric_thickness, -0.58)
    add_bevel(obj, min(0.0012, settings.fabric_thickness * 0.40), 2)
    shade_smooth(obj)
    set_parent(obj, parent)
    obj['rug_part'] = 'outer'
    return obj


def create_elliptic_band(settings, parent):
    segments = max(128, settings.pleat_count * 8)
    vertices = []
    uvs = []
    faces = []
    lower_z = -0.002
    upper_z = settings.waistband_height

    for row, z in enumerate((lower_z, upper_z)):
        for index in range(segments + 1):
            theta = index / segments * math.tau
            seam_shape = 1.0 + 0.004 * math.cos(theta - math.pi)
            vertices.append((
                math.cos(theta) * settings.waist_width * 1.018 * seam_shape,
                math.sin(theta) * settings.waist_depth * 1.018 * seam_shape,
                z,
            ))
            uvs.append((index / segments, row))

    row_size = segments + 1
    for index in range(segments):
        a = index
        b = index + 1
        c = row_size + index + 1
        d = row_size + index
        faces.append((a, d, c, b))

    obj = mesh_object('RUG_Waistband', vertices, faces, uvs)
    add_solidify(obj, settings.fabric_thickness * 1.55, -0.5)
    add_bevel(obj, min(0.0015, settings.fabric_thickness * 0.45), 3)
    shade_smooth(obj)
    set_parent(obj, parent)
    obj['rug_part'] = 'outer'

    if settings.waistband_overlap > 0.001:
        bpy.ops.mesh.primitive_cube_add(
            location=(settings.waist_width * 0.96, -0.012, settings.waistband_height * 0.54)
        )
        tab = bpy.context.object
        tab.name = 'RUG_WaistbandOverlap'
        tab.scale = (
            settings.waistband_overlap * 0.52,
            settings.fabric_thickness * 2.2,
            settings.waistband_height * 0.47,
        )
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        link_object(tab)
        add_bevel(tab, min(0.0015, settings.fabric_thickness * 0.5), 3)
        shade_smooth(tab)
        set_parent(tab, parent)
        tab['rug_part'] = 'outer'
        return obj, tab
    return obj, None


def create_lining(settings, parent):
    segments = max(128, settings.pleat_count * 6)
    rows = max(28, settings.vertical_segments // 2)
    row_size = segments + 1
    lining_length = settings.skirt_length * settings.lining_length_ratio
    vertices = []
    uvs = []
    faces = []

    for row in range(rows + 1):
        v = row / rows
        eased = smoothstep(v)
        rx = settings.waist_width * 0.955 + (settings.hem_width * 0.74 - settings.waist_width * 0.955) * eased
        ry = settings.waist_depth * 0.955 + (settings.hem_depth * 0.74 - settings.waist_depth * 0.955) * eased
        for index in range(segments + 1):
            theta = index / segments * math.tau
            drift = settings.wrinkle_strength * 0.45 * math.sin(theta * 4.0 + v * 7.0) * (v ** 1.5)
            vertices.append((
                math.cos(theta) * (rx + drift),
                math.sin(theta) * (ry + drift),
                -0.006 - lining_length * v,
            ))
            uvs.append((index / segments, 1.0 - v))

    for row in range(rows):
        for index in range(segments):
            a = row * row_size + index
            b = a + 1
            c = a + row_size + 1
            d = a + row_size
            faces.append((a, d, c, b))

    obj = mesh_object('RUG_Lining', vertices, faces, uvs)
    add_solidify(obj, max(0.0007, settings.fabric_thickness * 0.38), -0.4)
    add_bevel(obj, 0.00045, 2)
    shade_smooth(obj)
    set_parent(obj, parent)
    obj['rug_part'] = 'lining'
    return obj


def create_curve(name, points, bevel_depth, parent, cyclic=False, part='stitch'):
    curve = bpy.data.curves.new(name + '_Curve', type='CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 2
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 2
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for index, point in enumerate(points):
        spline.points[index].co = (*point, 1.0)
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, curve)
    link_object(obj)
    set_parent(obj, parent)
    obj['rug_part'] = part
    return obj


def ellipse_points(rx, ry, z, count=192, radial=0.0):
    points = []
    for index in range(count):
        theta = index / count * math.tau
        points.append((
            math.cos(theta) * (rx + radial),
            math.sin(theta) * (ry + radial),
            z,
        ))
    return points


def create_stitches(settings, parent):
    objects = []
    thread_radius = max(0.00035, settings.fabric_thickness * 0.22)
    objects.append(create_curve(
        'RUG_WaistTopStitch',
        ellipse_points(settings.waist_width * 1.021, settings.waist_depth * 1.021, settings.waistband_height - 0.004),
        thread_radius,
        parent,
        cyclic=True,
    ))
    objects.append(create_curve(
        'RUG_WaistBottomStitch',
        ellipse_points(settings.waist_width * 1.022, settings.waist_depth * 1.022, 0.006),
        thread_radius,
        parent,
        cyclic=True,
    ))
    objects.append(create_curve(
        'RUG_HemStitch',
        ellipse_points(settings.hem_width * 1.006, settings.hem_depth * 1.006, -settings.skirt_length + 0.018),
        thread_radius * 0.88,
        parent,
        cyclic=True,
    ))

    facets = 10
    steps = 10
    stitch_ratio = min(0.82, settings.pleat_stitch_length / max(settings.skirt_length, 0.001))
    ridge_index = 3
    for pleat in range(settings.pleat_count):
        around_index = pleat * facets + ridge_index
        points = []
        for step in range(steps + 1):
            v = stitch_ratio * step / steps
            point = skirt_point(settings, around_index, v, facets, radial_offset=0.004)
            points.append(tuple(point))
        objects.append(create_curve(
            f'RUG_PleatStitch_{pleat + 1:02d}',
            points,
            thread_radius * 0.72,
            parent,
        ))

    side_points = []
    side_index = int(settings.pleat_count * facets * 0.25)
    for step in range(24):
        v = step / 23
        side_points.append(tuple(skirt_point(settings, side_index, v, facets, radial_offset=0.003)))
    objects.append(create_curve('RUG_SideSeam', side_points, thread_radius * 0.65, parent))
    return objects


def append_box(vertices, faces, center, half_size):
    x, y, z = center
    hx, hy, hz = half_size
    base = len(vertices)
    vertices.extend([
        (x - hx, y - hy, z - hz), (x + hx, y - hy, z - hz),
        (x + hx, y + hy, z - hz), (x - hx, y + hy, z - hz),
        (x - hx, y - hy, z + hz), (x + hx, y - hy, z + hz),
        (x + hx, y + hy, z + hz), (x - hx, y + hy, z + hz),
    ])
    faces.extend([
        (base + 0, base + 1, base + 2, base + 3),
        (base + 4, base + 7, base + 6, base + 5),
        (base + 0, base + 4, base + 5, base + 1),
        (base + 1, base + 5, base + 6, base + 2),
        (base + 2, base + 6, base + 7, base + 3),
        (base + 4, base + 0, base + 3, base + 7),
    ])


def create_hardware(settings, parent):
    objects = []
    side_x = settings.waist_width * 1.02

    bpy.ops.mesh.primitive_cube_add(location=(side_x, 0.0, -settings.pleat_stitch_length * 0.46))
    zipper_tape = bpy.context.object
    zipper_tape.name = 'RUG_ZipperTape'
    zipper_tape.scale = (0.006, 0.012, settings.pleat_stitch_length * 0.48)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_object(zipper_tape)
    add_bevel(zipper_tape, 0.0008, 2)
    set_parent(zipper_tape, parent)
    zipper_tape['rug_part'] = 'hardware'
    objects.append(zipper_tape)

    vertices, faces = [], []
    tooth_count = max(12, int(settings.pleat_stitch_length / 0.006))
    for index in range(tooth_count):
        z = -0.008 - index * settings.pleat_stitch_length / tooth_count
        y = 0.004 if index % 2 == 0 else -0.004
        append_box(vertices, faces, (side_x + 0.006, y, z), (0.0022, 0.0028, 0.0015))
    teeth = mesh_object('RUG_ZipperTeeth', vertices, faces)
    add_bevel(teeth, 0.00045, 2)
    shade_smooth(teeth)
    set_parent(teeth, parent)
    teeth['rug_part'] = 'hardware'
    objects.append(teeth)

    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.012,
        minor_radius=0.0022,
        major_segments=32,
        minor_segments=8,
        location=(side_x + 0.010, 0.0, 0.006),
        rotation=(math.radians(90), 0.0, 0.0),
    )
    pull = bpy.context.object
    pull.name = 'RUG_ZipperPull'
    link_object(pull)
    set_parent(pull, parent)
    pull['rug_part'] = 'hardware'
    objects.append(pull)

    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.007,
        minor_radius=0.0014,
        major_segments=28,
        minor_segments=7,
        location=(side_x - 0.006, -0.008, settings.waistband_height * 0.55),
        rotation=(math.radians(90), 0.0, 0.0),
    )
    eye = bpy.context.object
    eye.name = 'RUG_HookEye'
    link_object(eye)
    set_parent(eye, parent)
    eye['rug_part'] = 'hardware'
    objects.append(eye)

    bpy.ops.mesh.primitive_cube_add(
        location=(side_x + settings.waistband_overlap * 0.35, 0.006, settings.waistband_height * 0.55)
    )
    hook = bpy.context.object
    hook.name = 'RUG_WaistHook'
    hook.scale = (0.010, 0.0018, 0.0018)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_object(hook)
    add_bevel(hook, 0.0008, 3)
    set_parent(hook, parent)
    hook['rug_part'] = 'hardware'
    objects.append(hook)
    return objects


def create_hem_facing(settings, parent):
    points = ellipse_points(
        settings.hem_width * 1.003,
        settings.hem_depth * 1.003,
        -settings.skirt_length + settings.fabric_thickness,
        count=256,
    )
    obj = create_curve(
        'RUG_HemFacing',
        points,
        max(settings.fabric_thickness * 0.95, 0.0016),
        parent,
        cyclic=True,
        part='outer',
    )
    return obj


def generate_uniform_skirt(settings, materials):
    clear_generated()
    ensure_collection()
    root = create_root()
    created = {'root': root, 'outer': [], 'lining': [], 'stitch': [], 'hardware': []}

    skirt = create_skirt_shell(settings, root)
    waistband, overlap = create_elliptic_band(settings, root)
    hem_facing = create_hem_facing(settings, root)
    created['outer'].extend([skirt, waistband, hem_facing])
    if overlap is not None:
        created['outer'].append(overlap)

    if settings.create_lining:
        created['lining'].append(create_lining(settings, root))
    if settings.create_stitches:
        created['stitch'].extend(create_stitches(settings, root))
    if settings.create_hardware:
        created['hardware'].extend(create_hardware(settings, root))

    for obj in created['outer']:
        if obj.type in {'MESH', 'CURVE'}:
            obj.data.materials.append(materials['fabric'])
    for obj in created['lining']:
        obj.data.materials.append(materials['lining'])
    for obj in created['stitch']:
        obj.data.materials.append(materials['thread'])
    for obj in created['hardware']:
        obj.data.materials.append(materials['metal'])

    root['rug_version'] = '0.2.0'
    root['rug_pleat_count'] = settings.pleat_count
    root['rug_skirt_length'] = settings.skirt_length
    return created


def generated_objects(include_root=False):
    collection = bpy.data.collections.get(GENERATED_COLLECTION)
    if collection is None:
        return []
    objects = list(collection.objects)
    if not include_root:
        objects = [obj for obj in objects if obj.type != 'EMPTY']
    return objects
