#!/usr/bin/env python3
"""
Screen-to-Promo Compositor — Frame-by-frame video compositing engine.

Usage:
  python3 compose.py --config config.json --output-frames ./frames/out/
  python3 compose.py --config config.json --output final.mp4   # encode directly

Config JSON structure:
{
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "segments": [
    {
      "type": "presenter",           # presenter | screenrec | transition | card
      "source": "path/to/frames/",   # frame dir
      "source_pattern": "lob_%04d.jpg",
      "duration": 8.0,
      "audio": "path/to/audio.wav",
      "words_json": "path/to/words.json",
      "presenter_alpha": "path/to/alpha_frames/",  # optional cutout frames
      "alpha_pattern": "lob_%04d.png"
    },
    {
      "type": "screenrec",
      "source": "path/to/frames/",
      "source_pattern": "prod_%04d.jpg",
      "duration": 14.4,
      "audio": "path/to/vo.wav",
      "words_json": "path/to/words.json",
      "content_bounds": [190, 888],   # [top, bottom] if letterboxed, null if full frame
      "zoom": {
        "cx": 1100, "cy_start": 250, "cy_end": 430, "scale": 1.8,
        "in_start": 4.0, "in_end": 6.0,
        "hold_end": 11.0,
        "out_end": 13.0
      },
      "time_map": {                   # optional: remap VO time to source time
        "vo_times": [0, 2.5, 5.0, 10.0, 15.0],
        "src_times": [0, 2.0, 4.0, 8.0, 18.0]
      },
      "smooth_jumps": [8.7]          # optional: source times where UI jumps, auto cross-fade
    },
    {
      "type": "transition",
      "from_segment": 0,             # index of outgoing segment
      "to_segment": 2,               # index of incoming segment
      "duration": 2.0,
      "mode": "overlay_dissolve",    # overlay_dissolve | crossfade | wipe
      "presenter_fade_start": 0.5,   # when presenter starts fading (relative to transition start)
      "presenter_fade_dur": 1.5,
      "bg_fade_dur": 2.0             # how long BG takes to fully appear
    },
    {
      "type": "card",
      "background": "#FFFFFF",
      "text": "Download Now",
      "duration": 3.0
    }
  ],
  "captions": {
    "enabled": true,
    "style": "pop",                   # pop | static | karaoke
    "font": null,
    "font_size": 52,
    "position_y": -130,               # from bottom
    "color": [255, 255, 255],
    "outline_color": [0, 0, 0],
    "accent_color": [255, 200, 50]
  },
  "audio_mix": {
    "normalize": true,
    "target_lufs": -25,
    "gap_after_segments": [0]         # segment indices that get a 0.5s silence after
  }
}
"""

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import platform
import time
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Font helpers
# ---------------------------------------------------------------------------

_FONT_CACHE = {}


def _find_system_font():
    """Return the first available system font path, or None."""
    if platform.system() == "Darwin":
        candidates = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFNSText.ttf",
            "/Library/Fonts/Arial.ttf",
        ]
    elif platform.system() == "Linux":
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        ]
    else:  # Windows
        candidates = ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"]
    for fp in candidates:
        if os.path.isfile(fp):
            return fp
    return None


