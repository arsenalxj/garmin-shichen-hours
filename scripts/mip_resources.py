"""为 FR255 生成 64 色预混色字形和圆环；普通机型继续使用原绘制路径。"""
import argparse
import base64
import json
import math
from functools import lru_cache
from pathlib import Path

from project import ROOT, THEMES, venv, write

venv()
from PIL import Image, ImageChops, ImageDraw
import generate_resources as gen

SIZE = 260
SCALE = SIZE / 466
SAMPLES = 8
FONT_NAMES = ['Ring', 'RingActive', 'Caption', 'Date', 'Time', 'TimeSleep', 'Metric']
# 灰阶覆盖保留下来后，小字可以恢复中等字重，避免细笔画只剩浅色边缘。
WEIGHTS = {'Ring': 400, 'RingActive': 400, 'Caption': 400, 'Date': 400,
           'Metric': 400, 'TimeSans': 350, 'TimeSansSleep': 300}


def channel(value):
    return min(255, max(0, 85 * gen.rounded(value / 85)))


def rgb(value):
    return gen.rgb(value) if isinstance(value, str) else (
        (value >> 16) & 255, (value >> 8) & 255, value & 255)


def number(value):
    r, g, b = rgb(value)
    return (r << 16) | (g << 8) | b


def dim(value, factor):
    r, g, b = (gen.rounded(v * factor) for v in rgb(value))
    return (r << 16) | (g << 8) | b


def palette(value):
    return tuple(channel(v) for v in rgb(value))


def quantize(image):
    return image.point([channel(v) for v in range(256)] * 3)


@lru_cache(maxsize=None)
def font(name, serif=False):
    actual = name.replace('Time', 'TimeSerif' if serif else 'TimeSans') if name.startswith('Time') else name
    spec = list(next(s for s in gen.FONTS if s[0] == actual))
    spec[2] = WEIGHTS.get(actual, spec[2])
    return gen.render_font(tuple(spec), SIZE)


def preblend(mask, foreground, background):
    """只保留透明/不透明，RGB 已包含对真实背景的边缘覆盖，不依赖设备 alpha 混合。"""
    fg, bg = palette(foreground), palette(background)
    channels = [mask.point([channel((a * v + b * (255 - v)) / 255) for v in range(256)])
                for a, b in zip(fg, bg)]
    return Image.merge('RGBA', (*channels, mask.point(lambda v: 255 if v else 0)))


def paint_text(image, name, value, x, baseline, foreground, serif=False):
    sheet, glyphs, base, _ = font(name, serif)
    by_char = {g[0]: g for g in glyphs}
    pen = gen.rounded(x * SCALE) - gen.rounded(sum(by_char[c][7] for c in value) / 2)
    top = gen.rounded(baseline * SCALE) - base
    for char in value:
        _, gx, gy, width, height, xo, yo, advance = by_char[char]
        mask = sheet.crop((gx, gy, gx + width, gy + height)).getchannel('A')
        image.paste(palette(foreground), (pen + xo, top + yo, pen + xo + width, top + yo + height), mask)
        pen += advance


def render_ring(theme, current, sleeping):
    """在连续圆弧上采样，再缩到 260px；时辰字在最终像素网格排版。"""
    factor = theme['dim'] if sleeping else 1
    tone = lambda key: dim(theme[key], factor)
    image = Image.new('RGB', (SIZE * SAMPLES, SIZE * SAMPLES), 'black')
    draw = ImageDraw.Draw(image)
    cx = SIZE * SAMPLES / 2
    scale = SCALE * SAMPLES
    outer = 230 * scale
    draw.ellipse((cx - outer, cx - outer, cx + outer, cx + outer),
                 fill=palette(tone('aodFace' if sleeping else 'face')))
    if theme['rimOn'] and not sleeping:
        radius = 228.5 * scale
        blend = tuple(gen.rounded((a + b) / 2) for a, b in zip(rgb(theme['rim']), rgb(theme['face'])))
        draw.ellipse((cx - radius, cx - radius, cx + radius, cx + radius),
                     outline=tuple(channel(v) for v in blend), width=gen.rounded(2 * SCALE) * SAMPLES)
    for index in range(12):
        active = index == current
        if sleeping and not active:
            continue
        inner = (158 if active else 174) * scale
        angles = [math.radians(-103.9 + 30 * index + 27.8 * j / 112) for j in range(113)]
        points = [(cx + outer * math.cos(a), cx + outer * math.sin(a)) for a in angles]
        points += [(cx + inner * math.cos(a), cx + inner * math.sin(a)) for a in reversed(angles)]
        fill = dim(gen.HOUR_COLORS[index], factor) if theme['cycle'] else tone('current' if active else 'segment')
        if sleeping:
            draw.line(points + points[:1], fill=palette(fill), width=gen.rounded(3 * SCALE) * SAMPLES, joint='curve')
        else:
            draw.polygon(points, fill=palette(fill))
    image = image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    for index, char in enumerate(gen.BRANCHES):
        active = index == current
        if theme['cycle']:
            ink = dim(gen.HOUR_COLORS[index], factor) if sleeping else number(gen.HOUR_INKS[index])
        else:
            ink = tone(('current' if sleeping else 'currentText') if active else 'segmentText')
        angle = math.radians(-90 + index * 30)
        paint_text(image, 'RingActive' if active else 'Ring', char,
                   233 + 202 * math.cos(angle), 244 + 202 * math.sin(angle), ink)
    return quantize(image)


