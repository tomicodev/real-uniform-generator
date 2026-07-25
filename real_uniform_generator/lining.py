from __future__ import annotations

import math

from .geometry import add_solidify, create_mesh_object, set_parent, shade_smooth
from .pattern import body_axes, ellipse_frame, zipper_u


def create_lining(settings, parent):
    segments = max(96, settings.pleat_count * 5)
    rows = max(32, settings.vertical_segments // 2)
    seam = zipper_u(settings)
    repeat_m = max(0.005, settings.texture_tile_cm / 100.0)
    vertices, uvs, faces = [], [], []
    for row in range(rows + 1):
        v = row / rows
        outer_v = min(1.0, settings.lining_length * v / settings.skirt_length)
        a, b = body_axes(settings, outer_v)
        ease = 0.94 + 0.015 * v
        a *= ease
        b *= ease
        for index in range(segments + 1):
            u = seam + index / segments
            point, _, _ = ellipse_frame(a, b, u)
            point.z = -0.008 - settings.lining_length * v
            vertices.append(tuple(point))
            uvs.append((index / segments * (2.0 * math.pi * max(a, b)) / repeat_m, settings.lining_length * (1.0 - v) / repeat_m))
    row_size = segments + 1
    for row in range(rows):
        for index in range(segments):
            a0 = row * row_size + index
            b0 = a0 + 1
            c0 = (row + 1) * row_size + index + 1
            d0 = c0 - 1
            faces.append((a0, d0, c0, b0))
    obj = create_mesh_object('RUG_Lining', vertices, faces, uvs)
    add_solidify(obj, 0.00055, -0.5)
    shade_smooth(obj)
    set_parent(obj, parent)
    obj['rug_part'] = 'lining'
    obj['rug_construction'] = 'seam_open_inner_lining'
    return obj
