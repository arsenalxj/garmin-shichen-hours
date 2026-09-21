# 字体来源与授权

表盘沿用已确认 HTML 原型中的 Noto Serif SC 与 Noto Sans SC 字体，原始 WOFF2 位于 `designs/shichen-watchface/fonts/`。

- Noto Sans SC：<https://github.com/google/fonts/tree/main/ofl/notosanssc>，授权见 `notosanssc-OFL.txt`。
- Noto Serif SC：<https://github.com/notofonts/noto-cjk/tree/main/Serif>，授权见 `notoserifsc-OFL.txt`。
- 两者均采用 SIL Open Font License 1.1。可商用及随应用分发；授权文本须随源码与衍生字体保留。

资源脚本从原型文件按字重实例化，仅为表盘所需字形生成 BMFont。位图字体名称为 Shichen 加资源名；未改写原型字形或改用系统字体。生成的中间 TTF 仅保存在 `.tools/font-cache/`。

`NOTICES.txt` 保留原型字体文件 name 表中的 Adobe 版权声明。完整声明及 OFL 文本也嵌入应用字符串资源 `FontLicense`；导出时另附可直接阅读的授权文件。