def font_inks(theme, index, sleeping):
    factor = theme['dim'] if sleeping else 1
    if index == 2:
        return list(dict.fromkeys(dim(c, factor) for c in
                    (gen.HOUR_COLORS if theme['cycle'] else [theme['current']])))
    if index == 3:
        return [dim(theme['aodDate' if sleeping else 'date'], factor)]
    if index == 4 and not sleeping:
        return [number(theme['time'])]
    if index == 5 and sleeping:
        return [dim(theme['aodTime'], factor)]
    if index == 6 and not sleeping:
        return list(dict.fromkeys([number(theme['meta']), 0xD92121]))
    return []


def generate_theme(name, theme):
    target = ROOT / name / 'resources/fr255-raster'
    target.mkdir(parents=True, exist_ok=True)
    entries, faces, patches, atlases = [], [], [], []
    specs = [None, None]
    metadata = {'size': SIZE, 'faces': [], 'patches': [], 'fonts': {}, 'atlases': []}

    def bitmap(identifier, image):
        image.save(target / f'{identifier}.png')
        entries.append(f'  <bitmap id="{identifier}" filename="{identifier}.png" dithering="none" compress="true"/>')
        return 'Rez.Drawables.' + identifier

    for index in range(2, 7):
        _, glyphs, base, height = font(FONT_NAMES[index], theme['serif'])
        specs.append([base, {ord(g[0]): list(g[1:]) for g in glyphs}])
        metadata['fonts'][str(index)] = {'base': base, 'height': height, 'glyphs': specs[-1][1]}
    for sleeping in (False, True):
        mode = int(sleeping)
        base_name = f'MipFace{mode}'
        base = render_ring(theme, None, sleeping)
        faces.append(bitmap(base_name, base))
        metadata['faces'].append(base_name)
        mode_patches = []
        for current in range(12):
            scene = render_ring(theme, current, sleeping)
            box = ImageChops.difference(base, scene).getbbox()
            if box is None:
                raise ValueError(f'{name}: {current} 时辰没有高亮变化')
            identifier = f'MipHour{mode}_{current}'
            resource = bitmap(identifier, scene.crop(box))
            mode_patches.append([resource, box[0], box[1]])
            metadata['patches'].append({'mode': mode, 'hour': current, 'id': identifier, 'box': box})
        patches.append(mode_patches)
        variants = [[], []]
        background = dim(theme['aodFace' if sleeping else 'face'], theme['dim'] if sleeping else 1)
        for index in range(2, 7):
            sheet, _, _, _ = font(FONT_NAMES[index], theme['serif'])
            ink_variants = []
            for v, ink in enumerate(font_inks(theme, index, sleeping)):
                identifier = f'MipFont{mode}_{index}_{v}'
                baked = preblend(sheet.getchannel('A'), ink, background)
                ink_variants.append([ink, bitmap(identifier, baked)])
                metadata['atlases'].append({'mode': mode, 'font': index, 'ink': ink,
                                           'background': background, 'id': identifier})
            variants.append(ink_variants)
        atlases.append(variants)

    def mc(value):
        if value is None:
            return 'null'
        if isinstance(value, str):
            return value  # 这里只传入已生成的资源符号。
        if isinstance(value, dict):
            return '{' + ', '.join(f'{k} => {mc(v)}' for k, v in value.items()) + '}'
        if isinstance(value, list):
            return '[' + ', '.join(mc(v) for v in value) + ']'
        return str(value)

    write(target / 'drawables.xml', '<resources>\n' + '\n'.join(entries) + '\n</resources>\n')
    write(target / 'raster.json', json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    source = '// 由 scripts/mip_resources.py 生成，仅 FR255 标准版使用。\nmodule RasterAssets {\n    const ENABLED = true;\n'
    for key, value in [('FACES', faces), ('PATCHES', patches), ('FONTS', specs), ('ATLASES', atlases)]:
        source += f'    const {key} = {mc(value)};\n'
    write(ROOT / f'shared/generated/fr255/{name}/RasterAssets.mc', source + '}\n')


def generate():
    write(ROOT / 'shared/generated/raster-default/RasterAssets.mc',
          '// 普通设备沿用原绘制路径。\nmodule RasterAssets {\n    const ENABLED = false;\n'
          '    const FACES = [];\n    const PATCHES = [];\n    const FONTS = [];\n    const ATLASES = [];\n}\n')
    for name, theme in THEMES.items():
        generate_theme(name, theme)
    generate_prototype_assets()


def generate_prototype_assets():
    """网页复用实际打包资源，内嵌 PNG 以支持直接打开本地 HTML 和离线导出。"""
    bundle = {}
    for name in THEMES:
        target = ROOT / name / 'resources/fr255-raster'
        assets = json.loads((target / 'raster.json').read_text())
        identifiers = assets['faces'] + [p['id'] for p in assets['patches']] + [a['id'] for a in assets['atlases']]
        assets['images'] = {}
        for identifier in identifiers:
            path = target / (identifier + '.png')
            with Image.open(path) as image:
                width, height = image.size
            assets['images'][identifier] = {
                'width': width, 'height': height,
                'uri': 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode('ascii'),
            }
        bundle[name] = assets
    write(ROOT / 'designs/shichen-watchface/fr255-raster.js',
          '// 由 scripts/mip_resources.py 从正式 FR255 资源生成，请勿手工修改。\n'
          'window.FR255_RASTER = ' + json.dumps(bundle, ensure_ascii=False, separators=(',', ':')) + ';\n')


def verify():
    """读实际产物验证，覆盖所有时辰和睡眠背景，并检查位图中真实的过渡色。"""
    scenes = antialiased = 0
    for name, theme in THEMES.items():
        target = ROOT / name / 'resources/fr255-raster'
        data = json.loads((target / 'raster.json').read_text())
        for item in data['patches']:
            base = Image.open(target / (data['faces'][item['mode']] + '.png')).convert('RGB')
            patch = Image.open(target / (item['id'] + '.png')).convert('RGB')
            box = item['box']
            assert patch.size == (box[2] - box[0], box[3] - box[1]), item
            base.paste(patch, box[:2])
            expected = render_ring(theme, item['hour'], bool(item['mode']))
            assert ImageChops.difference(base, expected).getbbox() is None, item
            assert all(c % 85 == 0 for color in base.getdata() for c in color), item
            scenes += 1
        for item in data['atlases']:
            atlas = Image.open(target / (item['id'] + '.png')).convert('RGBA')
            assert set(atlas.getchannel('A').getdata()) <= {0, 255}, item
            assert all(c % 85 == 0 for pixel in atlas.getdata() for c in pixel[:3]), item
            specs = data['fonts'][str(item['font'])]
            expected_chars = font(FONT_NAMES[item['font']], theme['serif'])[1]
            assert set(specs['glyphs']) == {str(ord(g[0])) for g in expected_chars}, item
            fg, bg = palette(item['ink']), palette(item['background'])
            for glyph in specs['glyphs'].values():
                x, y, w, h, xo, yo, advance = glyph
                assert 0 <= x < x+w <= atlas.width and 0 <= y < y+h <= atlas.height, glyph
                assert advance > 0 and yo >= 0, glyph
                colors = {p[:3] for p in atlas.crop((x, y, x+w, y+h)).getdata() if p[3]}
                if colors - {fg, bg}:
                    antialiased += 1
            if item['font'] in (4, 5):
                # 大数字必须实际拥有中间色，防止再次被导出成黑白硬边。
                assert any(p[3] and p[:3] not in (fg, bg) for p in atlas.getdata()), item
    return {'themes': len(THEMES), 'scenes': scenes, 'antialiased_glyphs': antialiased}


def preview_pixels(name, scene):
    """由已打包资源合成固定场景，供原生截图逐像素核对坐标和裁剪行为。"""
    target = ROOT / name / 'resources/fr255-raster'
    assets = json.loads((target / 'raster.json').read_text())
    sample = json.loads((ROOT / 'tests/scenes.json').read_text())[scene]
    theme = THEMES[name]
    sleeping = sample.get('sleeping', False)
    if sleeping and sample.get('protected', False):
        return Image.new('RGB', (SIZE, SIZE), 'black')
    mode = int(sleeping)
    hour, minute = sample.get('hour', 23), sample.get('minute', 45)
    current = ((hour + 1) // 2) % 12
    quarter = ((hour * 60 + minute + 60) % 120) // 15
    image = Image.open(target / (assets['faces'][mode] + '.png')).convert('RGB')
    patch = next(p for p in assets['patches'] if p['mode'] == mode and p['hour'] == current)
    image.paste(Image.open(target / (patch['id'] + '.png')), patch['box'][:2])

    def text(index, value, x, baseline, ink, align='center'):
        spec = assets['fonts'][str(index)]
        variant = next(a for a in assets['atlases'] if a['mode'] == mode and a['font'] == index and a['ink'] == ink)
        atlas = Image.open(target / (variant['id'] + '.png')).convert('RGBA')
        glyphs = [spec['glyphs'][str(ord(c))] for c in value]
        width = sum(g[6] for g in glyphs)
        pen = gen.rounded(x * SCALE) - (gen.rounded(width / 2) if align == 'center' else width if align == 'right' else 0)
        top = gen.rounded(baseline * SCALE) - spec['base']
        for gx, gy, w, h, xo, yo, advance in glyphs:
            glyph = atlas.crop((gx, gy, gx+w, gy+h))
            image.paste(glyph, (pen+xo, top+yo), glyph)
            pen += advance

    factor = theme['dim'] if sleeping else 1
    accent = dim(gen.HOUR_COLORS[current] if theme['cycle'] else theme['current'], factor)
    text(2, gen.BRANCHES[current] + '时 · ' + '初一二三四五六七'[quarter] + '刻', 233, 131, accent)
    text(3, f"09/{sample.get('day', 21):02d} 周" + '日一二三四五六'[sample.get('dayOfWeek', 2)-1],
         233, 170, dim(theme['aodDate' if sleeping else 'date'], factor))
    text(5 if sleeping else 4, f'{hour:02d}:{minute:02d}', 233, 268,
         dim(theme['aodTime' if sleeping else 'time'], factor))
    if not sleeping:
        x, y, w, h = (gen.rounded(v * SCALE) for v in (209, 281, 48, 4))
        ImageDraw.Draw(image).rectangle((x, y, x+w-1, y+h-1), fill=palette(accent))
        battery = sample.get('battery', 86)
        for value, x, align, ink in [
            (battery, 157, 'right', 0xD92121 if battery <= 20 else number(theme['meta'])),
            ('｜', 173, 'center', number(theme['meta'])),
            (sample.get('steps', 12860), 233, 'center', number(theme['meta'])),
            ('｜', 293, 'center', number(theme['meta'])),
            (sample.get('heartRate', 72), 309, 'left', number(theme['meta'])),
        ]:
            text(6, '--' if value is None else str(value), x, 328, ink, align)
    return image


def verify_capture(path, theme, scene):
    actual = Image.open(path).convert('RGB')
    expected = preview_pixels(theme, scene)
    assert actual.size == expected.size, '必须使用模拟器保存的原始 260px 截图'
    difference = ImageChops.difference(actual, expected)
    count = sum(pixel != (0, 0, 0) for pixel in difference.getdata())
    result = {'theme': theme, 'scene': scene, 'different_pixels': count, 'bounds': difference.getbbox()}
    if count:
        expected.save(Path(path).with_name(Path(path).stem + '-expected.png'))
        difference.save(Path(path).with_name(Path(path).stem + '-diff.png'))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--prototype-only', action='store_true', help='仅从现有正式资源同步网页像素资源')
    parser.add_argument('--verify-capture', type=Path)
    parser.add_argument('--theme', choices=THEMES)
    parser.add_argument('--scene', default='normal')
    args = parser.parse_args()
    if args.verify_capture:
        if not args.theme:
            parser.error('--verify-capture 需要 --theme')
        result = verify_capture(args.verify_capture, args.theme, args.scene)
        print(json.dumps(result))
        raise SystemExit(1 if result['different_pixels'] else 0)
    elif args.verify:
        print(json.dumps(verify()))
    elif args.prototype_only:
        generate_prototype_assets()
        print('已同步 FR255 原型像素资源。')
    else:
        generate()
        print('已生成 FR255 标准版的三个主题资源。')
