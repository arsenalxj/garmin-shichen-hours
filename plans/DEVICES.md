# 圆屏表盘设备包下载清单

核对日期：2026-09-21。适用于 `hour-white`、`hour-black`、`hour-color`，同一份设备包供三个表盘共用。

来源：[佳明官方兼容设备表](https://developer.garmin.com/connect-iq/compatible-devices/)。只纳入屏幕形状为 `round` 的手表条目；按确认排除三款 8 色机型后，共 121 个开发目标，其中 120 个在本机已发现设备资料，1 个尚未发现。一个条目可能合并多个共用开发包的硬件型号。

“本机已有资料”表示已存在 `compiler.json`、`simulator.json`，并确认支持 `watchFace`，不等于已经完成本项目的编译或模拟器验证。下载完成状态以 SDK Manager 显示为准。

## 当前开发所需代表机型已齐备

已具备全部九种受支持屏幕尺寸的代表资料：fēnix 3 HR（218、16 色）、fēnix 5（240）、fēnix 6（260）、fēnix 6X Pro（280）、Venu 2S（360）、Venu / vívoactive 6（390）、fēnix 8 43mm（416）、fēnix 8 47mm / 51mm（454）、fēnix 9 Pro 51mm（466）。

Venu 第一代用于验证旧款 AMOLED 的烧屏保护与息屏恢复。原 208 像素的三款 8 色目标已按确认排除。

## 发布前完整清单

为覆盖全部圆屏目标，最终需要补齐下列未勾选条目。按 SDK Manager 的 API 分组展开，逐项下载；各组同时含有其他屏形或码表，因此不要使用整组下载。已勾选条目表示本机已有资料。

### API level 6.0（27 项，待补 0 项）

- [x] D2™ Mach 2 Pro — 454 × 454；AMOLED
- [x] Enduro™ 3 — 280 × 280；MIP 64 色
- [x] fēnix® 8 43mm — 416 × 416；AMOLED
- [x] fēnix® 8 47mm / 51mm / tactix® 8 47mm / 51mm / quatix® 8 47mm / 51mm — 454 × 454；AMOLED
- [x] fēnix® 8 Pro 47mm / 51mm / MicroLED / quatix® 8 Pro 47mm / 51mm — 454 × 454；AMOLED
- [x] fēnix® 8 Solar 47mm — 260 × 260；MIP 64 色
- [x] fēnix® 8 Solar 51mm / tactix® 8 Solar 51mm — 280 × 280；MIP 64 色
- [x] fēnix® 9 43mm — 416 × 416；AMOLED
- [x] fēnix® 9 47mm / 51mm — 454 × 454；AMOLED
- [x] fēnix® 9 Pro 43mm — 416 × 416；AMOLED
- [x] fēnix® 9 Pro 47mm — 454 × 454；AMOLED
- [x] fēnix® 9 Pro 51mm — 466 × 466；AMOLED
- [x] fēnix® 9 Pro Solar 47mm — 260 × 260；MIP 64 色
- [x] fēnix® 9 Pro Solar 51mm — 280 × 280；MIP 64 色
- [x] fēnix® E — 416 × 416；AMOLED
- [x] Forerunner® 170 — 390 × 390；AMOLED
- [x] Forerunner® 170 Music — 390 × 390；AMOLED
- [x] Forerunner® 570 42mm — 390 × 390；AMOLED
- [x] Forerunner® 570 47mm — 454 × 454；AMOLED
- [x] Forerunner® 70 — 390 × 390；AMOLED
- [x] Forerunner® 970 — 454 × 454；AMOLED
- [x] Instinct® 3 AMOLED 45mm — 390 × 390；AMOLED
- [x] Instinct® 3 AMOLED 50mm — 416 × 416；AMOLED
- [x] Instinct® Crossover AMOLED — 390 × 390；AMOLED
- [x] Venu® 4 41mm — 390 × 390；AMOLED
- [x] Venu® 4 45mm / D2™ Air X15 — 454 × 454；AMOLED
- [x] vívoactive® 6 — 390 × 390；AMOLED

### API level 5.2（29 项，待补 0 项）

- [x] D2™ Mach 1 — 416 × 416；AMOLED
- [x] D2™ Mach 2 — 454 × 454；AMOLED
- [x] epix™ (Gen 2) / quatix® 7 Sapphire — 416 × 416；AMOLED
- [x] epix™ Pro (Gen 2) 42mm — 390 × 390；AMOLED
- [x] epix™ Pro (Gen 2) 47mm / quatix® 7 Pro — 416 × 416；AMOLED
- [x] epix™ Pro (Gen 2) 51mm / D2™ Mach 1 Pro / tactix® 7 – AMOLED Edition — 454 × 454；AMOLED
- [x] fēnix® 7 / quatix® 7 — 260 × 260；MIP 64 色
- [x] fēnix® 7 Pro — 260 × 260；MIP 64 色
- [x] fēnix® 7 Pro - Solar Edition (no Wi-Fi) — 260 × 260；MIP 64 色
- [x] fēnix® 7S — 240 × 240；MIP 64 色
- [x] fēnix® 7S Pro — 240 × 240；MIP 64 色
- [x] fēnix® 7X / tactix® 7 / quatix® 7X Solar / Enduro™ 2 — 280 × 280；MIP 64 色
- [x] fēnix® 7X Pro — 280 × 280；MIP 64 色
- [x] fēnix® 7X Pro - Solar Edition (no Wi-Fi) — 280 × 280；MIP 64 色
- [x] Forerunner® 165 — 390 × 390；AMOLED
- [x] Forerunner® 165 Music — 390 × 390；AMOLED
- [x] Forerunner® 255 — 260 × 260；MIP 64 色
- [x] Forerunner® 255 Music — 260 × 260；MIP 64 色
- [x] Forerunner® 255s — 218 × 218；MIP 64 色
- [x] Forerunner® 255s Music — 218 × 218；MIP 64 色
- [x] Forerunner® 265 — 416 × 416；AMOLED
- [x] Forerunner® 265s — 360 × 360；AMOLED
- [x] Forerunner® 955 / Solar — 260 × 260；MIP 64 色
- [x] Forerunner® 965 — 454 × 454；AMOLED
- [x] MARQ® (Gen 2) Athlete / Adventurer / Captain / Golfer / Carbon Edition / Commander - Carbon Edition — 390 × 390；AMOLED
- [x] MARQ® (Gen 2) Aviator — 390 × 390；AMOLED
- [x] Venu® 3 — 454 × 454；AMOLED
- [x] Venu® 3S — 390 × 390；AMOLED
- [x] vívoactive® 5 — 390 × 390；AMOLED

### API level 5.1（6 项，待补 0 项）

- [x] Approach® S50 — 390 × 390；AMOLED
- [x] Approach® S70 42mm — 390 × 390；AMOLED
- [x] Approach® S70 47mm — 454 × 454；AMOLED
- [x] Descent™ G2 — 390 × 390；AMOLED
- [x] Descent™ Mk3 43mm / Mk3i 43mm — 390 × 390；AMOLED
- [x] Descent™ Mk3i 51mm — 454 × 454；AMOLED

### API level 5.0（4 项，待补 0 项）

- [x] D2™ Air X10 — 416 × 416；AMOLED
- [x] Venu® 2 — 416 × 416；AMOLED
- [x] Venu® 2 Plus — 416 × 416；AMOLED
- [x] Venu® 2S — 360 × 360；AMOLED

### API level 3.4（17 项，待补 0 项）

- [x] Descent™ Mk2 / Mk2i — 280 × 280；MIP 64 色
- [x] Descent™ Mk2 S — 240 × 240；MIP 64 色
- [x] Enduro™ — 280 × 280；MIP 64 色
- [x] fēnix® 6 / 6 Solar / 6 Dual Power — 260 × 260；MIP 64 色
- [x] fēnix® 6 Pro / 6 Sapphire / 6 Pro Solar / 6 Pro Dual Power / quatix® 6 — 260 × 260；MIP 64 色
- [x] fēnix® 6S / 6S Solar / 6S Dual Power — 240 × 240；MIP 64 色
- [x] fēnix® 6S Pro / 6S Sapphire / 6S Pro Solar / 6S Pro Dual Power — 240 × 240；MIP 64 色
- [x] fēnix® 6X Pro / 6X Sapphire / 6X Pro Solar / tactix® Delta Sapphire / Delta Solar / Delta Solar - Ballistics Edition / quatix® 6X / 6X Solar / 6X Dual Power — 280 × 280；MIP 64 色
- [x] Forerunner® 945 LTE — 240 × 240；MIP 64 色
- [x] MARQ® Adventurer — 240 × 240；MIP 64 色
- [x] MARQ® Athlete — 240 × 240；MIP 64 色
- [x] MARQ® Aviator — 240 × 240；MIP 64 色
- [x] MARQ® Captain / MARQ® Captain: American Magic Edition — 240 × 240；MIP 64 色
- [x] MARQ® Commander — 240 × 240；MIP 64 色
- [x] MARQ® Driver — 240 × 240；MIP 64 色
- [x] MARQ® Expedition — 240 × 240；MIP 64 色
- [x] MARQ® Golfer — 240 × 240；MIP 64 色

### API level 3.3（15 项，待补 1 项）

- [x] Captain Marvel — 218 × 218；MIP 64 色
- [x] Darth Vader™ — 260 × 260；MIP 64 色
- [x] fēnix® 5 Plus — 240 × 240；MIP 64 色
- [x] fēnix® 5S Plus — 240 × 240；MIP 64 色
- [x] fēnix® 5X Plus — 240 × 240；MIP 64 色
- [x] First Avenger — 260 × 260；MIP 64 色
- [x] Forerunner® 245 — 240 × 240；MIP 64 色
- [x] Forerunner® 245 Music — 240 × 240；MIP 64 色
- [x] Forerunner® 745 — 240 × 240；MIP 64 色
- [x] Forerunner® 945 — 240 × 240；MIP 64 色
- [x] Rey™ — 218 × 218；MIP 64 色
- [x] Venu® — 390 × 390；AMOLED
- [ ] Venu® Mercedes-Benz® Collection — 390 × 390；AMOLED
- [x] vívoactive® 4 — 260 × 260；MIP 64 色
- [x] vívoactive® 4S — 218 × 218；MIP 64 色

### API level 3.2（3 项，待补 0 项）

- [x] D2™ Air — 390 × 390；AMOLED
- [x] Forerunner® 645 Music — 240 × 240；MIP 64 色
- [x] vívoactive® 3 Music — 240 × 240；MIP 64 色

### API level 3.1（12 项，待补 0 项）

- [x] D2™ Delta — 240 × 240；MIP 64 色
- [x] D2™ Delta PX — 240 × 240；MIP 64 色
- [x] D2™ Delta S — 240 × 240；MIP 64 色
- [x] Descent™ Mk1 — 240 × 240；MIP 64 色
- [x] fēnix® 5 / quatix® 5 — 240 × 240；MIP 64 色
- [x] fēnix® 5S — 218 × 218；MIP 64 色
- [x] fēnix® 5X / tactix® Charlie — 240 × 240；MIP 64 色
- [x] fēnix® Chronos — 218 × 218；MIP 64 色
- [x] Forerunner® 645 — 240 × 240；MIP 64 色
- [x] Forerunner® 935 — 240 × 240；MIP 64 色
- [x] vívoactive® 3 — 240 × 240；MIP 64 色
- [x] vívoactive® 3 Music LTE — 240 × 240；MIP 64 色

### API level 3.0（3 项，待补 0 项）

- [x] Approach® S62 — 260 × 260；MIP 64 色
- [x] D2™ Charlie — 240 × 240；MIP 64 色
- [x] vívoactive® 3 Mercedes-Benz® Collection — 240 × 240；MIP 64 色

### API level 2.4（1 项，待补 0 项）

- [x] Approach® S60 — 240 × 240；MIP 64 色

### API level 1.4（4 项，待补 0 项）

- [x] D2™ Bravo — 218 × 218；MIP 16 色
- [x] D2™ Bravo Titanium — 218 × 218；MIP 16 色
- [x] fēnix® 3 / tactix® Bravo / quatix® 3 — 218 × 218；MIP 16 色
- [x] fēnix® 3 HR — 218 × 218；MIP 16 色

## 不在本项目下载范围

按用户确认，Forerunner 45、Forerunner 55、Garmin Swim 2 三款 8 色手表不支持；已下载的设备包可保留，不参与本项目生成或构建。

Edge、GPSMAP、eTrex 等非手表设备，以及官方标记为 rectangle、semi-round、semi-octagon 的手表。Instinct 系列应按具体型号区分：本清单包含其圆屏 AMOLED 型号，其他屏形不纳入。
