# 十二时辰 · Garmin 圆屏表盘

三个独立的 Connect IQ 原生表盘，按 `designs/shichen-watchface/十二时辰表盘-三版对照.html` 实现，共用时间与绘制逻辑。

| 应用目录 | 风格 | 字体与配色 |
|---|---|---|
| `hour-white` | 宣纸留白 | 浅色盘面、朱砂当前时辰、宋体时间 |
| `hour-black` | 玄天黑金 | 深色盘面、金色当前时辰、无衬线时间 |
| `hour-color` | 十二时辰色 | 十二分区独立配色，中央强调色随时辰变化 |

外圈顶部为子时，顺时针排列。当前分区向内加厚，外沿位置不变。中央显示时辰刻数、日期、时间，底部依次为电量、步数、心率。

## 效果图

设计原型渲染图（子时·初刻 23:05），由 `designs/shichen-watchface/export-previews.mjs` 从原型页重新生成：

| 状态 | 宣纸留白 `hour-white` | 玄天黑金 `hour-black` | 十二时辰色 `hour-color` |
|---|---|---|---|
| 正常 | ![](designs/shichen-watchface/png/paper-454.png) | ![](designs/shichen-watchface/png/night-454.png) | ![](designs/shichen-watchface/png/cycle-454.png) |
| 常亮省电 | ![](designs/shichen-watchface/png/paper-aod-454.png) | ![](designs/shichen-watchface/png/night-aod-454.png) | ![](designs/shichen-watchface/png/cycle-aod-454.png) |

上表为 454px 大屏效果；同目录 `png/` 下还有各版 208px 小屏图（如 `paper-208.png`）。交互对照（时间、尺寸、电量、心率、步数、MIP 模拟）见 `designs/shichen-watchface/十二时辰表盘-三版对照.html`。

## 时间、数据与省电

- 读取手表本地时间，数字时钟跟随系统 12/24 小时制。
- 每刻 15 分钟，从初刻到七刻；23:00 子时初刻，23:45 子时三刻，00:00 子时四刻，01:00 丑时初刻。
- 日期在当地午夜切换。步数读取系统当日统计；心率优先使用当前有效读数，否则取五分钟内的最新有效历史样本，没有有效读数显示 `--`。
- 电量不高于 20% 时用朱砂色提示；心率只显示数字，不添加图标或单位。
- 普通省电状态按原型取消分区填充，只保留当前分区描边，并隐藏数据行和强调线。
- 设备报告 `requiresBurnInProtection` 时，省电状态直接全黑，抬腕后恢复完整画面。省电刷新不读取底部健康数据，不使用秒级定时器或后台服务。
- 只纳入官方资料中 `round` 且支持 `watchFace` 的设备。具体资料与验证范围见 `plans/DEVICES.md` 和 `plans/VALIDATION.md`。
- 按确认排除 Forerunner 45、Forerunner 55、Garmin Swim 2 三款 8 色机型。其余 MIP 严格映射原型颜色，因此白款普通分区可能与背景合并；当前时辰仍有强调色及向内延伸。

## 本地环境

自动准备脚本适用于 macOS Apple Silicon，使用项目内 Java 17、Connect IQ SDK 9.2.0 和 Python 虚拟环境，不替换系统工具。

```sh
python3 scripts/bootstrap.py
python3 scripts/device_status.py
python3 scripts/generate_resources.py
```

设备包由官方 SDK Manager 下载。资源生成器只使用已安装的纯圆屏设备资料，下载新机型后需要重新生成；生成器不会自动宣称所有官方型号已覆盖。

可通过 `CIQ_SDK` 指定 SDK 目录，通过 `CIQ_SIGNING_KEY` 指定已有开发签名密钥。设备资料使用 SDK Manager 的标准安装位置。

首次构建会生成 `.tools/signing/developer_key.der`。同一应用的后续更新应继续使用这把密钥，请单独备份；源码和交付包不包含私钥。

## 构建与验证

```sh
# 三个主题，默认覆盖九种屏幕尺寸的代表设备
python3 scripts/build.py --debug

# 指定设备与主题
python3 scripts/build.py --theme hour-white --device fenix9pro51mm

# 本机全部符合条件的机型
python3 scripts/build.py --all

# 字形覆盖、文字占位、应用 ID、原型规则一致性
python3 -m unittest discover -s tests -p 'test_*.py'

# 原生测试：先在官方模拟器中打开 ConnectIQ.app
python3 scripts/build.py --theme hour-white --device venu --test
python3 scripts/simulate.py --theme hour-white --device venu --test

# 正常读取模拟器系统数据
python3 scripts/simulate.py --theme hour-white --device fenix9pro51mm
```

模拟器程序位于 `.tools/sdk/bin/ConnectIQ.app`。`simulate.py` 运行普通表盘时会一直连接到该应用结束；从模拟器 File → Kill App 结束当前实例后可切换目标。模拟器产生的心率、步数用于开发验证，不是实表测量数据。

构建日志在 `build/<模式>/<主题>/<设备>.log`，本次批次汇总在对应目录的 `report.json`。原生测试另保存 `.simulation.log` 和 `.test-result.json`；SDK 的测试成功汇总才是通过依据。

## 固定数据验收

```sh
python3 scripts/preview.py --theme hour-color --device fenix9pro51mm --scene normal
python3 scripts/simulate.py --device fenix9pro51mm --file build/preview/hour-color/fenix9pro51mm/normal/preview.prg
```

场景定义在 `tests/scenes.json`，包括午夜、下一个时辰、寅时、12 小时制、缺失心率、六位步数、普通省电和受保护屏幕息屏。场景数据只参与 `build/preview/` 的独立验收构建；正式构建排除预览入口，不包含 `tests/preview` 或固定健康数据。

## 本机安装与商店导出

```sh
# 三个独立 .iq 商店文件，覆盖当前 manifest 中的设备及其地区硬件变体
python3 scripts/build.py --export
python3 scripts/verify_exports.py
```

导出文件位于 `build/export/hour-white/hour-white.iq`、`build/export/hour-black/hour-black.iq`、`build/export/hour-color/hour-color.iq`。导出不会上传 Connect IQ 商店。

实表侧载使用 `build/release/<主题>/<设备>.prg`，必须选择与手表匹配的设备 ID；手表通过 USB 挂载后，将对应 PRG 放入 `GARMIN/APPS/`，断开连接后在手表表盘列表中选择。`.iq` 用于商店提交，不能代替单机型 PRG 直接侧载。

字体来源与 SIL OFL 授权位于 `shared/licenses/`，发布交付需附带授权文本。三个应用有独立 ID，可以分别上架，尚未进行商店发布。
