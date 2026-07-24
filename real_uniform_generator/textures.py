import math

import bpy


IMAGE_PREFIX = 'RUG_Fabric'


def _preset(settings):
    presets = {
        'WINTER_NAVY': {
            'dark': (0.010, 0.018, 0.042),
            'light': (0.026, 0.048, 0.094),
            'roughness': 0.82,
        },
        'SUMMER_NAVY': {
            'dark': (0.014, 0.028, 0.066),
            'light': (0.040, 0.075, 0.140),
            'roughness': 0.70,
        },
        'CHARCOAL': {
            'dark': (0.022, 0.026, 0.034),
            'light': (0.078, 0.084, 0.098),
            'roughness': 0.79,
        },
        'BLACK': {
            'dark': (0.006, 0.007, 0.010),
            'light': (0.032, 0.036, 0.044),
            'roughness': 0.76,
        },
    }
    return presets[settings.fabric]


def _replace_image(name, width, height, colorspace):
    existing = bpy.data.images.get(name)
    if existing is not None:
        bpy.data.images.remove(existing)
    image = bpy.data.images.new(name, width=width, height=height, alpha=True, float_buffer=False)
    try:
        image.colorspace_settings.name = colorspace
    except TypeError:
        pass
    return image


def _set_pixels(image, array):
    flat = array.astype('float32', copy=False).ravel()
    image.pixels.foreach_set(flat)
    image.update()
    image.pack()


def generate_fabric_textures(settings):
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError('Blender付属のNumPyを読み込めませんでした') from exc

    size = int(settings.texture_resolution)
    preset = _preset(settings)
    y, x = np.indices((size, size), dtype=np.float32)
    u = x / max(1.0, size - 1.0)
    v = y / max(1.0, size - 1.0)

    thread_x = max(28.0, min(size * 0.31, settings.weave_scale * 0.48))
    thread_y = max(26.0, min(size * 0.29, settings.weave_scale * 0.44))

    warp = np.sin(u * math.tau * thread_x + 0.18 * np.sin(v * math.tau * 5.0))
    weft = np.sin(v * math.tau * thread_y + 0.16 * np.sin(u * math.tau * 4.0))
    twill = np.sin((u * 0.92 + v) * math.tau * (thread_x * 0.33))
    weave = warp * weft

    macro = (
        0.52 * np.sin(u * math.tau * 2.0 + v * 1.3)
        + 0.31 * np.sin(v * math.tau * 3.0 - u * 2.1)
        + 0.17 * np.sin((u + v) * math.tau * 7.0)
    )
    micro = np.sin(u * math.tau * (thread_x * 1.8) + 0.7) * np.sin(v * math.tau * (thread_y * 1.65))

    dark = np.asarray(preset['dark'], dtype=np.float32)
    light = np.asarray(preset['light'], dtype=np.float32)
    color_factor = np.clip(0.34 + macro * 0.065 + weave * 0.022 + twill * 0.012, 0.0, 1.0)
    rgb = dark[None, None, :] * (1.0 - color_factor[:, :, None]) + light[None, None, :] * color_factor[:, :, None]
    alpha = np.ones((size, size, 1), dtype=np.float32)
    base_rgba = np.concatenate((np.clip(rgb, 0.0, 1.0), alpha), axis=2)

    roughness = np.clip(
        preset['roughness'] + macro * 0.035 - weave * 0.018 + micro * 0.010,
        0.40,
        0.98,
    )
    rough_rgba = np.stack((roughness, roughness, roughness, np.ones_like(roughness)), axis=2)

    height = weave * 0.58 + twill * 0.22 + micro * 0.12 + macro * 0.08
    grad_y, grad_x = np.gradient(height)
    normal_strength = 0.85 + settings.weave_strength * 7.0
    nx = -grad_x * normal_strength
    ny = -grad_y * normal_strength
    nz = np.ones_like(nx)
    length = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx /= length
    ny /= length
    nz /= length
    normal_rgba = np.stack(
        (nx * 0.5 + 0.5, ny * 0.5 + 0.5, nz * 0.5 + 0.5, np.ones_like(nx)),
        axis=2,
    )

    suffix = f'{settings.fabric}_{size}'
    base_image = _replace_image(f'{IMAGE_PREFIX}_BaseColor_{suffix}', size, size, 'sRGB')
    rough_image = _replace_image(f'{IMAGE_PREFIX}_Roughness_{suffix}', size, size, 'Non-Color')
    normal_image = _replace_image(f'{IMAGE_PREFIX}_Normal_{suffix}', size, size, 'Non-Color')

    _set_pixels(base_image, base_rgba)
    _set_pixels(rough_image, rough_rgba)
    _set_pixels(normal_image, normal_rgba)

    base_image['rug_map_type'] = 'base_color'
    rough_image['rug_map_type'] = 'roughness'
    normal_image['rug_map_type'] = 'normal'
    return {
        'base_color': base_image,
        'roughness': rough_image,
        'normal': normal_image,
    }
