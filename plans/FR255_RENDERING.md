# Forerunner 255 标准版像素优化

2026-09-23，经用户确认采用预混色边缘、中文笔画校准和圆环像素优化。范围为 `fr255` 标准版的三个主题；布局、主色、时辰和数据逻辑沿用原设计。

## 绘制方式

- FR255 是 260 × 260、64 色 MIP。设备资源资料的 `alphaBlendingSupport=false`；原生实验中，仅将字体导入设为 `antialias=true` 仍得到黑白硬边。
- `scripts/mip_resources.py` 先将字形覆盖率与实际前景/背景混合，量化到 RGB 各 4 档，再保存为仅含全透明/全不透明像素的图集。数字和中文可以显示设备真实支持的中间色，无需运行时透明度混合。
- 小字统一采用 Noto Sans SC 400 字重，修正直接平滑旧 300 字重后的细淡问题；无衬线时间正常/省电为 350/300，白款衬线时间为 600/450。字号和文字锚点保持不变。
- 圆环在连续坐标上以 8 倍采样生成，缩到真实像素后再量化，避免先取整多边形顶点。正常与省电各有一个底图、12 个当前时辰补丁；环上字一并生成。切换时先画底图再覆盖当前补丁，清除前一个时辰的突出部分。
- 中央文字依然读取实时数据并逐字排版。`drawBitmap2` 的裁剪坐标保留图集原点，绘制时抵消源字形偏移，避免出现位置漂移。
- 新绘制路径使用 API 4.2.1 的 `drawBitmap2`；固件不提供此接口时自动沿用通用字体与绘制路径。
- 运行时只保留当前状态底图、当前时辰补丁和当前文字图集。切换省电状态时释放旧引用，资源内容在编译前生成，表盘无需每次做超采样或逐像素混色。

## 目录与生成

- `shared/generated/fr255/<主题>/RasterAssets.mc`：资源 ID、字形基线、定位、前景色与状态映射。
- `<主题>/resources/fr255-raster/`：圆环底图、时辰补丁、字体 PNG 和可核验的 `raster.json`。
- `shared/generated/raster-default/`：其他设备的关闭配置。
- `shared/source/HourRaster.mc`：共用位图绘制。`HourView` 保留原来的时间、日期和数据行为。
- `designs/shichen-watchface/fr255-raster.js`：从上述正式 PNG 与 `raster.json` 自动生成，供原型按相同坐标裁剪、合成；直接打开本地 HTML 也可使用。

```sh
python3 scripts/generate_resources.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/build.py --device fr255 --test
python3 scripts/simulate.py --theme hour-white --device fr255 --test
python3 scripts/build.py --device fr255

# 仅更新网页内嵌资源和 README 效果图，无需重新生成设备资源
python3 scripts/mip_resources.py --prototype-only
node designs/shichen-watchface/export-previews.mjs
```

`mip_resources.py --verify` 检查三个主题、正常/省电共 72 个圆环场景的补丁重建，所有字体的字符覆盖、图集边界、调色板和数字过渡色。SDK 原生测试遍历 12 时辰的正常→省电→唤醒，同时绘制低电量、最大值与缺失数据，并断言没有退回旧字体。

固定场景截图用模拟器 File → Save Screen Capture 保存原始 260px 图；随后逐像素检查实际位图裁剪、文字位置和颜色，例如：

```sh
python3 scripts/mip_resources.py --verify-capture build/preview/fr255-raster-probe/hour-color-after-normal.png --theme hour-color --scene normal
```

## 验收边界

本轮已完成：Python 8 项检查全部通过，包含原型内嵌资源与正式 PNG、定位表的一致性；三个主题分别通过 SDK 原生 7 项测试（共 21 项），含全天时辰逻辑和 FR255 绘制切换。原生测试的 VM 内存峰值为白款 40,944 字节、黑金款 40,872 字节、彩色款 43,928 字节，低于该设备 131,072 字节限额；图像另由设备的资源池管理，全部状态切换未出现资源分配失败。

三款正常/省电、彩色款最大数据与缺失数据共 8 张原生截图，均与资源合成的固定场景逐像素一致。此检查针对 SDK 的真实裁剪坐标、字形落点、资源选色和最终输出，不以浏览器预览代替设备模拟器。FR255 三款正式编译无警告、无错误；通用路径的 fēnix 3 HR、fēnix 6、Venu 也已通过编译，其中 fēnix 6 与 Venu 已在原生模拟器检查正常显示。

同步后的原型导出六张 260px 正常/省电图，与对应原生截图的像素差异均为 0；454px 全彩预览和字体候选图同步重新生成。原型脚本另检查全天每刻、两个显示状态、三个主题共 576 种组合，以及时间切换、低电量、缺失心率、最大步数和尺寸/字体控件；检查基于脚本与离线导出，未进行浏览器手动交互验收。

原生截图与诊断输出保存在 `build/preview/fr255-raster-probe/`。2026-09-23 用户在 FR255 标准版真机上确认效果明显改善，随后同步原型与 README。260px 和有限灰阶仍会留下细小台阶；网页复用像素资源可核对字形与位置，环境光下的显色及续航仍需以真机为准。

侧载包仍使用 `build/install/fr255/hour-white.prg`、`hour-black.prg`、`hour-color.prg`，三款应用 ID 保持不变。导出的商店包本次不更新。
