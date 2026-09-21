"""检查官方 .iq 包内每个地区硬件变体、签名材料与应用 ID。"""
import hashlib
import json
import subprocess
from xml.etree import ElementTree as ET

from project import ROOT, GARMIN, THEMES, devices, write


def main():
    available = devices()
    device_root = GARMIN/'Devices'
    expected = set()
    for dev in available:
        profile = json.loads((device_root/dev/'compiler.json').read_text())
        expected.update(part['number'] for part in profile['partNumbers'])
    reports = []
    for name, theme in THEMES.items():
        package = ROOT/f'build/export/{name}/{name}.iq'
        entries = set(subprocess.run(['bsdtar', '-tf', str(package)], check=True, capture_output=True, text=True).stdout.splitlines())
        manifest = subprocess.run(['bsdtar', '-xOf', str(package), 'manifest.xml'], check=True, capture_output=True).stdout
        xml = ET.fromstring(manifest)
        ns = {'iq': 'http://www.garmin.com/xml/connectiq'}
        app = xml.find('iq:application', ns)
        assert app.attrib['id'] == theme['id'], f'{name}: 应用 ID 不符'
        products = app.findall('iq:products/iq:product', ns)
        actual = {p.attrib['partNumber'] for p in products}
        assert expected == actual, f'{name}: 硬件变体不完整，缺少 {expected-actual}，额外 {actual-expected}'
        assert all(p.attrib['filename'] in entries for p in products), f'{name}: 缺少设备 PRG'
        assert {'manifest.sig2', 'dev_key.pub'} <= entries, f'{name}: 缺少官方签名材料'
        # 正式导出不得保留预览入口或单元测试符号。
        debug_entries = [e for e in entries if e.endswith('/debug.xml')]
        with subprocess.Popen(['bsdtar', '-xOf', str(package), *debug_entries], stdout=subprocess.PIPE) as process:
            debug_xml = process.communicate()[0]
            assert process.returncode == 0
        assert b'PreviewScenario' not in debug_xml and b'PreviewView' not in debug_xml, f'{name}: 混入预览入口'
        assert b'allMinutes' not in debug_xml, f'{name}: 混入测试入口'
        assert b'FontLicense' in debug_xml, f'{name}: 缺少嵌入字体授权资源'
        log = package.with_suffix('.log').read_text()
        reports.append({'theme': name, 'deviceTargets': len(available), 'hardwareVariants': len(actual),
                        'warnings': log.count('WARNING:'), 'errors': log.count('ERROR:'),
                        'bytes': package.stat().st_size, 'sha256': hashlib.sha256(package.read_bytes()).hexdigest(),
                        'passed': True})
        print(f'{name}：{len(available)} 个目标 / {len(actual)} 个硬件变体，包内覆盖及正式入口检查通过。')
    write(ROOT/'build/export/verification.json', json.dumps(reports, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()
