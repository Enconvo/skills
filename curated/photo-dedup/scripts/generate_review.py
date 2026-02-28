#!/usr/bin/env python3
"""
Photo Dedup — Static Review Page Generator
Generates a self-contained HTML file for reviewing duplicate photo groups.
No server needed — open the HTML directly in any browser.
"""

import argparse
import base64
import io
import json
import sys
import webbrowser
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: pip3 install Pillow pillow-heif")
    sys.exit(1)

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass


# ── CSS ──────────────────────────────────────────────────────────────────────
CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
  background: #f5f5f7;
  color: #1d1d1f;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}
.wrap { max-width: 1120px; margin: 0 auto; padding: 0 24px; }

/* Header */
.hd { background: #fff; border-bottom: 1px solid #d2d2d7; padding: 28px 0 24px; }
.hd h1 { font-size: 26px; font-weight: 700; display: flex; align-items: center; gap: 10px; }
.hd h1 .icon { font-size: 30px; }
.hd .sub { color: #86868b; font-size: 14px; margin-top: 4px; }
.stats { display: flex; gap: 36px; margin-top: 18px; }
.stat .val { font-size: 28px; font-weight: 700; color: #1d1d1f; line-height: 1.2; }
.stat .lbl { font-size: 11px; color: #86868b; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }

/* Toolbar */
.tb {
  position: sticky; top: 0; z-index: 100;
  background: rgba(255,255,255,0.82);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid rgba(0,0,0,0.08);
  padding: 10px 0;
}
.tb-inner { display: flex; align-items: center; gap: 8px; }
.sel-count { font-size: 14px; color: #86868b; margin-right: auto; }
.sel-count strong { color: #1d1d1f; font-weight: 600; }

/* Buttons */
.btn {
  display: inline-flex; align-items: center; gap: 5px;
  border: none; border-radius: 8px; padding: 7px 14px;
  font-size: 13px; font-weight: 500; font-family: inherit;
  cursor: pointer; transition: all 0.12s; white-space: nowrap;
}
.btn-o { background: rgba(0,0,0,0.05); color: #1d1d1f; }
.btn-o:hover { background: rgba(0,0,0,0.09); }
.btn-p { background: #007AFF; color: #fff; }
.btn-p:hover { background: #0062d1; }
.btn-p:disabled { background: #d2d2d7; color: #a1a1a6; cursor: default; }

/* Main */
main { padding: 20px 0 80px; }

/* Group */
.group {
  background: #fff; border-radius: 14px; margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  overflow: hidden;
}
.gh {
  padding: 13px 20px; display: flex; align-items: center;
  justify-content: space-between; border-bottom: 1px solid #f0f0f2;
}
.gt { font-size: 15px; font-weight: 600; }
.gc { font-size: 13px; color: #86868b; font-weight: 400; margin-left: 8px; }
.grid { display: flex; gap: 10px; padding: 14px 20px 18px; flex-wrap: wrap; }

/* Card */
.card {
  position: relative; border-radius: 10px; overflow: hidden;
  cursor: pointer; border: 3px solid transparent;
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.12s;
  background: #f0f0f2;
}
.card:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.1); }
.card.sel { border-color: #007AFF; }

/* Checkmark */
.ck {
  position: absolute; top: 8px; left: 8px;
  width: 24px; height: 24px; border-radius: 50%;
  background: rgba(255,255,255,0.55); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: all 0.15s;
  border: 2px solid rgba(255,255,255,0.8);
}
.card:hover .ck { opacity: 1; }
.card.sel .ck { opacity: 1; background: #007AFF; border-color: #007AFF; }
.ck svg { width: 14px; height: 14px; color: #fff; }

/* Zoom icon */
.zm {
  position: absolute; top: 8px; right: 8px;
  width: 28px; height: 28px; border-radius: 50%;
  background: rgba(0,0,0,0.45); backdrop-filter: blur(4px);
  color: #fff; display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: opacity 0.15s; cursor: zoom-in;
  font-size: 13px; z-index: 5; border: none;
}
.card:hover .zm { opacity: 1; }
.zm:hover { background: rgba(0,0,0,0.65); }

/* Image */
.card img {
  display: block; height: 210px; width: auto;
  min-width: 140px; max-width: 320px; object-fit: cover;
}

/* Card info */
.ci { padding: 7px 10px 4px; display: flex; align-items: center; justify-content: space-between; background: #fff; }
.ci .sz { font-size: 12px; font-weight: 600; color: #1d1d1f; }
.badge {
  font-size: 10px; font-weight: 600; padding: 2px 7px;
  border-radius: 4px; letter-spacing: 0.3px;
}
.badge.best { background: #dbf5db; color: #1a7a2e; }
.fn {
  padding: 0 10px 7px; font-size: 10px; color: #86868b;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

/* Lightbox */
.lb {
  display: none; position: fixed; inset: 0;
  background: rgba(0,0,0,0.92); z-index: 200;
  justify-content: center; align-items: center; cursor: zoom-out;
}
.lb.show { display: flex; }
.lb img { max-width: 92vw; max-height: 92vh; border-radius: 6px; }
.lb .close-hint {
  position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
  color: rgba(255,255,255,0.5); font-size: 13px;
}

/* Toast */
.toast {
  position: fixed; bottom: 28px; left: 50%;
  transform: translateX(-50%) translateY(100px);
  background: #1d1d1f; color: #fff;
  padding: 13px 28px; border-radius: 14px;
  font-size: 14px; font-weight: 500;
  box-shadow: 0 6px 24px rgba(0,0,0,0.35);
  transition: transform 0.35s cubic-bezier(0.4,0,0.2,1);
  z-index: 300; white-space: nowrap; max-width: 90vw;
  overflow: hidden; text-overflow: ellipsis;
}
.toast.show { transform: translateX(-50%) translateY(0); }

/* Hint */
.hint { color: #86868b; font-size: 13px; padding: 12px 20px 0; }
"""

# ── JavaScript ───────────────────────────────────────────────────────────────
JS = """
const CFG = __CFG__;
const sel = new Set();
const allPaths = new Set();

document.querySelectorAll('.card').forEach(c => allPaths.add(c.dataset.path));

function toggle(el) {
  const p = el.dataset.path;
  if (sel.has(p)) { sel.delete(p); el.classList.remove('sel'); }
  else { sel.add(p); el.classList.add('sel'); }
  upd();
}

function openLB(el) {
  document.getElementById('lb-img').src = el.querySelector('img').src;
  document.getElementById('lb').classList.add('show');
}
function closeLB() { document.getElementById('lb').classList.remove('show'); }

function best() {
  document.querySelectorAll('.group').forEach(g => {
    g.querySelectorAll('.card.sel').forEach(c => { sel.delete(c.dataset.path); c.classList.remove('sel'); });
    const first = g.querySelector('.card');
    if (first) { sel.add(first.dataset.path); first.classList.add('sel'); }
  });
  upd();
}

function clearAll() {
  sel.clear();
  document.querySelectorAll('.card.sel').forEach(c => c.classList.remove('sel'));
  upd();
}

function selGroup(gi) {
  document.querySelectorAll('.card[data-group="' + gi + '"]').forEach(c => {
    sel.add(c.dataset.path); c.classList.add('sel');
  });
  upd();
}

function getDeleteList() {
  const toDelete = [];
  allPaths.forEach(p => { if (!sel.has(p)) toDelete.push(p); });
  return toDelete;
}

function upd() {
  const n = sel.size;
  const delCount = getDeleteList().length;
  document.getElementById('cnt').textContent = n;
  document.getElementById('del-cnt').textContent = delCount;
  const btn = document.getElementById('save-btn');
  btn.disabled = n === 0 || delCount === 0;
  btn.textContent = delCount > 0
    ? '\\ud83d\\uddd1\\ufe0f \\u5220\\u9664\\u91cd\\u590d\\u6587\\u4ef6 (' + delCount + ')'
    : '\\ud83d\\uddd1\\ufe0f \\u5220\\u9664\\u91cd\\u590d\\u6587\\u4ef6';
}

function save() {
  if (sel.size === 0) return;
  const toDelete = getDeleteList();
  if (toDelete.length === 0) { toast('\\u6ca1\\u6709\\u9700\\u8981\\u5220\\u9664\\u7684\\u91cd\\u590d\\u6587\\u4ef6'); return; }

  const ok = confirm(
    '\\u786e\\u8ba4\\u5220\\u9664 ' + toDelete.length + ' \\u4e2a\\u91cd\\u590d\\u6587\\u4ef6\\uff1f\\n\\n' +
    '\\u4fdd\\u7559: ' + sel.size + ' \\u5f20\\u7167\\u7247\\n' +
    '\\u5220\\u9664: ' + toDelete.length + ' \\u4e2a\\u91cd\\u590d\\u6587\\u4ef6\\n\\n' +
    '\\u26a0\\ufe0f \\u6b64\\u64cd\\u4f5c\\u4e0d\\u53ef\\u64a4\\u9500\\uff01'
  );
  if (!ok) return;

  const btn = document.getElementById('save-btn');
  btn.disabled = true;
  btn.textContent = '\\u5220\\u9664\\u4e2d...';

  fetch('http://localhost:54535/command/call/enconvo/delete_files', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filePaths: toDelete })
  })
  .then(r => {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  })
  .then(data => {
    const results = data.data || [];
    const ok = results.filter(r => r.success).length;
    const fail = results.filter(r => !r.success).length;

    // Remove deleted cards from page
    toDelete.forEach(p => {
      const card = document.querySelector('.card[data-path="' + CSS.escape(p) + '"]');
      if (card) card.remove();
      allPaths.delete(p);
    });

    // Remove empty groups
    document.querySelectorAll('.group').forEach(g => {
      if (g.querySelectorAll('.card').length === 0) g.remove();
    });

    if (fail > 0) {
      toast('\\u2705 \\u5df2\\u5220\\u9664 ' + ok + ' \\u4e2a\\u6587\\u4ef6\\uff0c' + fail + ' \\u4e2a\\u5931\\u8d25');
    } else {
      toast('\\u2705 \\u5df2\\u6210\\u529f\\u5220\\u9664 ' + ok + ' \\u4e2a\\u91cd\\u590d\\u6587\\u4ef6');
    }
    upd();
  })
  .catch(err => {
    toast('\\u274c \\u5220\\u9664\\u5931\\u8d25: ' + err.message);
    btn.disabled = false;
    upd();
  });
}

function toast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(t._tid);
  t._tid = setTimeout(() => t.classList.remove('show'), 5000);
}

document.addEventListener('keydown', e => { if (e.key === 'Escape') closeLB(); });

best();
"""


def make_thumb(filepath, max_size=800):
    """Create a base64-encoded JPEG thumbnail."""
    try:
        img = Image.open(filepath)
        img.thumbnail((max_size, max_size), Image.LANCZOS)
        buf = io.BytesIO()
        img.convert('RGB').save(buf, format='JPEG', quality=82)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print(f"  Warning: {filepath.name}: {e}")
        return ""


def find_file(source_dir, fname, cluster=None):
    """Find a file by name, using paths from cluster if available."""
    if cluster and 'paths' in cluster and fname in cluster['paths']:
        p = Path(cluster['paths'][fname])
        if p.exists():
            return p
    matches = list(source_dir.rglob(fname))
    return matches[0] if matches else None


def build_html(data, source_dir, output_dir):
    """Build the self-contained review HTML page."""
    clusters = [c for c in data['clusters'] if c['count'] > 1]
    if not clusters:
        return None

    total = data['total_scanned']
    unique = data['unique_count']
    groups = len(clusters)
    dupes = data['duplicate_count']

    # Checkmark SVG
    check_svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>'

    # Build groups HTML
    print("Generating thumbnails...")
    groups_html = ""
    photo_count = 0

    for gi, c in enumerate(clusters):
        all_names = [c['selected']] + c.get('duplicates', [])
        cards_html = ""

        for fname in all_names:
            fpath = find_file(source_dir, fname, c)
            if not fpath or not fpath.exists():
                continue

            size_bytes = fpath.stat().st_size
            size_str = f"{size_bytes/1024:.0f} KB" if size_bytes < 1024 * 1024 else f"{size_bytes/1024/1024:.1f} MB"
            is_best = (fname == c['selected'])
            thumb = make_thumb(fpath)
            if not thumb:
                continue

            photo_count += 1
            escaped = str(fpath).replace('"', '&quot;')
            badge = '<span class="badge best">Best</span>' if is_best else ''

            cards_html += (
                f'<div class="card" data-path="{escaped}" data-group="{gi}" onclick="toggle(this)">'
                f'<div class="ck">{check_svg}</div>'
                f'<button class="zm" onclick="event.stopPropagation();openLB(this.parentElement)" title="Preview">&#x1F50D;</button>'
                f'<img src="data:image/jpeg;base64,{thumb}" loading="lazy" alt="{fname}">'
                f'<div class="ci"><span class="sz">{size_str}</span>{badge}</div>'
                f'<div class="fn" title="{fname}">{fname}</div>'
                f'</div>'
            )

        if not cards_html:
            continue

        groups_html += (
            f'<section class="group" id="g{gi}">'
            f'<div class="gh">'
            f'<span class="gt">Group {gi+1}<span class="gc">{c["count"]} photos</span></span>'
            f'<button class="btn btn-o" onclick="selGroup({gi})" style="padding:4px 10px;font-size:12px">Select all</button>'
            f'</div>'
            f'<div class="grid">{cards_html}</div>'
            f'</section>'
        )

    print(f"  Processed {photo_count} photos across {groups} groups")

    # Config JSON for JavaScript
    config = json.dumps({
        "output_dir": output_dir,
        "total": total,
        "unique": unique,
        "groups": groups,
        "dupes": dupes,
    })

    js_final = JS.replace('__CFG__', config)

    # Assemble full HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Photo Dedup</title>
<style>{CSS}</style>
</head>
<body>

<header class="hd">
  <div class="wrap">
    <h1><span class="icon">📸</span> Photo Dedup</h1>
    <p class="sub">Review duplicate groups and pick the photos you want to keep</p>
    <div class="stats">
      <div class="stat"><div class="val">{total}</div><div class="lbl">Total</div></div>
      <div class="stat"><div class="val">{unique}</div><div class="lbl">Unique</div></div>
      <div class="stat"><div class="val">{groups}</div><div class="lbl">Groups</div></div>
      <div class="stat"><div class="val">{dupes}</div><div class="lbl">Duplicates</div></div>
    </div>
  </div>
</header>

<div class="tb">
  <div class="wrap tb-inner">
    <span class="sel-count">保留: <strong id="cnt">0</strong> · 删除: <strong id="del-cnt">0</strong></span>
    <button class="btn btn-o" onclick="best()">Auto-select best</button>
    <button class="btn btn-o" onclick="clearAll()">Clear</button>
    <button class="btn btn-p" id="save-btn" onclick="save()" disabled>🗑️ 删除重复文件</button>
  </div>
</div>

<main class="wrap">
  <p class="hint">💡 点击选择要保留的照片 · 点击 🔍 预览 · 已自动选择最佳质量 · 未选中的重复文件将被删除</p>
  {groups_html}
</main>

<div class="lb" id="lb" onclick="closeLB()">
  <img id="lb-img" src="">
  <span class="close-hint">Click anywhere or press ESC to close</span>
</div>

<div class="toast" id="toast"></div>

<script>{js_final}</script>
</body>
</html>'''

    return html


def main():
    parser = argparse.ArgumentParser(description="Photo Dedup — generate review HTML")
    parser.add_argument("report", help="Path to dedup_report.json")
    parser.add_argument("--source", help="Source photos directory (overrides report)")
    parser.add_argument("--output-dir", default="~/Desktop/photo_picks",
                        help="Default output dir for the save script")
    parser.add_argument("-o", "--out", help="Output HTML path")
    parser.add_argument("--no-open", action="store_true", help="Don't open browser")
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"ERROR: Report not found: {report_path}")
        sys.exit(1)

    with open(report_path) as f:
        data = json.load(f)

    source_dir = Path(args.source) if args.source else Path(data['source'])
    if not source_dir.is_dir():
        print(f"ERROR: Source directory not found: {source_dir}")
        sys.exit(1)

    print(f"Source:  {source_dir}")
    print(f"Report:  {report_path}")

    html = build_html(data, source_dir, args.output_dir)
    if not html:
        print("No duplicate groups found. Nothing to review.")
        sys.exit(0)

    out_path = Path(args.out) if args.out else source_dir / "photo_dedup.html"
    out_path.write_text(html)
    size_mb = out_path.stat().st_size / 1024 / 1024
    print(f"\nReview page: {out_path} ({size_mb:.1f} MB)")
    print("Open in any browser to review and select photos.")

    if not args.no_open:
        webbrowser.open(f"file://{out_path}")


if __name__ == "__main__":
    main()
