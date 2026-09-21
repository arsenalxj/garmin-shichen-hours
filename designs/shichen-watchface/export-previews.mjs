// 从「十二时辰表盘-三版对照.html」提取 faceSVG 渲染逻辑，导出三版正常/省电状态 PNG。
// 用法：node export-previews.mjs   （需要 designs/ 已在 http://localhost:4311 提供访问，
// 以及本机装有 Microsoft Edge 用于光栅化；PNG 输出到本目录 png/）
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

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
const api = new Function('document', 'location', 'window', `${src}\nreturn { faceSVG, THEMES, state };`)(
  documentStub, { search: '' }, {});

const pngDir = path.join(here, 'png');
fs.mkdirSync(pngDir, { recursive: true });

// SVG 里用了原型页的本地开源字体，包装页要带上同一组 @font-face（相对 png/ 目录）
const FONTS = `<style>
@font-face{font-family:'Noto Serif SC';src:url('../fonts/NotoSerifSC-var.woff2') format('woff2');font-weight:100 900}
@font-face{font-family:'Noto Sans SC';src:url('../fonts/NotoSansSC-var.woff2') format('woff2');font-weight:100 900}
</style>`;

const EDGE = '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge';
const jobs = [];
for (const theme of api.THEMES) {
  for (const aod of [false, true]) {
    for (const px of [454, 208]) {
      jobs.push({ theme, aod, px });
    }
  }
}

for (const { theme, aod, px } of jobs) {
  api.state.aod = aod;
  const svg = api.faceSVG(theme, px);
  const name = `${theme.slug}${aod ? '-aod' : ''}-${px}`;
  const wrapper = path.join(pngDir, `_tmp_${name}.html`);
  fs.writeFileSync(wrapper, `<!DOCTYPE html><html><head><meta charset="UTF-8">${FONTS}</head><body style="margin:0">${svg}</body></html>`);
  const url = `http://localhost:4311/shichen-watchface/png/_tmp_${name}.html`;
  execFileSync(EDGE, ['--headless', '--disable-gpu', '--force-device-scale-factor=2',
    `--window-size=${px},${px}`, '--virtual-time-budget=3000',
    `--screenshot=${path.join(pngDir, name + '.png')}`, url], { stdio: 'ignore' });
  fs.unlinkSync(wrapper);
  console.log('✓', name + '.png');
}
