"""检查中文字库覆盖、文字实际占位和正式包排除验收数据。"""
import json
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


class ResourcesTest(unittest.TestCase):
    def test_chinese_coverage_and_atlas_bounds(self):
        expected = {'Ring': '子丑寅卯辰巳午未申酉戌亥', 'RingActive': '子丑寅卯辰巳午未申酉戌亥',
                    'Caption': '子丑寅卯辰巳午未申酉戌亥时 · 初一二三四五六七刻',
                    'Date': '0123456789/ 周日一二三四五六', 'Metric': '0123456789%｜-', 'Period': '上午下'}
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
        for size in [218, 240, 260, 280, 360, 390, 416, 454, 466]:
            font = glyphs(size, 'Metric')
            # 六位步数仍与左右分隔符保留间隔。
            self.assertLess(advance(font, '999999')+advance(font, '｜'), 96*size/466)
            for name in ['TimeSerif', 'TimeSerifSleep', 'TimeSans', 'TimeSansSleep']:
                self.assertLess(advance(glyphs(size, name), '23:59'), 300*size/466)
            caption = glyphs(size, 'Caption')
            self.assertLess(advance(caption, '子时 · 初刻'), 285*size/466)

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
        for name in ['notosanssc', 'notoserifsc']:
            self.assertIn('SIL OPEN FONT LICENSE', (ROOT/f'shared/licenses/{name}-OFL.txt').read_text())


if __name__ == '__main__':
    unittest.main()
