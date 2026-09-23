# 十二时辰佳明表盘

使用 Connect IQ / Monkey C，将已确认的圆屏原型实现为三个独立表盘：`hour-white`（宣纸留白）、`hour-black`（玄天黑金）、`hour-color`（十二时辰色）。

## 规范与设计依据

- 项目说明使用中文；完整需求见 `plans/PLAN.md`。
- 视觉依据为 `designs/shichen-watchface/十二时辰表盘-三版对照.html`，包含正常与省电状态。修复功能差异时同步原型；改变视觉前先确认。
- 原型与成品默认使用黑体时辰字和小注；260px MIP 原型复用 FR255 标准版的圆环和字形像素资源。字体与字号标定见 `shared/licenses/README.md`。
- 只支持官方设备资料中屏幕形状为 round、支持 Watch Face 的手表。
- 按用户确认排除三款 8 色机型：Forerunner 45、Forerunner 55、Garmin Swim 2。其余 MIP 机型严格映射原型颜色，接受白款浅灰分区与背景合并。
- 时辰按设备本地时间计算，一刻 15 分钟，显示初刻至七刻；系统的 12/24 小时显示设置不影响计算。
- 三个表盘分别持有应用 ID 和主题资源；公共行为集中实现，避免复制三套逻辑。

## 目录约定

- `hour-white/`、`hour-black/`、`hour-color/`：独立应用清单、构建入口与主题，长期保留。
- `shared/`：共用 Monkey C 源码、按分辨率生成的字体资源及授权文件；生成资源由脚本维护。
- `shared/generated/raster-default/`：普通绘制路径的资源开关；`shared/generated/fr255/<主题>/` 与 `<主题>/resources/fr255-raster/`：FR255 标准版的预混色字形、圆环和定位表，由 `scripts/mip_resources.py` 生成。名称使用 `Mip` 前缀；随生成脚本长期维护，停止支持此路径时整体移除。
- `scripts/`：环境准备、资源生成、设备清单和构建验证脚本，使用小写下划线命名。
- `tests/`：可在 Connect IQ 模拟器运行的行为测试与资源/布局检查。
- `designs/`：用户确认的 HTML 原型与字体，作为验收基准长期保留；字形子集与授权文本也在 `designs/shichen-watchface/fonts/`。
- `designs/shichen-watchface/fr255-raster.js`：由资源脚本从正式 FR255 PNG 与定位表生成的网页资源，支持本地直接打开原型；随对应像素资源一起更新或移除。`png/` 存放原型导出图，由 `export-previews.mjs` 重建。
- `plans/`：实施方案与验收记录。
- `.tools/`：本机 SDK、Java、Python 环境、下载缓存及开发签名密钥，不纳入版本管理。密钥应单独备份；其他缓存可在工具退出后清理。
- `build/`：编译包、日志和验收截图，可重新生成；清理前保留需要交付的包与证据。
- `build/install/<设备 ID>/`：供 USB 侧载的安装文件，按 `hour-white.prg`、`hour-black.prg`、`hour-color.prg` 命名，避免复制到手表时互相覆盖；从对应正式构建复制生成，可重新生成后清理。

## 构建与检查

本项目不使用 Node 包管理器。Python 辅助依赖放在 `.tools/venv/`，Java 和 SDK 使用项目内环境。

- `python3 scripts/bootstrap.py`：准备构建环境。
- `python3 scripts/generate_resources.py`：生成字体、主题和设备构建资源。
- `python3 scripts/build.py --help`：查看单设备、全设备与商店包构建选项。
- `python3 -m unittest discover -s tests -p 'test_*.py'`：资源、原型一致性与工具测试。
- 编译后必须通过 SDK 原生测试及代表设备模拟器检查，网页预览不能代替设备验证。
