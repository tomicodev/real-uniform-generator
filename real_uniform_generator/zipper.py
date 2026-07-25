from __future__ import annotations

import math
import bpy

from .geometry import add_bevel, add_solidify, create_mesh_object, link_object, set_parent
from .pattern import body_axes, ellipse_frame, zipper_u


def _seam_strip(settings, parent, name, tangent_offset, width, inward, part):
    steps = 36
    vertices, uvs, faces = [], [], []
    max_v = min(0.62, settings.zipper_length / settings.skirt_length)
    for index in range(steps + 1):
        v = max_v * index / steps
        a, b = body_axes(settings, v)
        position, tangent, normal = ellipse_frame(a, b, zipper_u(settings))
        center = position + tangent * tangent_offset - normal * inward
        center.z = -settings.skirt_length * v
        p0 = center - tangent * (width * 0.5)
        p1 = center + tangent * (width * 0.5)
        vertices.extend((tuple(p0), tuple(p1)))
        uvs.extend(((0.0, v), (1.0, v)))
    for index in range(steps):
        a0 = index * 2
        faces.append((a0, a0 + 2, a0 + 3, a0 + 1))
    obj = create_mesh_object(name, vertices, faces, uvs)
    add_solidify(obj, 0.00035 if part == 'zipper' else settings.fabric_thickness * 0.72, -0.5)
    set_parent(obj, parent)
    obj['rug_part'] = part
    return obj


def _coil_curve(settings, parent, name, tangent_offset):
    curve = bpy.data.curves.new(name + '_Curve', 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.00042
    curve.bevel_resolution = 1
    spline = curve.splines.new('POLY')
    count = max(36, int(settings.zipper_length / 0.003))
    spline.points.add(count - 1)
    max_v = settings.zipper_length / settings.skirt_length
    for index in range(count):
        v = max_v * index / (count - 1)
        a, b = body_axes(settings, v)
        position, tangent, normal = ellipse_frame(a, b, zipper_u(settings))
        zig = 0.00045 * math.sin(index * math.pi * 0.5)
        point = position + tangent * (tangent_offset + zig) - normal * 0.0082
        point.z = -settings.skirt_length * v
        spline.points[index].co = (*point, 1.0)
    obj = bpy.data.objects.new(name, curve)
    link_object(obj)
    set_parent(obj, parent)
    obj['rug_part'] = 'zipper'
    return obj


def _box(name, center, half_size, parent, part='hardware'):
    x, y, z = center
    hx, hy, hz = half_size
    vertices = [
        (x-hx,y-hy,z-hz),(x+hx,y-hy,z-hz),(x+hx,y+hy,z-hz),(x-hx,y+hy,z-hz),
        (x-hx,y-hy,z+hz),(x+hx,y-hy,z+hz),(x+hx,y+hy,z+hz),(x-hx,y+hy,z+hz),
    ]
    faces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(4,0,3,7)]
    obj = create_mesh_object(name, vertices, faces)
    add_bevel(obj, 0.00045, 2)
    set_parent(obj, parent)
    obj['rug_part'] = part
    return obj


def create_concealed_zipper(settings, parent):
    seam_allowance_a = _seam_strip(settings, parent, 'RUG_SeamAllowanceFront', 0.0085, 0.018, 0.0045, 'seam_allowance')
    seam_allowance_b = _seam_strip(settings, parent, 'RUG_SeamAllowanceBack', -0.0085, 0.018, 0.0045, 'seam_allowance')
    tape_a = _seam_strip(settings, parent, 'RUG_ZipperTapeA', 0.0062, 0.011, 0.0070, 'zipper')
    tape_b = _seam_strip(settings, parent, 'RUG_ZipperTapeB', -0.0062, 0.011, 0.0070, 'zipper')
    coil_a = _coil_curve(settings, parent, 'RUG_ZipperCoilA', 0.0012)
    coil_b = _coil_curve(settings, parent, 'RUG_ZipperCoilB', -0.0012)
    a, b = body_axes(settings, 0.018)
    position, tangent, normal = ellipse_frame(a, b, zipper_u(settings))
    slider_center = position - normal * 0.0090
    slider_center.z = -0.014
    slider = _box('RUG_ConcealedSlider', tuple(slider_center), (0.0038, 0.0022, 0.0055), parent)
    pull_center = slider_center - normal * 0.0025
    pull_center.z -= 0.0075
    pull = _box('RUG_InternalPullTab', tuple(pull_center), (0.0026, 0.0008, 0.0042), parent)
    slider['rug_construction'] = 'small_internal_slider'
    return {
        'internal': [seam_allowance_a, seam_allowance_b, tape_a, tape_b, coil_a, coil_b],
        'hardware': [slider, pull],
    }
