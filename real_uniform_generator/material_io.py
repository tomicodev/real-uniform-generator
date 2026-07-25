from __future__ import annotations

from pathlib import Path
import re
import bpy

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.tga', '.exr', '.bmp', '.webp'}
TOKENS = {
    'base_color': ('basecolor', 'base_color', 'albedo', 'diffuse', 'color', 'colour'),
    'roughness': ('roughness', 'rough', 'rgh'),
    'normal_gl': ('normalgl', 'normal_gl', 'opengl', 'normal'),
    'normal_dx': ('normaldx', 'normal_dx', 'directx'),
    'height': ('height', 'displacement', 'disp', 'bump'),
    'ao': ('ambientocclusion', 'ambient_occlusion', 'occlusion', 'ao'),
}
NEGATIVE = {
    'base_color': ('rough', 'normal', 'height', 'disp', 'bump', 'ao', 'metal'),
    'roughness': ('normal', 'height', 'basecolor', 'albedo', 'diffuse'),
    'normal_gl': ('rough', 'height', 'basecolor', 'albedo', 'diffuse', 'directx', 'normaldx'),
    'normal_dx': ('rough', 'height', 'basecolor', 'albedo', 'diffuse', 'opengl', 'normalgl'),
    'height': ('normal', 'rough', 'basecolor', 'albedo', 'diffuse'),
    'ao': ('normal', 'rough', 'height', 'basecolor', 'albedo', 'diffuse'),
}


def _name(path):
    return re.sub(r'[^a-z0-9]+', '_', path.stem.lower()).strip('_')


def _score(path, map_type):
    name = _name(path)
    score = 0
    for token in TOKENS[map_type]:
        normalized = re.sub(r'[^a-z0-9]+', '_', token).strip('_')
        if normalized in name:
            score += 20 + len(normalized)
    for token in NEGATIVE.get(map_type, ()):
        if token in name:
            score -= 28
    if path.suffix.lower() in {'.png', '.tif', '.tiff', '.exr'}:
        score += 3
    return score


def _candidate_files(root):
    files = [p for p in root.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
    for child in root.iterdir():
        if child.is_dir():
            files.extend(p for p in child.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS)
    return files


def find_pbr_files(directory):
    root = Path(bpy.path.abspath(directory))
    if not root.exists() or not root.is_dir():
        raise RuntimeError(f'PBRフォルダが見つかりません: {root}')
    candidates = _candidate_files(root)
    if not candidates:
        raise RuntimeError(f'画像ファイルがありません: {root}')
    result = {}
    for map_type in TOKENS:
        ranked = sorted(((_score(path, map_type), path) for path in candidates), key=lambda item: (item[0], -len(str(item[1]))), reverse=True)
        if ranked and ranked[0][0] > 0:
            result[map_type] = ranked[0][1]
    if 'base_color' not in result:
        raise RuntimeError('Base Color画像を判定できません。BaseColor / Albedo / Diffuseをファイル名へ含めてください。')
    return result


def _load(path, colorspace, pack, map_type):
    image = bpy.data.images.load(str(path.resolve()), check_existing=True)
    try:
        image.colorspace_settings.name = colorspace
    except Exception:
        pass
    if pack and image.packed_file is None:
        image.pack()
    image['rug_map_type'] = map_type
    image['rug_source_path'] = str(path.resolve())
    return image


def load_external_pbr(settings):
    files = find_pbr_files(settings.texture_directory)
    maps = {'base_color': _load(files['base_color'], 'sRGB', settings.pack_external_textures, 'base_color')}
    for key in ('roughness', 'height', 'ao'):
        if key in files:
            maps[key] = _load(files[key], 'Non-Color', settings.pack_external_textures, key)
    requested = settings.normal_format
    normal_key = None
    if requested == 'OPENGL':
        normal_key = 'normal_gl' if 'normal_gl' in files else None
    elif requested == 'DIRECTX':
        normal_key = 'normal_dx' if 'normal_dx' in files else None
    else:
        normal_key = 'normal_gl' if 'normal_gl' in files else ('normal_dx' if 'normal_dx' in files else None)
    if normal_key:
        maps['normal'] = _load(files[normal_key], 'Non-Color', settings.pack_external_textures, normal_key)
        maps['_normal_directx'] = normal_key == 'normal_dx'
    else:
        maps['_normal_directx'] = False
    return maps, files
