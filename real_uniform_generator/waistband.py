from __future__ import annotations

from .geometry import add_bevel, add_solidify, create_mesh_object, set_parent, shade_smooth
from .pattern import ellipse_axes_from_circumference, ellipse_circumference, ellipse_frame, zipper_u


def _band_mesh(settings, name, cross_section, parent, part):
    a, b = ellipse_axes_from_circumference(settings.waist_circumference, settings.body_depth_ratio)
    segments = max(128, settings.pleat_count * 8)
    repeat_m = max(0.005, settings.texture_tile_cm / 100.0)
    circumference = ellipse_circumference(a, b)
    seam = zipper_u(settings)
    vertices, uvs, faces = [], [], []
    cross_count = len(cross_section)
    for index in range(segments + 1):
        u = seam + index / segments
        position, _, normal = ellipse_frame(a, b, u)
        for radial, z in cross_section:
            point = position + normal * radial
            point.z = z
            vertices.append(tuple(point))
            uvs.append((circumference * index / segments / repeat_m, z / repeat_m))
    for index in range(segments):
        for cross in range(cross_count - 1):
            a0 = index * cross_count + cross
            a1 = a0 + 1
            b0 = (index + 1) * cross_count + cross
            b1 = b0 + 1
            faces.append((a0, b0, b1, a1))
    obj = create_mesh_object(name, vertices, faces, uvs)
    shade_smooth(obj)
    set_parent(obj, parent)
    obj['rug_part'] = part
    return obj


def create_waistband(settings, parent):
    h = settings.waistband_height
    t = settings.fabric_thickness
    # One sewn shell: outer belt face -> rounded top turn -> inner facing.
    cross_section = (
        (0.0010, 0.000),
        (0.0010, h - 0.0012),
        (0.0002, h + 0.0006),
        (-0.0018, h - 0.0010),
        (-0.0024, 0.0040),
        (-0.0012, 0.0015),
    )
    shell = _band_mesh(settings, 'RUG_WaistbandShell', cross_section, parent, 'outer')
    add_solidify(shell, max(0.00075, t * 0.72), -0.35)
    add_bevel(shell, min(0.00055, t * 0.40), 2)
    shell['rug_construction'] = 'outer_face_top_fold_inner_facing'

    interfacing = _band_mesh(
        settings,
        'RUG_WaistbandInterfacing',
        ((-0.0007, 0.0045), (-0.0007, h - 0.0040)),
        parent,
        'interfacing',
    )
    add_solidify(interfacing, 0.00038, -0.5)
    interfacing['rug_construction'] = 'fusible_interfacing'
    return {'outer': [shell], 'internal': [interfacing]}
