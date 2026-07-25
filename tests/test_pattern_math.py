"""Pure-Python checks for the v0.6 continuous pleat pattern."""

from dataclasses import dataclass
import importlib.util
import math
from pathlib import Path
import sys
import types


class Vector:
    def __init__(self, values):
        self.x, self.y, self.z = map(float, values)

    def __add__(self, other):
        return Vector((self.x + other.x, self.y + other.y, self.z + other.z))

    def __sub__(self, other):
        return Vector((self.x - other.x, self.y - other.y, self.z - other.z))

    def __mul__(self, value):
        return Vector((self.x * value, self.y * value, self.z * value))

    __rmul__ = __mul__

    @property
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalized(self):
        length = self.length or 1.0
        return Vector((self.x / length, self.y / length, self.z / length))


mathutils = types.ModuleType('mathutils')
mathutils.Vector = Vector
sys.modules['mathutils'] = mathutils

ROOT = Path(__file__).resolve().parents[1]
PATTERN_PATH = ROOT / 'real_uniform_generator' / 'pattern.py'
spec = importlib.util.spec_from_file_location('rug_pattern_test_module', PATTERN_PATH)
pattern = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = pattern
spec.loader.exec_module(pattern)


@dataclass
class Settings:
    waist_circumference: float = 0.68
    hip_circumference: float = 0.92
    body_depth_ratio: float = 0.78
    skirt_length: float = 0.48
    hip_line: float = 0.18
    hem_ease: float = 0.04
    back_drop: float = 0.006
    wrinkle_strength: float = 0.0015
    pleat_count: int = 20
    pleat_depth: float = 0.028
    pleat_stitch_length: float = 0.105
    pleat_release_length: float = 0.055
    fabric_thickness: float = 0.00125
    texture_tile_cm: float = 10.0
    zipper_position: str = 'LEFT'


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def run():
    settings = Settings()
    expected_columns = settings.pleat_count * len(pattern.PLEAT_COLUMNS) + 1
    waist = pattern.build_row(settings, 0.0)
    hip = pattern.build_row(settings, settings.hip_line / settings.skirt_length)
    hem = pattern.build_row(settings, 1.0)

    for row_name, row in (('waist', waist), ('hip', hip), ('hem', hem)):
        assert_true(len(row) == expected_columns, f'Unexpected {row_name} row size')
        u_values = [entry['uv'][0] for entry in row]
        assert_true(all(b >= a for a, b in zip(u_values, u_values[1:])), f'{row_name} UV distance is not monotonic')
        roles = {entry['role'] for entry in row}
        required = {'visible_start', 'visible_panel', 'knife_edge', 'underfold_return', 'underfold_panel', 'forward_fold', 'seam'}
        assert_true(required <= roles, f'{row_name} missing roles: {required - roles}')

    seam_gap = (waist[0]['point'] - waist[-1]['point']).length
    assert_true(seam_gap < 1e-7, f'Seam does not close geometrically: {seam_gap}')
    assert_true(abs(waist[0]['uv'][1] - 4.8) < 1e-6, 'Physical UV scale does not map 48 cm to V=4.8 at 10 cm tile size')

    waist_depth = pattern.fold_depth(settings, 0.0)
    hem_depth = pattern.fold_depth(settings, 1.0)
    assert_true(hem_depth > waist_depth * 5.0, 'Pleats do not release below stitch-down')
    assert_true(hem_depth < settings.pleat_depth, 'Flat underfold depth was not projected into the worn radial depth')

    waist_axes = pattern.body_axes(settings, 0.0)
    hip_axes = pattern.body_axes(settings, settings.hip_line / settings.skirt_length)
    hem_axes = pattern.body_axes(settings, 1.0)
    assert_true(hip_axes[0] > waist_axes[0] and hip_axes[1] > waist_axes[1], 'Hip did not grow from waist')
    assert_true(hem_axes[0] >= hip_axes[0], 'Hem is narrower than hip')

    seam_positions = set()
    for position in ('LEFT', 'BACK', 'RIGHT'):
        settings.zipper_position = position
        seam_positions.add(round(pattern.zipper_u(settings), 3))
    assert_true(len(seam_positions) == 3, 'Zipper positions are not distinct')

    print('RUG_PATTERN_TEST_OK')
    print(f'Columns per row: {expected_columns}')
    print(f'Fold depth: waist={waist_depth:.6f}m hem={hem_depth:.6f}m')


if __name__ == '__main__':
    run()
