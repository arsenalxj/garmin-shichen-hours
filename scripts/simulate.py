"""将已经构建的 PRG 送入官方模拟器；先打开 ConnectIQ.app。"""
import argparse
import json
import subprocess

from project import ROOT, THEMES, EXCLUDED_DEVICES, java, sdk, write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--theme', choices=THEMES, default='hour-white')
    parser.add_argument('--device', required=True)
    parser.add_argument('--test', action='store_true')
    parser.add_argument('--mode', choices=['debug', 'release'], default='debug')
    parser.add_argument('--file', type=str, help='指定预览或其他已构建 PRG')
    args = parser.parse_args()
    if args.device in EXCLUDED_DEVICES:
        parser.error('该 8 色机型已按用户确认排除，不支持运行本项目表盘。')
    mode = 'tests' if args.test else args.mode
    program = ROOT/args.file if args.file else ROOT/f'build/{mode}/{args.theme}/{args.device}.prg'
    if not program.is_file():
        parser.error(f'缺少 PRG，请先构建：{program}')
    command = [java(), '-classpath', str(sdk()/'bin/monkeybrains.jar'),
               'com.garmin.monkeybrains.monkeydodeux.MonkeyDoDeux',
               '-f', str(program), '-d', args.device, '-s', str(sdk()/'bin/shell')]
    if args.test:
        command.append('-t')
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    output = result.stdout + result.stderr
    log = program.with_suffix('.simulation.log')
    log.write_text(output)
    print(output)
    if args.test:
        # SDK 9.2 的 MonkeyDoDeux 在测试通过时也可能返回 1，使用原生测试汇总判定。
        import re
        summary = re.search(r'PASSED \(passed=(\d+), failed=0, errors=0\)', output)
        ok = summary is not None and int(summary.group(1)) > 0
        write(program.with_suffix('.test-result.json'), json.dumps({
            'passed': ok, 'tests': int(summary.group(1)) if summary else 0,
            'processExitCode': result.returncode, 'log': str(log.relative_to(ROOT)),
        }, ensure_ascii=False, indent=2)+'\n')
        raise SystemExit(0 if ok else 1)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
