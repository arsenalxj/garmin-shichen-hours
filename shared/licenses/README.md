# 字体来源与授权

表盘使用已确认 HTML 原型中的字体，原始 WOFF2 位于 `designs/shichen-watchface/fonts/`。

| 字体 | 用途 | 来源 | 授权 |
|---|---|---|---|
| 霞鹜文楷 LXGW WenKai Medium | 环上时辰字、小注「子时 · 初刻」、启动器图标 | <https://github.com/lxgw/LxgwWenKai> | `lxgwwenkai-OFL.txt` |
| Noto Serif SC | 宣纸留白款数字时间 | <https://github.com/notofonts/noto-cjk/tree/main/Serif> | `notoserifsc-OFL.txt` |
| Noto Sans SC | 玄天黑金款与时辰色款数字时间、日期、电量与步数行 | <https://github.com/google/fonts/tree/main/ofl/notosanssc> | `notosanssc-OFL.txt` |

三者均采用 SIL Open Font License 1.1。可商用及随应用分发；授权文本须随源码与衍生字体保留。

资源脚本从原型文件按字重实例化，仅为表盘所需字形生成 BMFont。霞鹜文楷是静态 Medium，没有可变字重，环上当前时辰靠放大与强调色区分。位图字体名称为 Shichen 加资源名，未使用三个原字体的保留字体名，也未改写原型字形或改用系统字体。生成的中间 TTF 仅保存在 `.tools/font-cache/`。

`NOTICES.txt` 保留原型字体文件 name 表中的原始版权声明（含霞鹜文楷所衍生的 Klee One 部分）。完整声明及 OFL 文本也嵌入应用字符串资源 `FontLicense`；导出与侧载包另附可直接阅读的授权文件。