def _resolve_font(size=52, path=None):
    """Return a cached font object. Avoids re-creating fonts every frame."""
    key = (path, size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    font = None
    if path:
        try:
            font = ImageFont.truetype(path, size)
        except (OSError, IOError):
            pass
    if font is None:
        sys_font = _find_system_font()
        if sys_font:
            try:
                font = ImageFont.truetype(sys_font, size)
            except (OSError, IOError):
                font = ImageFont.load_default()
        else:
            font = ImageFont.load_default()

    _FONT_CACHE[key] = font
    return font


# ---------------------------------------------------------------------------
# Word / caption helpers
# ---------------------------------------------------------------------------


def load_words(path):
    if not path:
        return []
    p = Path(path)
    if not p.exists():
        print(f"  Warning: words file not found: {path}", file=sys.stderr)
        return []
    with open(p) as f:
        data = json.load(f)
    return data.get("words", data if isinstance(data, list) else [])


def active_word(words, t):
    for w in words:
        if w["start"] <= t <= w["end"] + 0.15:
            return w
    return None


def word_progress(word, t):
    if not word:
        return 0
    return min(1.0, (t - word["start"]) / max(word["end"] - word["start"], 0.05))


# ---------------------------------------------------------------------------
# Config validation
# ---------------------------------------------------------------------------

REQUIRED_SEGMENT_KEYS = {
    "presenter": ["source", "duration"],
    "screenrec": ["source", "duration"],
    "transition": ["from_segment", "to_segment", "duration"],
    "card": ["duration"],
}


def validate_config(config):
    """Validate config and return list of warnings (empty = ok)."""
    errors = []
    if "segments" not in config:
        errors.append("Missing 'segments' key")
        return errors
    if "fps" not in config:
        errors.append("Missing 'fps' — defaulting to 30")
    if "width" not in config:
        errors.append("Missing 'width' — defaulting to 1920")
    if "height" not in config:
        errors.append("Missing 'height' — defaulting to 1080")

    for i, seg in enumerate(config["segments"]):
        stype = seg.get("type")
        if not stype:
            errors.append(f"Segment {i}: missing 'type'")
            continue
        if stype not in REQUIRED_SEGMENT_KEYS:
            errors.append(f"Segment {i}: unknown type '{stype}'")
            continue
        for key in REQUIRED_SEGMENT_KEYS[stype]:
            if key not in seg:
                errors.append(f"Segment {i} ({stype}): missing '{key}'")

        if stype in ("presenter", "screenrec"):
            src = Path(seg.get("source", ""))
            if not src.is_dir():
                errors.append(f"Segment {i}: source dir not found: {src}")

        if stype == "transition":
            n = len(config["segments"])
            for ref_key in ("from_segment", "to_segment"):
                ref = seg.get(ref_key, -1)
                if not (0 <= ref < n):
                    errors.append(f"Segment {i}: {ref_key}={ref} out of range")

        zoom = seg.get("zoom")
        if zoom:
            for key in ("cx", "cy_start", "cy_end", "scale", "in_start", "in_end", "hold_end", "out_end"):
                if key not in zoom:
                    errors.append(f"Segment {i} zoom: missing '{key}'")

    return errors


# ---------------------------------------------------------------------------
# Compositor
# ---------------------------------------------------------------------------


class Compositor:
    def __init__(self, config):
        self.cfg = config
        self.W = config.get("width", 1920)
        self.H = config.get("height", 1080)
        self.FPS = config.get("fps", 30)
        self.cap_cfg = config.get("captions", {})
        self._init_fonts()
        self._preload_segments()
        self._frame_cache = {}
        self._cache_max = 120  # keep last N frames in memory

    def _init_fonts(self):
        """Pre-load fonts once, not per-frame."""
        cc = self.cap_cfg
        if not cc.get("enabled"):
            self.font = None
            return
        font_path = cc.get("font")
        font_size = cc.get("font_size", 52)
        self.font = _resolve_font(font_size, font_path)
        self._font_path = font_path

    def _preload_segments(self):
        """Count frames for each segment source and pre-load words."""
        for seg in self.cfg["segments"]:
            if seg["type"] in ("presenter", "screenrec"):
                src = Path(seg["source"])
                pat = seg.get("source_pattern", "f_%04d.jpg")
                prefix = pat.split("%")[0] if "%" in pat else ""
                seg["_n_frames"] = len(list(src.glob(f"{prefix}*")))
                if seg["_n_frames"] == 0:
                    print(f"  Warning: no frames found in {src} with pattern {pat}", file=sys.stderr)
                seg["_words"] = load_words(seg.get("words_json"))
                if seg.get("presenter_alpha"):
                    alpha_dir = Path(seg["presenter_alpha"])
                    seg["_n_alpha"] = len(list(alpha_dir.glob("*.png")))

    def _get_frame(self, seg, fidx):
        """Load a frame from segment source with basic caching."""
        src = Path(seg["source"])
        pat = seg.get("source_pattern", "f_%04d.jpg")
        n = seg.get("_n_frames", 1)
        fi = min(max(1, fidx), n)
        fp = src / (pat % fi)
        cache_key = str(fp)

        if cache_key in self._frame_cache:
            return self._frame_cache[cache_key].copy()

        if fp.exists():
            img = Image.open(fp).convert("RGB")
            if img.size != (self.W, self.H):
                img = img.resize((self.W, self.H), Image.LANCZOS)
        else:
            img = Image.new("RGB", (self.W, self.H), (255, 255, 255))

        # Evict old entries if cache is full
        if len(self._frame_cache) >= self._cache_max:
            oldest = next(iter(self._frame_cache))
            del self._frame_cache[oldest]
        self._frame_cache[cache_key] = img
        return img.copy()

    def _get_alpha_frame(self, seg, fidx):
        """Load a cutout (RGBA) frame."""
        alpha_dir = Path(seg["presenter_alpha"])
        pat = seg.get("alpha_pattern", "lob_%04d.png")
        n = seg.get("_n_alpha", 1)
        fi = min(max(1, fidx), n)
        fp = alpha_dir / (pat % fi)
        if fp.exists():
            img = Image.open(fp).convert("RGBA")
            if img.size != (self.W, self.H):
                img = img.resize((self.W, self.H), Image.LANCZOS)
            return img
        return self._get_frame(seg, fidx).convert("RGBA")

    def _get_screenrec_frame(self, seg, local_t):
        """Get screen recording frame with optional time mapping and content cropping."""
        tm = seg.get("time_map")
        if tm:
            src_t = float(np.interp(local_t, tm["vo_times"], tm["src_times"]))
        else:
            src_t = local_t

        fidx = int(src_t * self.FPS) + 1
        img = self._get_frame(seg, fidx)

        # Content cropping for letterboxed sources
        bounds = seg.get("content_bounds")
        if bounds:
            ct, cb = bounds
            ch = cb - ct
            content = img.crop((0, ct, self.W, cb))
            result = Image.new("RGB", (self.W, self.H), (255, 255, 255))
            result.paste(content, (0, (self.H - ch) // 2))
            return result
        return img

    def _apply_zoom(self, img, seg, local_t):
        """Apply zoom based on segment zoom config with AR lock."""
        z = seg.get("zoom")
        if not z:
            return img

        t = local_t
        in_s, in_e = z["in_start"], z["in_end"]
        hold_e = z["hold_end"]
        out_e = z["out_end"]

        if t < in_s or t >= out_e:
            return img

        if in_s <= t < in_e:
            p = (t - in_s) / (in_e - in_s)
            p = 0.5 - 0.5 * math.cos(p * math.pi)  # ease in-out
            zi = True
        elif in_e <= t < hold_e:
            p = 1.0
            zi = True
        else:
            p = (t - hold_e) / (out_e - hold_e)
            p = 0.5 - 0.5 * math.cos(p * math.pi)  # ease in-out
            zi = False

        cx = z["cx"]
        cys, cye = z["cy_start"], z["cy_end"]
        sc = z["scale"]
        s = 1 + (sc - 1) * p if zi else sc - (sc - 1) * p
        cy = cys + (cye - cys) * p if zi else cye

        cw = int(self.W / s)
        ch = int(cw * self.H / self.W)  # AR LOCK — critical
        x1 = max(0, min(self.W - cw, cx - cw // 2))
        y1 = max(0, min(self.H - ch, int(cy) - ch // 2))

        # Constrain zoom to content area for letterboxed sources
        bounds = seg.get("content_bounds")
        if bounds:
            ct, cb = bounds
            content_h = cb - ct
            y_off = (self.H - content_h) // 2
            y1 = max(y_off - 20, min(y_off + content_h - ch + 20, y1))

        return img.crop((x1, y1, x1 + cw, y1 + ch)).resize((self.W, self.H), Image.LANCZOS)

    def _smooth_jump(self, seg, img, local_t):
        """Cross-fade over UI jump points in source video."""
        jumps = seg.get("smooth_jumps", [])
        HALF = 0.25
        for jt in jumps:
            if abs(local_t - jt) < HALF and local_t > jt - HALF:
                pre_t = jt - HALF
                post_t = jt + HALF
                pre_img = self._get_screenrec_frame(seg, pre_t)
                post_img = self._get_screenrec_frame(seg, post_t)
                p = (local_t - (jt - HALF)) / (2 * HALF)
                p = 0.5 - 0.5 * math.cos(p * math.pi)
                return Image.blend(pre_img, post_img, p)
        return img

    def _draw_caption(self, img, word_text, t_in_word):
        """Draw pop/static caption with cached fonts."""
        if not word_text or not self.cap_cfg.get("enabled") or not self.font:
            return img
        cc = self.cap_cfg
        style = cc.get("style", "pop")

        # Pop scale bounce at word onset
        if style == "pop" and t_in_word < 0.3:
            scale = 1.0 + 0.15 * math.sin(min(t_in_word / 0.3, 1.0) * math.pi)
        else:
            scale = 1.0

        text = word_text.upper()
        base_size = cc.get("font_size", 52)
        fs = int(base_size * scale)

        # Use cached font — only create a new one if scale changed the size
        if fs == base_size:
            f = self.font
        else:
            f = _resolve_font(max(20, fs), self._font_path)

        d = ImageDraw.Draw(img)
        bb = d.textbbox((0, 0), text, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        x = (self.W - tw) // 2
        y = self.H + cc.get("position_y", -130)

        oc = tuple(cc.get("outline_color", [0, 0, 0]))
        tc = tuple(cc.get("color", [255, 255, 255]))
        ac = tuple(cc.get("accent_color", [255, 200, 50]))

        # Outline (3px stroke)
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx * dx + dy * dy <= 9:  # circular outline, skip corners
                    d.text((x + dx, y + dy), text, fill=oc, font=f)
        d.text((x, y), text, fill=tc, font=f)

        # Accent underline swipe
        if style == "pop" and t_in_word > 0.2:
            lp = min(1.0, (t_in_word - 0.2) / 0.3)
            lw = int(tw * lp)
            lx = x + (tw - lw) // 2
            d.rectangle([lx, y + th + 4, lx + lw, y + th + 8], fill=ac)

        return img

    def _overlay_alpha(self, bg, fg_rgba, opacity=1.0):
        """Composite RGBA foreground onto RGB background."""
        bg_rgba = bg.convert("RGBA")
        fg = fg_rgba.copy()
        if opacity < 1.0:
            r, g, b, a = fg.split()
            a = a.point(lambda x: int(x * opacity))
            fg = Image.merge("RGBA", (r, g, b, a))
        bg_rgba.paste(fg, (0, 0), fg)
        return bg_rgba.convert("RGB")

    def _build_timeline(self):
        """Build segment timeline with proper start times. Transitions consume time sequentially."""
        segments = self.cfg["segments"]
        gap_after = set(self.cfg.get("audio_mix", {}).get("gap_after_segments", []))
        timeline = []
        t_cursor = 0.0
        for idx, seg in enumerate(segments):
            timeline.append({"start": t_cursor, "seg": seg, "idx": idx})
            t_cursor += seg["duration"]
            if idx in gap_after:
                t_cursor += 0.5
        return timeline, t_cursor

    def compose(self, out_dir):
        """Compose all frames to out_dir."""
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        timeline, total_dur = self._build_timeline()
        total_frames = int(total_dur * self.FPS)

        print(f"Composing {total_frames} frames ({total_dur:.1f}s) @ {self.FPS}fps...")
        t_start = time.time()

        for fi in range(total_frames):
            t = fi / self.FPS
            out_path = out_dir / f"f_{fi + 1:04d}.jpg"  # 1-indexed to match prep_source output

            if fi % 150 == 0 and fi > 0:
                elapsed = time.time() - t_start
                fps_rate = fi / elapsed
                eta = (total_frames - fi) / fps_rate
                print(f"  {fi}/{total_frames} ({t:.1f}s) — {fps_rate:.1f} fps, ETA {eta:.0f}s")
            elif fi == 0:
                print(f"  {fi}/{total_frames} ({t:.1f}s)")

            # Find active segment (last matching in timeline order)
            img = Image.new("RGB", (self.W, self.H), (255, 255, 255))
            for entry in reversed(timeline):
                seg = entry["seg"]
                seg_start = entry["start"]
                seg_end = seg_start + seg["duration"]
                gap = 0.5 if entry["idx"] in set(self.cfg.get("audio_mix", {}).get("gap_after_segments", [])) else 0
                if seg_start <= t < seg_end + gap:
                    local_t = t - seg_start

                    if seg["type"] == "presenter":
                        fidx = min(int(local_t * self.FPS) + 1, seg["_n_frames"])
                        img = self._get_frame(seg, fidx)
                        w = active_word(seg["_words"], local_t)
                        if w:
                            img = self._draw_caption(img, w["word"], word_progress(w, local_t))

                    elif seg["type"] == "screenrec":
                        img = self._get_screenrec_frame(seg, local_t)
                        img = self._smooth_jump(seg, img, local_t)
                        img = self._apply_zoom(img, seg, local_t)
                        w = active_word(seg["_words"], local_t)
                        if w:
                            img = self._draw_caption(img, w["word"], word_progress(w, local_t))

                    elif seg["type"] == "transition":
                        img = self._render_transition(seg, self.cfg["segments"], timeline, local_t)

                    elif seg["type"] == "card":
                        img = self._render_card(seg)

                    break

            img.save(out_path, quality=92)

        elapsed = time.time() - t_start
        print(f"Done! {total_frames} frames in {elapsed:.1f}s ({total_frames/elapsed:.1f} fps)")
        return total_frames, total_dur

    def _render_transition(self, seg, all_segments, timeline, local_t):
        """Render overlay_dissolve or crossfade transition."""
        mode = seg.get("mode", "crossfade")
        dur = seg["duration"]
        from_seg = all_segments[seg["from_segment"]]
        to_seg = all_segments[seg["to_segment"]]

        if mode == "overlay_dissolve" and from_seg.get("presenter_alpha"):
            # Presenter cutout fades out while BG fades in
            bg_progress = min(1.0, local_t / seg.get("bg_fade_dur", dur))
            bg_alpha = 0.5 - 0.5 * math.cos(bg_progress * math.pi)

            white = Image.new("RGB", (self.W, self.H), (255, 255, 255))
            if to_seg["type"] == "screenrec":
                to_img = self._get_screenrec_frame(to_seg, 0)
            else:
                to_img = self._get_frame(to_seg, 1)
            bg = Image.blend(white, to_img, bg_alpha)

            # Presenter fade
            fade_start = seg.get("presenter_fade_start", 0.5)
            fade_dur = seg.get("presenter_fade_dur", 1.5)
            if local_t < fade_start:
                lob_opacity = 1.0
            elif local_t < fade_start + fade_dur:
                fp = (local_t - fade_start) / fade_dur
                lob_opacity = max(0, 0.5 + 0.5 * math.cos(fp * math.pi))
            else:
                lob_opacity = 0.0

            if lob_opacity > 0:
                n = from_seg.get("_n_frames", 1)
                lob_rgba = self._get_alpha_frame(from_seg, n)
                bg = self._overlay_alpha(bg, lob_rgba, lob_opacity)

            # Captions from presenter words if still speaking
            from_t = from_seg["duration"] - (seg["duration"] - local_t)
            w = active_word(from_seg.get("_words", []), from_t)
            if w:
                bg = self._draw_caption(bg, w["word"], word_progress(w, from_t))
            return bg

        elif mode == "wipe":
            # Left-to-right wipe
            progress = local_t / dur
            progress = 0.5 - 0.5 * math.cos(progress * math.pi)
            from_img = self._get_frame(from_seg, from_seg.get("_n_frames", 1))
            if to_seg["type"] == "screenrec":
                to_img = self._get_screenrec_frame(to_seg, 0)
            else:
                to_img = self._get_frame(to_seg, 1)
            split_x = int(self.W * progress)
            result = from_img.copy()
            if split_x > 0:
                result.paste(to_img.crop((0, 0, split_x, self.H)), (0, 0))
            return result

        else:
            # Simple crossfade
            alpha = local_t / dur
            alpha = 0.5 - 0.5 * math.cos(alpha * math.pi)
            from_img = self._get_frame(from_seg, from_seg.get("_n_frames", 1))
            if to_seg["type"] == "screenrec":
                to_img = self._get_screenrec_frame(to_seg, 0)
            else:
                to_img = self._get_frame(to_seg, 1)
            return Image.blend(from_img, to_img, alpha)

    def _render_card(self, seg):
        """Render a title/CTA card."""
        bg_color = seg.get("background", "#FFFFFF")
        if isinstance(bg_color, str) and bg_color.startswith("#") and len(bg_color) >= 7:
            r, g, b = int(bg_color[1:3], 16), int(bg_color[3:5], 16), int(bg_color[5:7], 16)
        else:
            r, g, b = 255, 255, 255
        img = Image.new("RGB", (self.W, self.H), (r, g, b))
        text = seg.get("text", "")
        if text:
            d = ImageDraw.Draw(img)
            f = _resolve_font(64)
            bb = d.textbbox((0, 0), text, font=f)
            tw, th = bb[2] - bb[0], bb[3] - bb[1]
            d.text(((self.W - tw) // 2, (self.H - th) // 2), text, fill=(0, 0, 0), font=f)
        return img


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Screen-to-Promo Compositor")
    parser.add_argument("--config", required=True, help="Config JSON file")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output-frames", help="Output frames directory")
    group.add_argument("--output", help="Output video file (auto-encodes with ffmpeg)")
    parser.add_argument("--audio", help="Audio file to mux (only with --output)")
    parser.add_argument("--validate-only", action="store_true", help="Validate config and exit")
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    # Validate
    errors = validate_config(config)
    for e in errors:
        print(f"  Config: {e}", file=sys.stderr)
    if any("missing" in e.lower() and "defaulting" not in e.lower() for e in errors):
        print("Fix config errors before composing.", file=sys.stderr)
        sys.exit(1)
    if args.validate_only:
        if errors:
            print(f"{len(errors)} warning(s)")
        else:
            print("Config OK")
        sys.exit(0)

    comp = Compositor(config)

    if args.output_frames:
        n_frames, duration = comp.compose(args.output_frames)
        print(f"\nTotal: {n_frames} frames, {duration:.1f}s")
    else:
        # Compose to temp dir, then encode
        import tempfile
        tmpdir = tempfile.mkdtemp(prefix="s2p_frames_")
        try:
            n_frames, duration = comp.compose(tmpdir)
            fps = config.get("fps", 30)
            cmd = [
                "ffmpeg", "-y", "-r", str(fps),
                "-i", f"{tmpdir}/f_%04d.jpg",
            ]
            if args.audio:
                cmd += ["-i", args.audio]
            cmd += [
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-pix_fmt", "yuv420p", "-vf", "setsar=1",
            ]
            if args.audio:
                cmd += ["-c:a", "copy", "-map", "0:v", "-map", "1:a"]
            cmd.append(args.output)
            print(f"\nEncoding → {args.output}")
            subprocess.run(cmd, check=True)
            print(f"Done: {args.output}")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
