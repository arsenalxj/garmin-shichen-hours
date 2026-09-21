"""刷新已有下载清单中的本机状态，不下载设备或更改兼容范围。"""
import re
from project import ROOT, devices, write


def main():
    available = devices()
    names = {d['name'] for d in available.values()}
    path = ROOT/'plans/DEVICES.md'
    content = path.read_text()
    catalog = set()
    missing = []
    def row(match):
        name = match.group(1)
        catalog.add(name)
        if name not in names:
            missing.append(name)
        return '- ['+('x' if name in names else ' ')+'] '+name+' — '
    content = re.sub(r'^- \[[ x]\] (.*?) — ', row, content, flags=re.M)
    installed = len(catalog & names)
    content = re.sub(r'其中 \d+ 个在本机已发现设备资料，\d+ 个尚未发现',
                     f'其中 {installed} 个在本机已发现设备资料，{len(missing)} 个尚未发现', content)
    groups = re.split(r'(?=^### API level )',content,flags=re.M)
    for i, group in enumerate(groups):
        if not group.startswith('### API level '):
            continue
        total = len(re.findall(r'^- \[[ x]\]', group, re.M))
        pending = len(re.findall(r'^- \[ \]', group, re.M))
        groups[i] = re.sub(r'（\d+ 项，待补 \d+ 项）', f'（{total} 项，待补 {pending} 项）', group, count=1)
    write(path, ''.join(groups))
    print(f'清单 {len(catalog)} 个目标，已发现 {installed} 个，未发现 {len(missing)} 个。')
    for name in missing:
        print('未发现：'+name)
    for name in sorted(names-catalog):
        print('本机新增、待纳入清单：'+name)


if __name__ == '__main__':
    main()
