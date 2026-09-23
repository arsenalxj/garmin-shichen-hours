"""FR255 真正打包资源的调色板、字形覆盖与时辰补丁检查。"""
import json
import base64
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MipResourcesTest(unittest.TestCase):
    def test_prototype_uses_packaged_pixels_and_metrics(self):
        script = (ROOT / 'designs/shichen-watchface/fr255-raster.js').read_text()
        bundle = json.loads(script.split('window.FR255_RASTER = ', 1)[1].rstrip(';\n'))
        self.assertEqual(set(bundle), {'hour-white', 'hour-black', 'hour-color'})
        for theme, assets in bundle.items():
            target = ROOT / theme / 'resources/fr255-raster'
            images = assets.pop('images')
            self.assertEqual(assets, json.loads((target / 'raster.json').read_text()), theme)
            identifiers = assets['faces'] + [p['id'] for p in assets['patches']] + [a['id'] for a in assets['atlases']]
            self.assertEqual(set(images), set(identifiers), theme)
            for identifier, image in images.items():
                self.assertEqual(base64.b64decode(image['uri'].split(',', 1)[1]),
                                 (target / (identifier + '.png')).read_bytes(), (theme, identifier))

    def test_fr255_has_dedicated_raster_resources(self):
        for theme in ('hour-white', 'hour-black', 'hour-color'):
            target = ROOT / theme / 'resources/fr255-raster'
            self.assertTrue((target / 'raster.json').is_file(), theme)
            jungle = (ROOT / theme / 'monkey.jungle').read_text().splitlines()
            selected = [line for line in jungle if line.startswith('fr255.')]
            self.assertTrue(any('fr255-raster' in line for line in selected))
            self.assertFalse(any('fr255-raster' in line for line in jungle
                                 if line.startswith('fr255m.')))

    def test_raster_pixels_and_patch_reconstruction(self):
        # 使用项目既有 Pillow 环境读取 PNG；测试入口仍可用系统 Python。
        result = subprocess.run([
            str(ROOT / '.tools/venv/bin/python'),
            str(ROOT / 'scripts/mip_resources.py'), '--verify',
        ], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['scenes'], 72)
        self.assertEqual(report['themes'], 3)
        self.assertGreater(report['antialiased_glyphs'], 100)


if __name__ == '__main__':
    unittest.main()
