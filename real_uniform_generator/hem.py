from __future__ import annotations


def build_hem_rows(settings, build_row):
    """Return rows that turn the outer cloth inward and upward as one surface."""
    rows = []
    bottom = build_row(settings, 1.0, radial_offset=-settings.fabric_thickness * 0.70, z_offset=0.0004)
    rows.append(bottom)
    segments = max(6, int(settings.hem_turnup / 0.006))
    repeat_m = max(0.005, settings.texture_tile_cm / 100.0)
    for index in range(1, segments + 1):
        t = index / segments
        v = max(0.0, 1.0 - (settings.hem_turnup / settings.skirt_length) * t)
        row = build_row(settings, v, radial_offset=-(settings.fabric_thickness * 2.2 + 0.0012))
        for entry in row:
            entry['uv'] = (entry['uv'][0], -settings.hem_turnup * t / repeat_m)
            entry['role'] = 'hem_return'
        rows.append(row)
    return rows
