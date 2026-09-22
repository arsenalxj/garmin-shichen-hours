"""检查中文字库覆盖、文字实际占位和正式包排除验收数据。"""
import json
import math
import re
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {'iq': 'http://www.garmin.com/xml/connectiq'}


def glyphs(size, name):
    result = {}
    for line in (ROOT/f'shared/resources/{size}/fonts/{name}.fnt').read_text().splitlines():
        if line.startswith('char '):
            data = {k: int(v) for k,v in re.findall(r'(\w+)=(-?\d+)', line)}
            result[chr(data['id'])] = data
    return result


def advance(font, text):
    return sum(font[c]['xadvance'] for c in text)


def line_base(size, name):
    fnt = (ROOT/f'shared/resources/{size}/fonts/{name}.fnt').read_text()
    return int(re.search(r'common[^\n]*base=(-?\d+)', fnt).group(1))


def text_box(size, name, text, anchor, justify, baseline):
    """文字盒 (left, right, top, bottom)，坐标为 466 原型坐标系。"""
    font, base = glyphs(size, name), line_base(size, name)
    width = advance(font, text)
    left = anchor - width if justify == 'end' else anchor - width/2 if justify == 'middle' else anchor
    ink = [font[c] for c in text]
    top = baseline + min(g['yoffset'] - base for g in ink)*466/size
    bottom = baseline + max(g['yoffset'] + g['height'] - base for g in ink)*466/size
    return left, left + width, top, bottom


class ResourcesTest(unittest.TestCase):
    def test_chinese_coverage_and_atlas_bounds(self):
        expected = {'Ring': '子丑寅卯辰巳午未申酉戌亥', 'RingActive': '子丑寅卯辰巳午未申酉戌亥',
                    'Caption': '子丑寅卯辰巳午未申酉戌亥时 · 初一二三四五六七刻',
                    'Date': '0123456789/ 周日一二三四五六', 'Metric': '0123456789｜-'}
        for directory in (ROOT/'shared/resources').iterdir():
            if not directory.name.isdigit():
                continue
            for name, chars in expected.items():
                font = glyphs(directory.name, name)
                self.assertTrue(set(chars) <= set(font), (directory.name, name))
                fnt = (directory/f'fonts/{name}.fnt').read_text()
                values = {k: int(v) for k,v in re.findall(r'(scaleW|scaleH|lineHeight)=(-?\d+)', fnt)}
                for g in font.values():
                    self.assertGreaterEqual(g['yoffset'], 0)
                    self.assertLessEqual(g['x']+g['width'], values['scaleW'])
                    self.assertLessEqual(g['y']+g['height'], values['scaleH'])

    def test_text_stays_between_dividers(self):
        # 当前时辰扇环只占顶部 ±15°：角点落在扇环角度内不能压到内径 158，落在角度外只会碰到
        # 相邻分区（环内沿 174）；两种限值都留 8px 余量。文字盒按真实字形墨迹算，不用字体行高。
        boxes = []
        for size in [218, 240, 260, 280, 360, 390, 416, 454, 466]:
            # 数据区一行「电量 ｜ 步数 ｜ 心跳」基线 328，电量右端 CX-76、分隔线 CX±60、心跳左端 CX+76；
            # 最宽取值 100 / 99999 / 199。
            for text, anchor, justify in [('100', -76, 'end'), ('｜', -60, 'middle'), ('99999', 0, 'middle'),
                                          ('｜', 60, 'middle'), ('199', 76, 'start')]:
                boxes.append((size, text, text_box(size, 'Metric', text, 233 + anchor, justify, 328)))
            for name in ['TimeSerif', 'TimeSerifSleep', 'TimeSans', 'TimeSansSleep']:
                boxes.append((size, name, text_box(size, name, '23:59', 233, 'middle', 268)))
            # 小注与当前时辰同色，基线 131：中心处必须留在当前时辰内径 158 之内（分区内沿在 y=75），
            # 否则强调色小注压在强调色分区上看不见。
            top = text_box(size, 'Caption', '子时 · 初刻', 233, 'middle', 131)[2]
            self.assertGreater(top, 75, size)
        for size, text, (left, right, top, bottom) in boxes:
            scale = size/466
            for x in (left*scale, right*scale):
                for y in (top*scale, bottom*scale):
                    dx, dy = x - size/2, y - size/2
                    angle = math.degrees(math.atan2(abs(dx), -dy)) if dy < 0 else 180.0
                    limit = 158 if angle <= 15 else 174
                    self.assertLess(math.hypot(dx, dy), (limit - 8)*scale, (size, text, x, y))

    def test_ring_font_candidates_have_subset_and_license(self):
        html = (ROOT/'designs/shichen-watchface/十二时辰表盘-三版对照.html').read_text()
        fonts = ROOT/'designs/shichen-watchface/fonts'
        # 原型页引用的候选环上字体必须同时留下子集和 OFL 授权文本，否则换字体时容易只改一半。
        for name in ['LXGWWenKai-Medium', 'ZhuqueFangsong-Regular', 'Yozai-Medium']:
            self.assertIn(f'fonts/{name}.woff2', html)
            self.assertGreater((fonts/f'{name}.woff2').stat().st_size, 0)
            self.assertIn('SIL OPEN FONT LICENSE', (fonts/f'licenses/{name}-OFL.txt').read_text())

    def test_manifest_identity_and_round_scope(self):
        available = json.loads((ROOT/'build/devices.json').read_text())
        ids = set()
        for theme in ['hour-white', 'hour-black', 'hour-color']:
            xml = ET.parse(ROOT/theme/'manifest.xml')
            app = xml.find('iq:application', NS)
            ids.add(app.attrib['id'])
            self.assertEqual(app.attrib['type'], 'watchface')
            products = {p.attrib['id'] for p in app.findall('iq:products/iq:product', NS)}
            self.assertEqual(products, set(available))
            self.assertFalse(products & {'fr45', 'fr55', 'garminswim2'})
            jungle = (ROOT/theme/'monkey.jungle').read_text()
            self.assertIn('base.excludeAnnotations = preview', jungle)
            self.assertNotIn('tests/preview', jungle)
            self.assertNotIn('PreviewScenario', jungle)
        self.assertEqual(len(ids), 3)
        for device in available.values():
            self.assertEqual(device['width'], device['height'])

    def test_prototype_color_and_quarter_agreement(self):
        html = (ROOT/'designs/shichen-watchface/十二时辰表盘-三版对照.html').read_text()
        self.assertIn("'初一二三四五六七'[ke]", html)
        self.assertIn("#6C9BCA", html)
        themes = json.loads((ROOT/'shared/themes.json').read_text())
        for theme in themes.values():
            for field in ['face', 'time', 'date', 'meta', 'aodFace', 'aodTime', 'aodDate']:
                self.assertIn('#'+theme[field], html)
        for name in ['notosanssc', 'notoserifsc', 'lxgwwenkai']:
            self.assertIn('SIL OPEN FONT LICENSE', (ROOT/f'shared/licenses/{name}-OFL.txt').read_text())


if __name__ == '__main__':
    unittest.main()
