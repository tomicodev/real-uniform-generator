import math

import bmesh


def mark_sharp_edges(obj, angle_degrees=7.5):
    if obj.type != 'MESH' or not obj.data.polygons:
        return

    mesh = obj.data
    for polygon in mesh.polygons:
        polygon.use_smooth = True

    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        threshold = math.radians(angle_degrees)
        for edge in bm.edges:
            if len(edge.link_faces) != 2:
                continue
            angle = edge.calc_face_angle(0.0)
            delta = edge.verts[1].co - edge.verts[0].co
            is_mainly_vertical = abs(delta.z) >= max(abs(delta.x), abs(delta.y)) * 0.75
            if is_mainly_vertical and angle >= threshold:
                edge.smooth = False
        bm.to_mesh(mesh)
        mesh.update()
    finally:
        bm.free()


def configure_bevel_normals(obj):
    for modifier in obj.modifiers:
        if modifier.type != 'BEVEL':
            continue
        if hasattr(modifier, 'harden_normals'):
            modifier.harden_normals = True
        if hasattr(modifier, 'use_clamp_overlap'):
            modifier.use_clamp_overlap = True


def finish_generated_geometry(created):
    for obj in created.get('outer', []):
        if obj.type != 'MESH':
            continue
        if obj.name == 'RUG_SkirtOuter':
            mark_sharp_edges(obj, 5.0)
        else:
            mark_sharp_edges(obj, 18.0)
        configure_bevel_normals(obj)

    for obj in created.get('lining', []):
        if obj.type == 'MESH':
            for polygon in obj.data.polygons:
                polygon.use_smooth = True
            configure_bevel_normals(obj)
