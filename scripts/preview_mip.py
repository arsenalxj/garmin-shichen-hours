"""按 MIP 机型的真实规则模拟表盘：图集二值化后，在设备像素上按 HourView.mc 的布局合成。

浏览器预览和导出的 PNG 都是抗锯齿的，看不出 1 位屏上的实际观感。这里把字体图集按
--cutoff 二值化再合成，字号、基线、锚点、扇环都与 HourView.mc 一致，只差分区配色没做
64 色抖动（画的是纯色），所以图上能判断的就是文字与布局。

两种取图集的方式：
  默认走 generate_resources 的渲染路径，可以扫任意切点，用来选值；
  --atlas 直接读 shared/resources/<size>/fonts/ 下已生成的那一套，用来验证真正打包进
  应用的图集。

--cutoff 的含义与设备一致：SDK 把 alpha > 0 的像素一律当墨（见 generate_resources 的
MONO_CUTOFF 注释），所以这里也用同一条规则合成，于是
  --cutoff 1    复现设备现状（抗锯齿图集的整个支持域都变成实心）
  --cutoff 64   复现预二值化后的效果，即当前 MONO_CUTOFF
对已经二值化的图集，--cutoff 退化成无操作，因此同一张图在任意切点下都相同，就说明设备
结果不再依赖图集里的灰阶。

例：
  python3 scripts/preview_mip.py --size 260 --cutoff 1 --cutoff 64
  python3 scripts/preview_mip.py --size 260 --atlas --cutoff 64 --sleep
"""
import argparse
import math
import re
from collections import namedtuple

from project import ROOT, THEMES, venv

venv()
from PIL import Image, ImageDraw, ImageFont

import generate_resources as gen

# HourView.mc 的 466 原型坐标系常量，改布局时两处要一起改。
CX = 233.0
RING_Y = 244.0                      # 环上时辰文字的纵向半径中心，比圆心低 11
R_OUT, R_IN, R_IN_ACTIVE, R_TXT = 230.0, 174.0, 158.0, 202.0
CAPTION_Y, DATE_Y, TIME_Y = 131, 170, 268
RULE = (209, 281, 48, 4)            # 强调线 x, y, 宽, 高
METRIC_Y = 328
METRIC_ANCHORS = [(157, 'end'), (173, 'middle'), (233, 'middle'), (293, 'middle'), (309, 'start')]
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
QUARTERS = "初一二三四五六七"
WEEKDAYS = "日一二三四五六"

Atlas = namedtuple('Atlas', 'sheet glyphs base')


def rnd(value):
    return int(math.floor(value + 0.5))


