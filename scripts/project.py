"""项目路径与官方设备资料；只读取 SDK Manager 已安装的内容。"""
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GARMIN = Path.home() / "Library/Application Support/Garmin/ConnectIQ"
THEMES = json.loads((ROOT / "shared/themes.json").read_text())
# 用户确认不支持这三款 8 色圆屏手表。
EXCLUDED_DEVICES = {"fr45", "fr55", "garminswim2"}


def venv():
    """资源脚本使用项目固定依赖，不改变系统 Python。"""
    python = ROOT / ".tools/venv/bin/python"
    if Path(sys.prefix) != ROOT / ".tools/venv":
        if not python.exists():
            raise SystemExit("请先运行 python3 scripts/bootstrap.py")
        os.execv(str(python), [str(python), *sys.argv])


def sdk():
    path = Path(os.environ.get("CIQ_SDK", ROOT / ".tools/sdk")).expanduser()
    if not (path / "bin/monkeybrains.jar").is_file():
        raise SystemExit("未找到 Connect IQ SDK；请设置 CIQ_SDK 或运行 bootstrap.py")
    return path


def java():
    candidates = sorted((ROOT / ".tools/java").glob("*/Contents/Home/bin/java"))
    path = candidates[-1] if candidates else shutil.which("java")
    if not path:
        raise SystemExit("未找到 Java 17；请运行 bootstrap.py")
    return str(path)


def devices():
    items = {}
    root = GARMIN / "Devices"
    for path in sorted(root.glob("*/compiler.json")):
        if path.parent.name in EXCLUDED_DEVICES:
            continue
        try:
            compiler = json.loads(path.read_text())
            simulator = json.loads((path.parent / "simulator.json").read_text())
        except (OSError, ValueError):
            continue
        faces = [a for a in compiler.get("appTypes", []) if a["type"] == "watchFace"]
        if simulator.get("display", {}).get("shape") != "round" or not faces:
            continue
        items[path.parent.name] = {
            "id": path.parent.name, "name": compiler["displayName"],
            "width": compiler["resolution"]["width"],
            "height": compiler["resolution"]["height"],
            "display": compiler["displayType"],
            "icon": compiler["launcherIcon"]["width"],
            "iconHeight": compiler["launcherIcon"]["height"],
            "memory": faces[0]["memoryLimit"],
            "burnInProtection": bool(simulator.get("screenProtectionSupport", False)),
        }
    return items


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text() != text:
        path.write_text(text)
