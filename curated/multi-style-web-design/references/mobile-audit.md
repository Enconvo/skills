# Mobile responsive audit

A CDP-based script that loads every variant at iPhone 14 viewport (393×852) and reports any element whose `getBoundingClientRect().right` exceeds `clientWidth` — i.e. content that would be sliced off the right edge of the screen.

## Why this exists

The defensive pattern `html { overflow-x: clip }` (Phase 4.5) prevents a wide nav from offsetting body centering — but it also **silently hides** any other overflow. So an element that pushes 50px past the viewport edge looks fine in dev tools (no horizontal scrollbar) but is actually slicing user-facing content. See SKILL.md §B23 for the canonical example (hero-stats grid with `Beginner→Intermediate` getting cut on iPhone).

## Run it

```bash
node scripts/audit_mobile.mjs   # writes mobile-audit.json + prints to stderr
```

Prints one line per variant:
```
[v1-brutalist-index] viewport=393 bodyW=393 overflow=4
    h1.title-layer.back  right=395  w=398  text="Money,Markets &Mechanics."
    div.stat  right=432  w=134  text="Concepts52"
```

`overflow=0` is clean. Anything else needs investigation.

## Reading the output

**Real bugs** to fix:
- `.hero-stats .stat`, `.stat .v` — hero KPI grid not responsive (B23 fix)
- `h1.title`, `.title-layer`, `.row*` — headlines wrap incorrectly or have nowrap + large clamp upper bound
- `.lede`, `.summary` — long-string body copy in fixed-width container
- `figure`, `.full-img`, `.cinema` — full-bleed images with negative margins not scaling with parent padding

**False positives** (visual is fine, audit catches the boundingRect):
- `.blob`, decorative `::before` elements with negative `top`/`right` inside a parent that has `overflow: hidden` — the visual is clipped, but rect still reports the off-screen position
- `.spread-07 .figure` and similar inside a `position: relative; overflow: hidden` parent — same reason

If unsure: take a real screenshot at 393px viewport and look. If content is visually present and not sliced, it's a false positive. If content is missing or sliced, it's real.

## The script

```javascript
// scripts/audit_mobile.mjs
import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';

const variants = [
  'v1-brutalist-index','v2-editorial-nightscape','v3-glass-library','v4-studio-black',
  'v5-swiss-modernist','v6-riso-pop','v7-atelier-couture','v8-studio-spectrum',
  'v9-stadium','v10-neon-arcade','v11-panel','v12-gallery-white','v13-soft-organic',
  'v14-quartermaster','v15-holographic-future','v16-reportage','v17-vivieen-hosted'
];

const port = 9222 + Math.floor(Math.random() * 1000);
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
  '--headless=new','--disable-gpu','--hide-scrollbars',
  `--remote-debugging-port=${port}`,'--user-data-dir=/tmp/chrome-audit-' + Date.now(),
  'about:blank'
], { stdio: 'ignore' });
await new Promise(r => setTimeout(r, 2500));

const detector = `
(() => {
  const W = document.documentElement.clientWidth;
  const overflow = [];
  document.querySelectorAll('*').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return;
    if (r.right > W + 1) {
      const tag = el.tagName.toLowerCase();
      const cls = el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\\s+/).slice(0,3).join('.') : '';
      const id = el.id ? '#' + el.id : '';
      overflow.push({ sel: tag + id + cls, right: Math.round(r.right), w: Math.round(r.width), text: (el.textContent||'').slice(0,40).replace(/\\s+/g,' ') });
    }
  });
  const map = new Map();
  for (const o of overflow) {
    const cur = map.get(o.sel);
    if (!cur || o.right > cur.right) map.set(o.sel, o);
  }
  return { viewport: W, body: document.body.scrollWidth, overflow: [...map.values()].slice(0, 8) };
})()
`;

const results = {};
for (const v of variants) {
  const tabsR = await fetch(`http://127.0.0.1:${port}/json/new?http://127.0.0.1:7531/${v}/`, { method: 'PUT' });
  const tab = await tabsR.json();
  await new Promise((resolve, reject) => {
    const ws = new WebSocket(tab.webSocketDebuggerUrl);
    let id = 1; const pending = new Map();
    ws.onopen = async () => {
      try {
        await send('Emulation.setDeviceMetricsOverride', { width: 393, height: 852, deviceScaleFactor: 2, mobile: true });
        await send('Page.enable', {});
        await send('Page.reload', {});
        await new Promise(r => setTimeout(r, 2500));
        const result = await send('Runtime.evaluate', { expression: detector, returnByValue: true });
        process.stderr.write(`[${v}] viewport=${result.result.value.viewport} bodyW=${result.result.value.body} overflow=${result.result.value.overflow.length}\n`);
        for (const o of result.result.value.overflow.slice(0, 5)) {
          process.stderr.write(`    ${o.sel}  right=${o.right}  w=${o.w}  text="${o.text}"\n`);
        }
        results[v] = result.result.value;
        ws.close(); resolve();
      } catch (e) { reject(e); }
    };
    ws.onmessage = (ev) => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m.result); pending.delete(m.id); } };
    ws.onerror = (e) => reject(e);
    function send(method, params) { return new Promise(res => { const myId = id++; pending.set(myId, res); ws.send(JSON.stringify({ id: myId, method, params })); }); }
  });
  await fetch(`http://127.0.0.1:${port}/json/close/${tab.id}`);
}
writeFileSync('mobile-audit.json', JSON.stringify(results, null, 2));
chrome.kill();
```

## When to run

- **Before every variant ships** — once per variant, ideally as part of the `init_project.py` post-step
- **After any layout change** that touches `.hero-stats`, full-bleed figures, or grid scaffolds
- **As a regression suite** when a critical bug like B23 is patched — verify all variants stay clean

## Acceptance criteria

A variant ships only when `bodyW === viewport` (393) AND `overflow.length === 0` for non-decorative selectors. Decorative-overflow false positives (blobs, gradient washes inside `overflow: hidden` parents) are documented per-variant if persistent.
