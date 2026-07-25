from __future__ import annotations

import math
from dataclasses import dataclass
from mathutils import Vector


@dataclass(frozen=True)
class PleatColumn:
    tangent: float
    normal: float
    role: str


# Continuous cloth order for one knife pleat. Tangent intentionally moves
# backward through the hidden underfold before returning to the next panel.
PLEAT_COLUMNS = (
    PleatColumn(0.000, 0.000, 'visible_start'),
    PleatColumn(0.070, 0.080, 'left_shoulder'),
    PleatColumn(0.790, 0.035, 'visible_panel'),
    PleatColumn(0.895, 0.280, 'knife_edge'),
    PleatColumn(0.185, -1.000, 'underfold_return'),
    PleatColumn(0.650, -0.820, 'underfold_panel'),
    PleatColumn(0.965, -0.100, 'forward_fold'),
)


def smoothstep(value: float) -> float:
    value = max(0.0, min(1.0, float(value)))
    return value * value * (3.0 - 2.0 * value)


def smootherstep(value: float) -> float:
    value = max(0.0, min(1.0, float(value)))
    return value ** 3 * (value * (value * 6.0 - 15.0) + 10.0)


def ellipse_circumference(a: float, b: float) -> float:
    a = max(float(a), 1e-6)
    b = max(float(b), 1e-6)
    h = ((a - b) ** 2) / ((a + b) ** 2)
    return math.pi * (a + b) * (1.0 + (3.0 * h) / (10.0 + math.sqrt(max(1e-9, 4.0 - 3.0 * h))))


def ellipse_axes_from_circumference(circumference: float, depth_ratio: float):
    depth_ratio = max(0.50, min(1.0, float(depth_ratio)))
    unit = ellipse_circumference(1.0, depth_ratio)
    a = max(float(circumference), 0.10) / unit
    return a, a * depth_ratio


def ellipse_frame(a: float, b: float, u: float):
    theta = math.tau * u
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    position = Vector((a * cos_t, b * sin_t, 0.0))
    tangent = Vector((-a * sin_t, b * cos_t, 0.0)).normalized()
    normal = Vector((cos_t / max(a, 1e-6), sin_t / max(b, 1e-6), 0.0)).normalized()
    return position, tangent, normal


def body_axes(settings, v: float):
    waist_a, waist_b = ellipse_axes_from_circumference(settings.waist_circumference, settings.body_depth_ratio)
    hip_a, hip_b = ellipse_axes_from_circumference(settings.hip_circumference, settings.body_depth_ratio)
    hem_a, hem_b = ellipse_axes_from_circumference(settings.hip_circumference + settings.hem_ease, settings.body_depth_ratio)
    hip_ratio = min(0.80, settings.hip_line / max(settings.skirt_length, 1e-6))
    if v <= hip_ratio:
        blend = smootherstep(v / max(hip_ratio, 1e-6))
        return waist_a + (hip_a - waist_a) * blend, waist_b + (hip_b - waist_b) * blend
    lower = smootherstep((v - hip_ratio) / max(1e-6, 1.0 - hip_ratio))
    return hip_a + (hem_a - hip_a) * lower, hip_b + (hem_b - hip_b) * lower


def pleat_release(settings, v: float) -> float:
    stitched = min(0.82, settings.pleat_stitch_length / max(settings.skirt_length, 1e-6))
    transition = max(0.020, settings.pleat_release_length / max(settings.skirt_length, 1e-6))
    return smootherstep((v - stitched) / transition)


def fold_depth(settings, v: float) -> float:
    release = pleat_release(settings, v)
    sewn_depth = max(settings.fabric_thickness * 2.2, 0.0028)
    # pleat_depth is the flat pattern underfold; only its fold-angle projection
    # becomes radial depth in the worn garment.
    free_depth = settings.pleat_depth * 0.72 * (0.88 + 0.12 * v)
    return sewn_depth * (1.0 - release) + free_depth * release


def body_drift(settings, u: float, v: float):
    release = pleat_release(settings, v)
    gate = release * (v ** 1.65)
    theta = math.tau * u
    radial = settings.wrinkle_strength * gate * (0.55 * math.sin(theta * 2.0 + v * 7.0) + 0.28 * math.sin(theta * 5.0 - v * 11.0) + 0.17 * math.sin(theta * 9.0 + v * 4.0))
    vertical = settings.back_drop * max(0.0, math.sin(theta)) * (v ** 1.75)
    return radial, vertical


def zipper_u(settings) -> float:
    return {'LEFT': 0.50, 'BACK': 0.25, 'RIGHT': 0.00}.get(settings.zipper_position, 0.50)


def build_row(settings, v: float, radial_offset: float = 0.0, z_offset: float = 0.0):
    a, b = body_axes(settings, v)
    circumference = ellipse_circumference(a, b)
    pitch = circumference / settings.pleat_count
    depth = fold_depth(settings, v)
    repeat_m = max(0.005, settings.texture_tile_cm / 100.0)
    seam = zipper_u(settings)
    entries = []
    flat_distance = 0.0
    previous_flat = None
    for pleat_index in range(settings.pleat_count):
        for local_index, column in enumerate(PLEAT_COLUMNS):
            finished_distance = (pleat_index + column.tangent) * pitch
            u = seam + finished_distance / circumference
            position, tangent, normal = ellipse_frame(a, b, u)
            radial_drift, vertical_drop = body_drift(settings, u, v)
            point = position + normal * (column.normal * depth + radial_offset + radial_drift)
            point.z = -settings.skirt_length * v - vertical_drop + z_offset
            flat_point = Vector((finished_distance, column.normal * depth, 0.0))
            if previous_flat is not None:
                flat_distance += (flat_point - previous_flat).length
            previous_flat = flat_point
            entries.append({'point': point, 'uv': (flat_distance / repeat_m, settings.skirt_length * (1.0 - v) / repeat_m), 'role': column.role, 'pleat': pleat_index, 'local': local_index, 'u': u, 'normal': normal, 'tangent': tangent})
    u = seam + 1.0
    position, tangent, normal = ellipse_frame(a, b, u)
    radial_drift, vertical_drop = body_drift(settings, u, v)
    point = position + normal * (radial_offset + radial_drift)
    point.z = -settings.skirt_length * v - vertical_drop + z_offset
    final_flat = Vector((circumference, 0.0, 0.0))
    if previous_flat is not None:
        flat_distance += (final_flat - previous_flat).length
    entries.append({'point': point, 'uv': (flat_distance / repeat_m, settings.skirt_length * (1.0 - v) / repeat_m), 'role': 'seam', 'pleat': settings.pleat_count, 'local': 0, 'u': u, 'normal': normal, 'tangent': tangent})
    return entries
