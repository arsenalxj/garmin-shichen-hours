// 从「十二时辰表盘-三版对照.html」提取 faceSVG 渲染逻辑，导出三版正常/省电状态 PNG。
// 用法：node designs/shichen-watchface/export-previews.mjs
// 需要本机 Microsoft Edge；直接打开临时本地页，无需 HTTP 服务或 Node 依赖。
// 260px 使用 FR255 正式像素资源，454px 使用通用矢量预览；输出保持原始像素尺寸。
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const html = fs.readFileSync(path.join(here, '十二时辰表盘-三版对照.html'), 'utf8');
const src = html.match(/<script>([\s\S]*)<\/script>/)[1];

// 最小 DOM 桩：让脚本里的控件绑定与 render() 空转
const stub = new Proxy(function () {}, {
  get: (t, p) => (p === Symbol.toPrimitive ? () => '' : stub),
  set: () => true,
  apply: () => stub,
});
const documentStub = { querySelector: () => stub, querySelectorAll: () => [], createElement: () => stub };
const previewWindow = {};
new Function('window', fs.readFileSync(path.join(here, 'fr255-raster.js'), 'utf8'))(previewWindow);
const api = new Function('document', 'location', 'window', `${src}\nreturn { faceSVG, THEMES, RING_FONTS, state };`)(
  documentStub, { search: '' }, previewWindow);
api.state.date = '2026-09-21';

const pngDir = path.join(here, 'png');
fs.mkdirSync(pngDir, { recursive: true });

// SVG 里用了原型页的本地开源字体，包装页要带上同一组 @font-face（相对 png/ 目录）
const FONTS = `<style>
@font-face{font-family:'Noto Serif SC';src:url('../fonts/NotoSerifSC-var.woff2') format('woff2');font-weight:100 900}
@font-face{font-family:'Noto Sans SC';src:url('../fonts/NotoSansSC-var.woff2') format('woff2');font-weight:100 900}
@font-face{font-family:'LXGW WenKai';src:url('../fonts/LXGWWenKai-Medium.woff2') format('woff2');font-weight:400 700}
@font-face{font-family:'Zhuque Fangsong';src:url('../fonts/ZhuqueFangsong-Regular.woff2') format('woff2');font-weight:400 700}
@font-face{font-family:'Yozai';src:url('../fonts/Yozai-Medium.woff2') format('woff2');font-weight:400 700}
</style>`;

const EDGE = process.env.EDGE_BIN || '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge';
const jobs = [];
for (const theme of api.THEMES) {
  for (const aod of [false, true]) {
    for (const px of [454, 260]) {
      jobs.push({ theme, aod, px });
    }
  }
}

function shoot(name, svg, px) {
  const wrapper = path.join(pngDir, `_tmp_${name}.html`);
  fs.writeFileSync(wrapper, `<!DOCTYPE html><html><head><meta charset="UTF-8">${FONTS}</head><body style="margin:0">${svg}</body></html>`);
  try {
    execFileSync(EDGE, ['--headless', '--disable-gpu', '--force-device-scale-factor=1',
      `--window-size=${px},${px}`, '--hide-scrollbars', '--virtual-time-budget=3000',
      `--screenshot=${path.join(pngDir, name + '.png')}`, pathToFileURL(wrapper).href], { stdio: 'ignore' });
  } finally {
    fs.unlinkSync(wrapper);
  }
  console.log('✓', name + '.png');
}

for (const { theme, aod, px } of jobs) {
  api.state.aod = aod;
  api.state.mip = px === 260;
  shoot(`${theme.slug}${aod ? '-aod' : ''}-${px}`, api.faceSVG(theme, px), px);
}

// 环上字体候选对照：同一版式换字体，按 ?ring=<slug> 的状态各出一张。
api.state.aod = false;
api.state.mip = false;
for (const { slug } of api.RING_FONTS) {
  api.state.ringFont = slug;
  shoot(`ring-${slug}-454`, api.faceSVG(api.THEMES[0], 454), 454);
}
api.state.ringFont = api.RING_FONTS[0].slug;

// 同步候选字体对照图，标注当前成品字体；复用项目已有 Pillow 环境。
execFileSync(path.resolve(here, '../../.tools/venv/bin/python'), ['-c', `
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
root, target = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(root / 'scripts'))
import generate_resources as gen
fonts = json.loads(sys.argv[3])
sheet = Image.new('RGB', (948, 304), 'white')
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype(str(gen.ttf('Sans', 400)), 18)
for i, candidate in enumerate(fonts):
    x, y = 12 + (i % 3) * 312, 12 + (i // 3) * 146
    crop = Image.open(target / ('ring-' + candidate['slug'] + '-454.png')).crop((0, 0, 454, 144))
    sheet.paste(crop.resize((300, 95), Image.Resampling.LANCZOS), (x, y))
    label = candidate['name'] + ('（当前成品）' if candidate['slug'] == 'sans' else '')
    draw.text((x, y + 100), label, fill='#1D1B1C', font=font)
sheet.save(target / 'ring-fonts-compare.png')
`, path.resolve(here, '../..'), pngDir, JSON.stringify(api.RING_FONTS)], { stdio: 'inherit' });
console.log('✓ ring-fonts-compare.png');
