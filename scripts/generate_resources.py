"""从已确认原型的开源字体生成 BMFont、三个应用入口和设备配置。"""
import json
import hashlib
import math
from pathlib import Path
from xml.sax.saxutils import escape

from project import ROOT, THEMES, devices, venv, write

venv()
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
HOUR_COLORS = ["2B3A4F", "2A3C5C", "6C9BCA", "EA8958", "F2C867", "FFD111",
               "D92121", "FEBA07", "D4AF37", "FA7C5E", "6E4D7E", "1D3F5A"]
# 名称、字体族、字重、466px 原型字号、必要字形、原型字间距。
# Kai 为原型确认的楷体（霞鹜文楷静态 Medium 子集），没有可变字重，Ring 与 RingActive 同源，
# 当前时辰靠放大与强调色区分，与原型一致。
FONTS = [
    ("Ring", "Kai", 500, 31, BRANCHES, 0),
    ("RingActive", "Kai", 500, 35, BRANCHES, 0),
    ("Caption", "Kai", 500, 34, BRANCHES + "时 · 初一二三四五六七刻", 0),
    ("Date", "Sans", 400, 32, "0123456789/ 周日一二三四五六", 0),
    ("TimeSerif", "Serif", 900, 106, "0123456789:", 1),
    ("TimeSerifSleep", "Serif", 700, 106, "0123456789:", 1),
    ("TimeSans", "Sans", 500, 106, "0123456789:", 1),
    ("TimeSansSleep", "Sans", 400, 106, "0123456789:", 1),
    ("Metric", "Sans", 400, 36, "0123456789｜-", 0),
]
KAI = "designs/shichen-watchface/fonts/LXGWWenKai-Medium.woff2"


def rounded(value):
    return int(math.floor(value + 0.5))


def ttf(family, weight):
    """字族 → 可用 PIL 打开的 TTF，结果按源文件指纹缓存在 .tools/font-cache。"""
    if family == 'Kai':
        source = ROOT / KAI
        name = 'LXGWWenKai-Medium'
    else:
        source = ROOT / f"designs/shichen-watchface/fonts/Noto{family}SC-var.woff2"
        name = f"Noto{family}SC-{weight}"
    fingerprint = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
    path = ROOT / f".tools/font-cache/{name}-{fingerprint}.ttf"
    if not path.exists():
        font = TTFont(source)
        if family != 'Kai':
            instantiateVariableFont(font, {"wght": weight}, inplace=True)
        font.flavor = None
        # 位图衍生物使用项目名称，授权和原始来源仍保留在 licenses 中。
        path.parent.mkdir(parents=True, exist_ok=True)
        font.save(path)
    return path


def make_font(spec, size):
    name, family, weight, font_size, charset, spacing = spec
    font = ImageFont.truetype(str(ttf(family, weight)), rounded(font_size * size / 466))
    chars = sorted(set(charset), key=ord)
    cmap = TTFont(ttf(family, weight)).getBestCmap()
    missing = [c for c in chars if ord(c) not in cmap]
    if missing:
        raise ValueError(f'{family} 原始字体缺少字形：{"".join(missing)}')
    boxes = {c: font.getbbox(c, anchor="ls") for c in chars}
    base = -min(b[1] for b in boxes.values())
    height = max(b[3] for b in boxes.values()) + base
    sheet_width = 256
    glyphs = []
    x = y = row_height = 0
    for c in chars:
        left, top, right, bottom = boxes[c]
        w, h = max(1, right-left), max(1, bottom-top)
        if x + w + 1 > sheet_width:
            x = 0
            y += row_height + 1
            row_height = 0
        glyphs.append((c, x, y, w, h, left, top, rounded(font.getlength(c) + spacing * size / 466)))
        x += w + 1
        row_height = max(row_height, h)
    sheet = Image.new("RGBA", (sheet_width, y + row_height + 1), (255, 255, 255, 0))
    draw = ImageDraw.Draw(sheet)
    lines = [f'info face="Shichen{name}" size={rounded(font_size * size / 466)} bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=0,0',
             f'common lineHeight={height} base={base} scaleW={sheet.width} scaleH={sheet.height} pages=1 packed=0',
             f'page id=0 file="{name}.png"', f'chars count={len(glyphs)}']
    for c, x, y, w, h, left, top, advance in glyphs:
        draw.text((x-left, y-top), c, font=font, anchor="ls", fill="white")
        lines.append(f'char id={ord(c)} x={x} y={y} width={w} height={h} xoffset={left} yoffset={top+base} xadvance={advance} page=0 chnl=15')
    target = ROOT / f"shared/resources/{size}/fonts"
    target.mkdir(parents=True, exist_ok=True)
    sheet.save(target / f"{name}.png")
    write(target / f"{name}.fnt", "\n".join(lines) + "\n")
    return base


