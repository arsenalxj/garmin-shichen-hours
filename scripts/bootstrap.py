"""在项目 .tools 中准备 macOS Apple Silicon 的 Java、SDK 和 Python 依赖。"""
import hashlib
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen

from project import ROOT

JAVA_URL = 'https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.20.1%2B1/OpenJDK17U-jdk_aarch64_mac_hotspot_17.0.20.1_1.tar.gz'
JAVA_SHA = '196d13ba5f10414bef7f6a05a9b3f00edacb18ebacef2b99485db9e2ee18f0e8'
SDK_URL = 'https://developer.garmin.com/downloads/connect-iq/sdks/connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2.dmg'
SDK_SHA = '13bcc210483284074819c80dc90946db233af37be2518225e3f533d5804ebc1d'


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as file:
        for chunk in iter(lambda: file.read(1024*1024), b''):
            result.update(chunk)
    return result.hexdigest()


def download(url, filename, checksum):
    target = ROOT / '.tools/downloads' / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or digest(target) != checksum:
        partial = target.with_suffix(target.suffix+'.part')
        print(f'下载 {filename}…', flush=True)
        with urlopen(url, timeout=60) as source, partial.open('wb') as dest:
            shutil.copyfileobj(source, dest)
        if digest(partial) != checksum:
            raise SystemExit(f'{filename} SHA256 不匹配，未安装。')
        partial.replace(target)
    return target


def main():
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        raise SystemExit('自动准备脚本适用于 macOS Apple Silicon；其他系统请安装 Java 17 与 Connect IQ SDK，并设置 CIQ_SDK。')
    java_dir = ROOT/'.tools/java'
    if not list(java_dir.glob('*/Contents/Home/bin/java')):
        archive = download(JAVA_URL, 'java.tar.gz', JAVA_SHA)
        java_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(['tar', '-xzf', str(archive), '-C', str(java_dir)], check=True)
    if not (ROOT/'.tools/sdk/bin/monkeybrains.jar').is_file():
        dmg = download(SDK_URL, 'sdk.dmg', SDK_SHA)
        mount = ROOT/'.tools/sdk-mount'
        mount.mkdir(exist_ok=True)
        subprocess.run(['hdiutil', 'attach', str(dmg), '-nobrowse', '-mountpoint', str(mount)], check=True)
        try:
            matches = list(mount.rglob('monkeybrains.jar'))
            if len(matches) != 1:
                raise SystemExit('SDK 镜像目录结构发生变化，请使用 SDK Manager 安装。')
            shutil.copytree(matches[0].parent.parent, ROOT/'.tools/sdk', dirs_exist_ok=True)
        finally:
            subprocess.run(['hdiutil', 'detach', str(mount)], check=True)
            mount.rmdir()
    python = ROOT/'.tools/venv/bin/python'
    if not python.exists():
        subprocess.run([sys.executable, '-m', 'venv', str(ROOT/'.tools/venv')], check=True)
    subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(ROOT/'scripts/requirements.txt')], check=True)
    print('本地工具已就绪。设备包需在官方 SDK Manager 中登录并按 plans/DEVICES.md 下载。')


if __name__ == '__main__':
    main()
