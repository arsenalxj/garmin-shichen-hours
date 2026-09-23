# 字体来源与授权

表盘使用已确认 HTML 原型中的字体，原始 WOFF2 位于 `designs/shichen-watchface/fonts/`。

| 字体 | 用途 | 来源 | 授权 |
|---|---|---|---|
| 霞鹜文楷 LXGW WenKai Medium | 启动器图标 | <https://github.com/lxgw/LxgwWenKai> | `lxgwwenkai-OFL.txt` |
| Noto Serif SC | 宣纸留白款数字时间 | <https://github.com/notofonts/noto-cjk/tree/main/Serif> | `notoserifsc-OFL.txt` |
| Noto Sans SC | 玄天黑金款与时辰色款数字时间、日期、电量与步数行，以及环上时辰字与小注「子时 · 初刻」 | <https://github.com/google/fonts/tree/main/ofl/notosanssc> | `notosanssc-OFL.txt` |

三者均采用 SIL Open Font License 1.1。可商用及随应用分发；授权文本须随源码与衍生字体保留。

资源脚本从原型文件按字重实例化，仅为表盘所需字形生成 BMFont。霞鹜文楷是静态 Medium，没有可变字重。环上当前时辰靠放大与强调色区分。位图字体名称为 Shichen 加资源名，未使用三个原字体的保留字体名，也未改写原型字形或改用系统字体。生成的中间 TTF 仅保存在 `.tools/font-cache/`。

原型与成品的环上时辰字、小注均默认使用 Noto Sans SC，字号按实测墨迹标定；原型中的楷体等选项仅用于字体候选对照。260px MIP 默认直接复用 FR255 正式像素资源，其他尺寸对齐通用字体的字重与字号。MIP 是彩色屏，普通路径的“1 位”指字体的覆盖掩码。

普通路径的小字采用 300 字重、MIP 阈值 48，尽量保证二值化后的连续性；它不能保证每个汉字的笔画都均匀，也无法消除大数字的硬边。中央时间采用衬线 600、无衬线 300。

FR255 标准版采用专用的 64 色预混色资源：字形先与实际背景混合，边缘只使用设备可以显示的颜色，再以不透明像素绘制。小字改用 400 字重，无衬线时间正常/省电分别用 350/300，衬线时间沿用 600/450。保留灰阶覆盖后可以使用中等字重，减少二值化造成的笔画跳变。环上文字随圆环预生成，中央文字仍逐字动态排版；完整生成和验证说明见 `plans/FR255_RENDERING.md`。

AMOLED 沿用通用抗锯齿字体资源。启动器图标仍用楷体。

`NOTICES.txt` 保留原型字体文件 name 表中的原始版权声明（含霞鹜文楷所衍生的 Klee One 部分）。完整声明及 OFL 文本也嵌入应用字符串资源 `FontLicense`；导出与侧载包另附可直接阅读的授权文件。
