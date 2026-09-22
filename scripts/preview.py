"""构建固定数据的原生验收场景；输出仅限 build/preview，不用于商店发布。"""
import argparse
import json
import subprocess

from build import signing_key
from project import ROOT, THEMES, devices, java, sdk, write


def main():
    scenes = json.loads((ROOT/'tests/scenes.json').read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--theme', choices=THEMES, required=True)
    parser.add_argument('--device', required=True)
    parser.add_argument('--scene', choices=scenes, default='normal')
    args = parser.parse_args()
    available = devices()
    if args.device not in available:
        parser.error('没有此圆屏机型的设备资料')
    device = available[args.device]
    target = ROOT/f'build/preview/{args.theme}/{args.device}/{args.scene}'
    scene = scenes[args.scene]
    fields = [('HOUR', 'hour', 23), ('MINUTE', 'minute', 45), ('DAY', 'day', 21), ('WEEKDAY', 'dayOfWeek', 2),
              ('BATTERY', 'battery', 86), ('STEPS', 'steps', 12860), ('HR', 'heartRate', 72),
              ('PROTECTED', 'protected', device['burnInProtection']), ('SLEEPING', 'sleeping', False)]
    source = 'module PreviewScenario {\n' + '\n'.join(f'    const {key} = {json.dumps(scene.get(field, default))};' for key,field,default in fields) + '\n}\n'
    write(target/'source/PreviewScenario.mc', source)
    suffix = 'aa' if device['display'] == 'amoled' else 'mono'
    source_dirs = [ROOT/'shared/source', ROOT/args.theme/'source', ROOT/'tests/preview',
                   ROOT/f'shared/generated/{device["width"]}', target/'source']
    resources = [ROOT/args.theme/'resources/base', ROOT/args.theme/f'resources/{device["width"]}-{suffix}', ROOT/args.theme/f'resources/icon{device["icon"]}x{device["iconHeight"]}']
    jungle = f'project.manifest = {ROOT/args.theme/"manifest.xml"}\n'
    jungle += 'base.sourcePath = '+ ';'.join(map(str,source_dirs))+'\n'
    jungle += 'base.resourcePath = '+ ';'.join(map(str,resources))+'\n'
    jungle += 'base.excludeAnnotations = production\n'
    write(target/'preview.jungle', jungle)
    output = target/'preview.prg'
    command = [java(), '-jar', str(sdk()/'bin/monkeybrains.jar'), '-f', str(target/'preview.jungle'),
               '-d', args.device, '-o', str(output), '-y', str(signing_key()), '-w', '-l', '1']
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    output.with_suffix('.log').write_text(result.stdout+result.stderr)
    print(result.stdout+result.stderr)
    if result.returncode:
        raise SystemExit(result.returncode)
    print('原生验收场景：'+str(output))


if __name__ == '__main__':
    main()
