"""Pure-Python checks for the v0.5 continuous pleat pattern.

This test injects a minimal ``mathutils.Vector`` substitute so it can run in
normal CPython as part of GitHub Actions. Blender runtime tests cover bpy.
"""

from dataclasses import dataclass
import base64
import binascii
import io
import math
from pathlib import Path
import re
import sys
import types
from zipfile import BadZipFile, ZipFile


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

_BASE64_FRAGMENT = re.compile(r'[A-Za-z0-9+/=]+')
_BASE64_INVALID = re.compile(r'[^A-Za-z0-9+/=]+')


def _pad_base64(value: str) -> str:
    return value + '=' * (-len(value) % 4)


def encoded_candidates(path: Path):
    raw = path.read_text(encoding='utf-8-sig')
    compact = ''.join(raw.split())
    if not compact:
        raise RuntimeError(f'Runtime payload is empty: {path}')

    seen = set()
    values = [
        ('normalised', compact),
        ('urlsafe-normalised', compact.translate(str.maketrans('-_', '+/'))),
        ('non-base64-filtered', _BASE64_INVALID.sub('', compact)),
        (
            'long-fragments',
            ''.join(
                fragment
                for fragment in _BASE64_FRAGMENT.findall(compact)
                if len(fragment) >= 24
            ),
        ),
    ]
    for label, value in values:
        value = _pad_base64(value)
        if value and value not in seen:
            seen.add(value)
            yield label, value


def read_pattern_source(path: Path) -> str:
    errors = []
    for label, encoded in encoded_candidates(path):
        try:
            payload = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            errors.append(f'{label}: Base64: {exc}')
            continue

        try:
            with ZipFile(io.BytesIO(payload)) as archive:
                bad_member = archive.testzip()
                if bad_member is not None:
                    raise RuntimeError(f'corrupt member: {bad_member}')
                source = archive.read('pattern.py').decode('utf-8-sig')
                compile(source, f'{path}!/pattern.py', 'exec')
                print(f'Runtime payload recovery mode: {label}')
                return source
        except (BadZipFile, KeyError, UnicodeDecodeError, RuntimeError, SyntaxError) as exc:
            errors.append(f'{label}: ZIP: {type(exc).__name__}: {exc}')

    raise RuntimeError('Runtime payload recovery failed: ' + ' | '.join(errors))


ROOT = Path(__file__).resolve().parents[1]
payload_path = ROOT / 'real_uniform_generator' / 'v05_runtime_payload.b64'
source = read_pattern_source(payload_path)

pattern = types.ModuleType('rug_pattern_test_module')
pattern.__file__ = f'{payload_path}!/pattern.py'
sys.modules[pattern.__name__] = pattern
exec(compile(source, pattern.__file__, 'exec'), pattern.__dict__)


@dataclass
class Settings:
    waist_circumference: float = 0.68
    hip_circumference: float = 0.92
    body_depth_ratio: float = 0.76
    skirt_length: float = 0.48
    hip_line: float = 0.18
    hem_ease: float = 0.055
    back_drop: float = 0.006
    wrinkle_strength: float = 0.0018
    pleat_count: int = 20
    pleat_depth: float = 0.028
    pleat_stitch_length: float = 0.105
    pleat_release_length: float = 0.055
    fabric_thickness: float = 0.00125
    texture_repeat_cm: float = 10.0
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

    assert_true(len(waist) == expected_columns, 'Unexpected waist row size')
    assert_true(len(hip) == expected_columns, 'Unexpected hip row size')
    assert_true(len(hem) == expected_columns, 'Unexpected hem row size')

    seam_gap = (waist[0]['point'] - waist[-1]['point']).length
    assert_true(seam_gap < 1e-7, f'Seam does not close geometrically: {seam_gap}')

    for row_name, row in (('waist', waist), ('hip', hip), ('hem', hem)):
        u_values = [entry['uv'][0] for entry in row]
        assert_true(
            all(b >= a for a, b in zip(u_values, u_values[1:])),
            f'{row_name} flat-cloth UV distance is not monotonic',
        )
        roles = {entry['role'] for entry in row}
        required = {
            'visible_start', 'visible_panel', 'knife_edge',
            'underfold_return', 'underfold_panel', 'forward_fold', 'seam',
        }
        assert_true(required <= roles, f'{row_name} is missing pleat roles: {required - roles}')

    waist_depth = pattern.fold_depth(settings, 0.0)
    hem_depth = pattern.fold_depth(settings, 1.0)
    assert_true(hem_depth > waist_depth * 5.0, 'Pleats do not release below stitch-down')

    waist_axes = pattern.body_axes(settings, 0.0)
    hip_axes = pattern.body_axes(settings, settings.hip_line / settings.skirt_length)
    hem_axes = pattern.body_axes(settings, 1.0)
    assert_true(hip_axes[0] > waist_axes[0], 'Hip width did not grow from waist')
    assert_true(hip_axes[1] > waist_axes[1], 'Hip depth did not grow from waist')
    assert_true(hem_axes[0] >= hip_axes[0], 'Hem width is narrower than hip')

    seam_positions = set()
    for position in ('LEFT', 'BACK', 'RIGHT'):
        settings.zipper_position = position
        seam_positions.add(round(pattern.zipper_u(settings), 3))
    assert_true(len(seam_positions) == 3, 'Zipper seam positions are not distinct')

    print('RUG_PATTERN_TEST_OK')
    print(f'Columns per row: {expected_columns}')
    print(f'Fold depth: waist={waist_depth:.6f}m hem={hem_depth:.6f}m')


if __name__ == '__main__':
    run()