def hour_index(hour):
    return ((hour + 1) // 2) % 12


def quarter_index(hour, minute):
    return (((hour * 60 + minute + 60) % 120) // 15)


def load_size(size):
    available = gen.devices()
    for device in available.values():
        if device['width'] == size:
            return available, device
    raise SystemExit(f'没有分辨率为 {size} 的圆屏设备：{sorted({d["width"] for d in available.values()})}')


RING, RING_ACTIVE, CAPTION, DATE, TIME, TIME_SLEEP, METRIC = range(7)


def load_fonts(size, reference, cutoff, serif):
    """返回 Atlas 列表，下标与 HourView.mc 的 _fonts 一致。"""
    names = ['Ring', 'RingActive', 'Caption', 'Date', 'TimeSerif' if serif else 'TimeSans',
             'TimeSerifSleep' if serif else 'TimeSansSleep', 'Metric']
    fonts = []
    for name in names:
        if reference == 'atlas':
            atlas = read_atlas(size, name)
        else:
            sheet, glyphs, base, _ = gen.render_font(next(f for f in gen.FONTS if f[0] == name), size)
            atlas = Atlas(sheet, glyphs, base)
        # 二值化后再合成：1 位屏上没有灰阶，边缘像素要么是笔画要么消失。
        atlas.sheet.putalpha(atlas.sheet.getchannel('A').point(lambda v: 255 if v >= cutoff else 0))
        fonts.append(atlas)
    return fonts


def read_atlas(size, name):
    target = ROOT / f'shared/resources/{size}/fonts'
    glyphs = []
    for line in (target / f'{name}.fnt').read_text().splitlines():
        if line.startswith('char '):
            field = {k: int(v) for k, v in re.findall(r'(\w+)=(-?\d+)', line)}
            glyphs.append((chr(field['id']), field['x'], field['y'], field['width'], field['height'],
                           field['xoffset'], field['yoffset'], field['xadvance']))
    base = int(re.search(r'common[^\n]*base=(-?\d+)', (target / f'{name}.fnt').read_text()).group(1))
    return Atlas(Image.open(target / f'{name}.png').convert('RGBA'), glyphs, base)


def scale_color(value, dim):
    return tuple(rnd(component * dim) for component in gen.rgb(value))


def draw_text(canvas, atlas, value, anchor, baseline, justify, color, scale):
    """锚点与基线在 466 原型系，要乘 scale；字形表里的 offset 与 advance 已是设备像素。"""
    width = sum(next(g[7] for g in atlas.glyphs if g[0] == c) for c in value)
    pen = rnd(anchor * scale)
    pen = pen - width if justify == 'end' else pen - rnd(width / 2) if justify == 'middle' else pen
    # drawText 的 y 是行顶（基线减 base），字形再按 yoffset 落位。
    top = rnd(baseline * scale) - atlas.base
    for char in value:
        _, x, y, w, h, xoffset, yoffset, advance = next(g for g in atlas.glyphs if g[0] == char)
        ink = Image.new('RGB', (w, h), color)
        ink.putalpha(atlas.sheet.crop((x, y, x + w, y + h)).getchannel('A'))
        canvas.paste(ink, (pen + xoffset, top + yoffset), ink)
        pen += advance


def sector(canvas, index, active, fill, scale, cx):
    inner = R_IN_ACTIVE if active else R_IN
    start = -90.0 + index * 30 - 15 + 1.1
    span = 30.0 - 2.2
    points = []
    for step in range(13):
        angle = math.radians(start + span * step / 12.0)
        points.append((cx + rnd(R_OUT * math.cos(angle) * scale), cx + rnd(R_OUT * math.sin(angle) * scale)))
    for step in range(12, -1, -1):
        angle = math.radians(start + span * step / 12.0)
        points.append((cx + rnd(inner * math.cos(angle) * scale), cx + rnd(inner * math.sin(angle) * scale)))
    ImageDraw.Draw(canvas).polygon(points, fill=fill)


def face(size, theme_name, reference, cutoff, sleeping, sample):
    theme = THEMES[theme_name]
    _, device = load_size(size)
    fonts = load_fonts(size, reference, cutoff, theme['serif'])
    scale = size / 466.0
    cx = size // 2
    dim = theme['dim'] if sleeping else 1.0

    def tone(key):
        return scale_color(theme[key], dim)

    canvas = Image.new('RGB', (size, size), (0, 0, 0))
    current = hour_index(sample['hour'])
    ImageDraw.Draw(canvas).ellipse(
        (cx - rnd(R_OUT * scale), cx - rnd(R_OUT * scale), cx + rnd(R_OUT * scale), cx + rnd(R_OUT * scale)),
        fill=tone('aodFace' if sleeping else 'face'))
    if theme['rimOn'] and not sleeping:
        blend = ''.join(f'{rnd((a + b) / 2):02X}' for a, b in zip(gen.rgb(theme['rim']), gen.rgb(theme['face'])))
        ImageDraw.Draw(canvas).ellipse(
            (cx - rnd(228.5 * scale), cx - rnd(228.5 * scale), cx + rnd(228.5 * scale), cx + rnd(228.5 * scale)),
            outline=scale_color(blend, 1.0), width=max(1, rnd(2 * scale)))
    for index in range(12):
        active = index == current
        if theme['cycle']:
            fill = scale_color(gen.HOUR_COLORS[index], dim)
            ink = scale_color(gen.HOUR_COLORS[index], dim) if sleeping else scale_color(gen.HOUR_INKS[index], 1.0)
        else:
            fill = tone('current' if active else 'segment')
            ink = tone('current' if active and sleeping else 'currentText' if active else 'segmentText')
        if not sleeping or active:
            sector(canvas, index, active, fill, scale, cx)
        angle = math.radians(-90 + index * 30)
        draw_text(canvas, fonts[RING_ACTIVE if active else RING], BRANCHES[index],
                  CX + R_TXT * math.cos(angle), RING_Y + R_TXT * math.sin(angle), 'middle', ink, scale)
    accent = tone(theme['current']) if not theme['cycle'] else scale_color(gen.HOUR_COLORS[current], dim)
    col_time = tone('aodTime' if sleeping else 'time')
    col_date = tone('aodDate' if sleeping else 'date')
    col_meta = tone('aodMeta' if sleeping else 'meta')
    caption = BRANCHES[current] + '时 · ' + QUARTERS[quarter_index(sample['hour'], sample['minute'])] + '刻'
    clock = f"{sample['hour']:02d}:{sample['minute']:02d}"
    draw_text(canvas, fonts[CAPTION], caption, CX, CAPTION_Y, 'middle', accent, scale)
    draw_text(canvas, fonts[DATE], sample['date'], CX, DATE_Y, 'middle', col_date, scale)
    draw_text(canvas, fonts[TIME_SLEEP if sleeping else TIME], clock, CX, TIME_Y, 'middle', col_time, scale)
    if not sleeping:
        x, y, w, h = RULE
        ImageDraw.Draw(canvas).rectangle((rnd(x * scale), rnd(y * scale), rnd((x + w) * scale), rnd((y + h) * scale)), fill=accent)
        values = [str(sample['battery']), '｜', str(sample['steps']), '｜', str(sample['heart'])]
        for value, (anchor, justify) in zip(values, METRIC_ANCHORS):
            color = (0xD9, 0x21, 0x21) if value == values[0] and sample['battery'] <= 20 else col_meta
            draw_text(canvas, fonts[METRIC], value, anchor, METRIC_Y, justify, color, scale)
    return canvas


def label(image, text, size):
    banner = Image.new('RGB', (image.width, image.height + size), (24, 24, 24))
    banner.paste(image, (0, size))
    ImageDraw.Draw(banner).text((4, 2), text, fill=(240, 240, 240), font=ImageFont.load_default())
    return banner


def magnify(image, factor):
    return image.resize((image.width * factor, image.height * factor), Image.Resampling.NEAREST)


def main():
    parser = argparse.ArgumentParser(description='MIP 1 位字体与布局模拟')
    parser.add_argument('--size', type=int, default=260, help='设备分辨率，默认 260')
    parser.add_argument('--theme', default='hour-color', choices=sorted(THEMES))
    parser.add_argument('--atlas', action='store_true', help='读已生成的图集，而不是重新渲染')
    parser.add_argument('--cutoff', type=int, action='append', help='alpha 二值化切点，可重复；默认取 MONO_CUTOFF')
    parser.add_argument('--sleep', action='store_true', help='同时输出 AOD 状态')
    parser.add_argument('--time', default='10:31', help='示例时间，用来决定时辰与刻')
    parser.add_argument('--date', default='09/23 周三')
    parser.add_argument('--battery', type=int, default=82)
    parser.add_argument('--steps', type=int, default=6543)
    parser.add_argument('--heart', type=int, default=72)
    parser.add_argument('--zoom', type=int, default=4, help='中央文字区放大倍数')
    parser.add_argument('--out', default=None, help='输出目录，默认 build/preview-mip')
    args = parser.parse_args()
    hour, minute = (int(part) for part in args.time.split(':'))
    sample = {'hour': hour, 'minute': minute, 'date': args.date,
              'battery': args.battery, 'steps': args.steps, 'heart': args.heart}
    cutoffs = args.cutoff or [gen.MONO_CUTOFF]
    reference = 'atlas' if args.atlas else 'render'
    target = ROOT / (args.out or f'build/preview-mip/{args.theme}-{args.size}')
    target.mkdir(parents=True, exist_ok=True)
    # 中央文字区（原型坐标 80..386 × 100..350）放大后最能看出笔画是否被削断。
    box = tuple(rnd(v * args.size / 466) for v in (80, 100, 386, 350))
    strips = []
    for cutoff in cutoffs:
        for sleeping in ([False, True] if args.sleep else [False]):
            name = f"cutoff{cutoff}{'-aod' if sleeping else ''}"
            canvas = face(args.size, args.theme, reference, cutoff, sleeping, sample)
            canvas.save(target / f'{name}.png')
            strip = label(magnify(canvas.crop(box), args.zoom), f'{name}  {"atlas" if args.atlas else "render"}  {args.theme} {args.size}px', 14)
            strip.save(target / f'{name}-center.png')
            strips.append(strip)
    sheet = Image.new('RGB', (max(s.width for s in strips), sum(s.height for s in strips)), (24, 24, 24))
    offset = 0
    for strip in strips:
        sheet.paste(strip, (0, offset))
        offset += strip.height
    sheet.save(target / 'compare.png')
    print(f'{"、".join(str(c) for c in cutoffs)} 切点 → {target}/compare.png')


if __name__ == '__main__':
    main()
