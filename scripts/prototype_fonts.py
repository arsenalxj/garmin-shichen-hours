"""把候选开源字体裁成原型子集，供对照页切换环上字形。

原字体下载到 .tools/font-cache/candidates/（不进版本管理），
只有裁好的子集与授权文本写入 designs/shichen-watchface/fonts/。
选定字体接入表盘时，再由 generate_resources.py 按设备分辨率生成 BMFont。
"""
from urllib.request import urlopen

from project import ROOT, venv, write

venv()
from fontTools import subset
from fontTools.ttLib import TTFont

CACHE = ROOT/'.tools/font-cache/candidates'
OUT = ROOT/'designs/shichen-watchface/fonts'
LICENSES = OUT/'licenses'
# 十二地支 + 时辰小注用字：环上与「子时 · 初刻」同族显示。
# 空格也要留：小注「子时 · 初刻」中间有空格，缺字形时 BMFont 生成会直接报错。
CHARS = "子丑寅卯辰巳午未申酉戌亥时· 初一二三四五六七刻"

# 文件名、界面名、下载地址、授权文本地址
CANDIDATES = [
    ("LXGWWenKai-Medium", "霞鹜文楷", "LXGWWenKai-Medium.ttf",
     "https://github.com/lxgw/LxgwWenKai/releases/download/v1.522/LXGWWenKai-Medium.ttf",
     "https://raw.githubusercontent.com/lxgw/LxgwWenKai/main/OFL.txt"),
    ("ZhuqueFangsong-Regular", "朱雀仿宋", "ZhuqueFangsong-Regular.ttf",
     "https://github.com/TrionesType/zhuque/releases/download/v0.212/ZhuqueFangsong-v0.212.zip",
     "https://raw.githubusercontent.com/TrionesType/zhuque/master/LICENSE.txt"),
    ("Yozai-Medium", "悠哉字体", "Yozai-Medium.ttf",
     "https://github.com/lxgw/yozai-font/releases/download/v0.868/Yozai-Medium.ttf",
     "https://raw.githubusercontent.com/lxgw/yozai-font/master/OFL.txt"),
]


def fetch(url, path):
    """整份下完再改名，中断不会留下半个文件冒充缓存。"""
    if path.exists() and path.stat().st_size:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + '.part')
    with urlopen(url) as response, open(part, 'wb') as target:
        target.write(response.read())
    part.rename(path)
    return path


def source(name, url, archive):
    """返回解好的字体原文件；已缓存就直接复用，不重复下载几十兆。"""
    target = CACHE/name
    if target.exists() and target.stat().st_size:
        return target
    path = fetch(url, CACHE/archive)
    if archive.endswith('.zip'):
        from zipfile import ZipFile
        with ZipFile(path) as z:
            for entry in z.namelist():
                if entry.endswith(('.ttf', '.otf')):
                    z.extract(entry, CACHE)
        extracted = sorted(p for p in CACHE.glob('*.ttf') if p.stem.startswith(name.split('-')[0]))
        if not extracted:
            raise SystemExit(f'压缩包中没有找到 {name}')
        extracted[0].rename(target)
    else:
        path.rename(target)
    return target


def subset_font(src, target):
    font = TTFont(src)
    missing = [c for c in CHARS if ord(c) not in font.getBestCmap()]
    if missing:
        raise SystemExit(f'{src.name} 缺少字形：{"".join(missing)}')
    options = subset.Options()
    options.flavor = 'woff2'
    options.layout_features = []
    options.drop_tables += ['DSIG', 'BASE', 'JSTF']
    options.name_IDs = ['*']
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(text=CHARS)
    subsetter.subset(font)
    font.flavor = 'woff2'
    font.save(target)


def main():
    for name, label, archive, url, license_url in CANDIDATES:
        src = source(name, url, archive)
        target = OUT/f'{name}.woff2'
        subset_font(src, target)
        license_path = LICENSES/f'{name}-OFL.txt'
        if not license_path.exists():
            license_path.parent.mkdir(parents=True, exist_ok=True)
            write(license_path, urlopen(license_url).read().decode('utf-8'))
        print(f'✓ {label} {name}.woff2 {target.stat().st_size/1024:.0f} KB')


if __name__ == '__main__':
    main()