def rgb(hex_value):
    return tuple(int(hex_value[i:i+2], 16) for i in (0, 2, 4))


def ink(hex_value):
    components = [c / 255 for c in rgb(hex_value)]
    components = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in components]
    return "1D1B1C" if sum(c*w for c, w in zip(components, (0.2126, 0.7152, 0.0722))) > 0.32 else "F8F4ED"


def theme_source(theme):
    lines = ["// 由 scripts/generate_resources.py 生成。", "module Theme {"]
    for field, key in [("SERIF", "serif"), ("CYCLE", "cycle"), ("RIM_ON", "rimOn")]:
        lines.append(f"    const {field} = {str(theme[key]).lower()};")
    for field, key in [("FACE", "face"), ("SEGMENT", "segment"), ("SEGMENT_TEXT", "segmentText"),
                       ("CURRENT", "current"), ("CURRENT_TEXT", "currentText"), ("TIME", "time"),
                       ("DATE", "date"), ("META", "meta"), ("AOD_FACE", "aodFace"), ("AOD_TIME", "aodTime"),
                       ("AOD_DATE", "aodDate"), ("AOD_META", "aodMeta")]:
        lines.append(f"    const {field} = 0x{theme[key]};")
    blend = ''.join(f'{rounded((a+b)/2):02X}' for a,b in zip(rgb(theme['rim']), rgb(theme['face'])))
    lines += [f"    const RIM_BLEND = 0x{blend};", f"    const DIM = {theme['dim']};",
              "    const HOUR_COLORS = [" + ', '.join('0x'+h for h in HOUR_COLORS) + "];",
              "    const HOUR_INKS = [" + ', '.join('0x'+ink(h) for h in HOUR_COLORS) + "];", "}"]
    return '\n'.join(lines) + '\n'


