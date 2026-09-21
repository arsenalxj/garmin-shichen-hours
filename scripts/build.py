"""构建独立表盘；默认覆盖各屏幕尺寸的代表机型，不连接商店。"""
import argparse
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

from project import ROOT, THEMES, devices, java, sdk, write

REPRESENTATIVES = ['fenix3_hr', 'fenix5', 'fenix6', 'fenix6xpro',
                   'venu2s', 'venu', 'fenix843mm', 'fenix847mm', 'fenix9pro51mm']


def signing_key():
    override = os.environ.get('CIQ_SIGNING_KEY')
    if override:
        path = Path(override).expanduser().resolve()
        if not path.is_file():
            raise SystemExit('CIQ_SIGNING_KEY 指向的私钥不存在')
        return path
    path = ROOT / '.tools/signing/developer_key.der'
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.parent.chmod(0o700)
        # 私钥只通过进程管道转换，不打印，也不产生额外 PEM 文件。
        pem = subprocess.run(['openssl', 'genrsa', '4096'], check=True, capture_output=True).stdout
        der = subprocess.run(['openssl', 'pkcs8', '-topk8', '-inform', 'PEM', '-outform', 'DER', '-nocrypt'],
                             input=pem, check=True, capture_output=True).stdout
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as file:
            file.write(der)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--theme', choices=[*THEMES, 'all'], default='all')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--device', action='append', help='设备 ID，可重复指定')
    group.add_argument('--all', action='store_true', help='编译本机全部纯圆屏 Watch Face 目标')
    group.add_argument('--export', action='store_true', help='导出 manifest 中的全部目标到 .iq；不上传商店')
    parser.add_argument('--test', action='store_true', help='包含原生单元测试')
    parser.add_argument('--debug', action='store_true', help='包含调试信息')
    parser.add_argument('--generate', action='store_true', help='先按最新已下载设备生成资源与应用清单')
    args = parser.parse_args()
    if args.export and (args.test or args.debug):
        parser.error('商店导出不能包含测试或调试数据')
    if args.generate:
        subprocess.run(['python3', str(ROOT/'scripts/generate_resources.py')], check=True, cwd=ROOT)
    available = devices()
    targets = list(available) if args.all else args.device or REPRESENTATIVES
    if args.export:
        targets = ['store']
    missing = [d for d in targets if d != 'store' and d not in available]
    if missing:
        parser.error('缺少设备资料或机型不在支持范围：' + ', '.join(missing))
    themes = list(THEMES) if args.theme == 'all' else [args.theme]
    key = signing_key()
    mode = 'export' if args.export else 'tests' if args.test else 'debug' if args.debug else 'release'
    report = {'mode': mode, 'started': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'builds': []}
    report_path = ROOT / f'build/{mode}/report.json'
    for theme in themes:
        for device in targets:
            output = ROOT / f'build/{mode}/{theme}/{theme if args.export else device}.{"iq" if args.export else "prg"}'
            output.parent.mkdir(parents=True, exist_ok=True)
            command = [java(), '-Xmx1g', '-jar', str(sdk()/'bin/monkeybrains.jar'),
                       '-f', str(ROOT/theme/'monkey.jungle'), '-o', str(output), '-y', str(key), '-w', '-l', '1']
            command += ['-e', '-r'] if args.export else ['-d', device]
            if args.test:
                command.append('-t')
            elif not args.debug and not args.export:
                command.append('-r')
            started = time.monotonic()
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            log = output.with_suffix('.log')
            log.write_text(result.stdout + result.stderr)
            ok = result.returncode == 0 and output.is_file()
            report['builds'].append({'theme': theme, 'device': device, 'passed': ok,
                                     'seconds': round(time.monotonic()-started, 2),
                                     'bytes': output.stat().st_size if ok else None,
                                     'log': str(log.relative_to(ROOT))})
            write(report_path, json.dumps(report, ensure_ascii=False, indent=2)+'\n')
            print(f'{"通过" if ok else "失败"} {theme} / {device}', flush=True)
            if not ok:
                print((result.stdout+result.stderr)[-9000:])
                raise SystemExit(1)
            if args.export:
                shutil.copytree(ROOT/'shared/licenses', output.parent/'licenses', dirs_exist_ok=True)
    print(f'完成 {len(report["builds"])} 项构建。报告：{report_path}')


if __name__ == '__main__':
    main()
