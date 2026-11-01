// Render SVG/HTML files to PNG with Playwright Chromium.
// usage: node render.js <in.svg|in.html> <out.png> <width> <height|auto> <light|dark>
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [inp, out, w, h, scheme] = process.argv.slice(2);
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: +w, height: h === 'auto' ? 800 : +h },
                                   colorScheme: scheme || 'light', deviceScaleFactor: 1 });
  const p = await ctx.newPage();
  await p.goto('file://' + path.resolve(inp));
  await p.screenshot({ path: out, fullPage: h === 'auto' });
  await b.close();
})();