def icon(theme, width, height, target):
    # 启动器图标沿用时辰环与子字；高分辨率绘制后缩小。
    scale = 4
    size = min(width, height)
    image = Image.new("RGBA", (size*scale, size*scale))
    draw = ImageDraw.Draw(image)
    mid = size*scale/2
    radius = mid-2*scale
    draw.ellipse((mid-radius, mid-radius, mid+radius, mid+radius), fill='#'+theme['face'])
    for i in range(12):
        outer = radius
        # 与原型一致：基准内径 174，当前时辰向内延伸 16（外径 230）。
        inner = radius*(158/230 if i == 0 else 174/230)
        angles = [math.radians(-105+i*30+1.1+j*27.8/12) for j in range(13)]
        points = [(mid+outer*math.cos(a), mid+outer*math.sin(a)) for a in angles]
        points += [(mid+inner*math.cos(a), mid+inner*math.sin(a)) for a in reversed(angles)]
        color = HOUR_COLORS[i] if theme['cycle'] else theme['current'] if i == 0 else theme['segment']
        draw.polygon(points, fill='#'+color)
    font = ImageFont.truetype(str(ttf('Kai', 500)), rounded(size*scale*0.42))
    draw.text((mid, mid), '子', font=font, anchor='mm', fill='#'+theme['time'])
    target.mkdir(parents=True, exist_ok=True)
    canvas = Image.new('RGBA', (width, height))
    canvas.paste(image.resize((size, size), Image.Resampling.LANCZOS), ((width-size)//2, (height-size)//2))
    canvas.save(target/'launcher.png')
    write(target/'drawables.xml', '<resources>\n  <bitmap id="LauncherIcon" filename="launcher.png"/>\n</resources>\n')


def generate():
    available = devices()
    if not available:
        raise SystemExit("没有可用的圆屏设备资料，请先在 SDK Manager 下载。")
    sizes = sorted({d['width'] for d in available.values()})
    for size in sizes:
        bases = {f[0]: make_font(f, size) for f in FONTS}
        default_bases = [bases[n] for n in ['Ring', 'RingActive', 'Caption', 'Date', 'TimeSans', 'TimeSansSleep', 'Metric']]
        write(ROOT/f'shared/generated/{size}/FontMetrics.mc',
              '// 由字体真实边界生成，坐标对应原型文字基线。\nmodule FontMetrics {\n'
              + f'    const BASES = {default_bases};\n'
              + f'    const SERIF_BASES = [{bases["TimeSerif"]}, {bases["TimeSerifSleep"]}];\n'
              + '}\n')
    for name, theme in THEMES.items():
        app = ROOT/name
        products = '\n'.join(f'      <iq:product id="{d}"/>' for d in available)
        write(app/'manifest.xml', f'''<?xml version="1.0" encoding="UTF-8"?>
<iq:manifest xmlns:iq="http://www.garmin.com/xml/connectiq" version="3">
  <iq:application id="{theme['id']}" type="watchface" name="@Strings.AppName" entry="HourApp" launcherIcon="@Drawables.LauncherIcon" minApiLevel="1.2.0" version="1.0.0">
    <iq:products>
{products}
    </iq:products>
    <iq:permissions/>
    <iq:languages><iq:language>eng</iq:language><iq:language>zhs</iq:language><iq:language>zht</iq:language></iq:languages>
    <iq:barrels/>
  </iq:application>
</iq:manifest>
''')
        write(app/'source/Theme.mc', theme_source(theme))
        license_text = '\n\n'.join((ROOT/'shared/licenses'/filename).read_text() for filename in
                                   ['NOTICES.txt', 'notosanssc-OFL.txt', 'notoserifsc-OFL.txt',
                                    'lxgwwenkai-OFL.txt'])
        write(app/'resources/base/strings.xml', '<resources>\n'
              + f'  <string id="AppName">{escape(theme["name"])}</string>\n'
              + f'  <string id="FontLicense">{escape(license_text)}</string>\n</resources>\n')
        configs = sorted({(d['width'], d['display'] == 'amoled') for d in available.values()})
        for size, antialias in configs:
            suffix = 'aa' if antialias else 'mono'
            entries = []
            for spec in FONTS:
                font_name = spec[0]
                if font_name.startswith('Time'):
                    if ('Serif' in font_name) != theme['serif']:
                        continue
                    font_id = 'TimeSleep' if font_name.endswith('Sleep') else 'Time'
                else:
                    font_id = font_name
                entries.append(f'  <font id="{font_id}" filename="../../../shared/resources/{size}/fonts/{font_name}.fnt" antialias="{str(antialias).lower()}"/>')
            write(app/f'resources/{size}-{suffix}/fonts.xml', '<resources>\n'+'\n'.join(entries)+'\n</resources>\n')
        for width, height in sorted({(d['icon'], d['iconHeight']) for d in available.values()}):
            icon(theme, width, height, app/f'resources/icon{width}x{height}')
        jungle = ['# 由 scripts/generate_resources.py 生成；只包含纯圆屏 Watch Face 目标。',
                  'project.manifest = manifest.xml', 'base.sourcePath = ../shared/source;source;../tests/native',
                  'base.resourcePath = resources/base', 'base.excludeAnnotations = preview']
        for dev, d in available.items():
            suffix = 'aa' if d['display'] == 'amoled' else 'mono'
            jungle += [f'{dev}.sourcePath = $(base.sourcePath);../shared/generated/{d["width"]}',
                       f'{dev}.resourcePath = $(base.resourcePath);resources/{d["width"]}-{suffix};resources/icon{d["icon"]}x{d["iconHeight"]}']
        write(app/'monkey.jungle', '\n'.join(jungle)+'\n')
    write(ROOT/'build/devices.json', json.dumps(available, ensure_ascii=False, indent=2)+'\n')
    print(f'已生成 3 个应用，{len(available)} 个圆屏目标，{len(sizes)} 种分辨率。')
    return available


if __name__ == '__main__':
    generate()
