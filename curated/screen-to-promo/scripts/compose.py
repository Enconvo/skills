#!/usr/bin/env python3
"""
Screen-to-Promo Compositor — Frame-by-frame video compositing engine.

Usage:
  python3 compose.py --config config.json --output out.mp4

Config JSON structure:
{
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "segments": [
    {
      "type": "presenter",           # presenter | screenrec | transition | card
      "source": "path/to/frames/",   # frame dir or video file
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

import argparse, json, math, sys, platform
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def _resolve_font(size=52):
    """Find a usable system font cross-platform."""
    candidates = []
    if platform.system() == "Darwin":
        candidates = ["/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/SFNSText.ttf"]
    elif platform.system() == "Linux":
        candidates = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                       "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"]
    else:  # Windows
        candidates = ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"]
    for fp in candidates:
        try: return ImageFont.truetype(fp, size)
        except: continue
    return ImageFont.load_default()

def load_words(path):
    if not path: return []
    with open(path) as f:
        return json.load(f).get("words", [])

def active_word(words, t):
    for w in words:
        if w["start"] <= t <= w["end"] + 0.15:
            return w
    return None

def word_progress(word, t):
    if not word: return 0
    return min(1.0, (t - word["start"]) / max(word["end"] - word["start"], 0.05))

class Compositor:
    def __init__(self, config):
        self.cfg = config
        self.W = config["width"]
        self.H = config["height"]
        self.FPS = config["fps"]
        self.cap_cfg = config.get("captions", {})
        self._load_font()
        self._preload_segments()

    def _load_font(self):
        cc = self.cap_cfg
        if not cc.get("enabled"): return
        font_path = cc.get("font")
        if font_path:
            try: self.font = ImageFont.truetype(font_path, cc.get("font_size", 52))
            except: self.font = _resolve_font(cc.get("font_size", 52))
        else:
            self.font = _resolve_font(cc.get("font_size", 52))

    def _preload_segments(self):
        """Count frames for each segment source."""
        for seg in self.cfg["segments"]:
            if seg["type"] in ("presenter", "screenrec"):
                src = Path(seg["source"])
                pat = seg.get("source_pattern", "*.jpg")
                prefix = pat.split("%")[0] if "%" in pat else ""
                seg["_n_frames"] = len(list(src.glob(f"{prefix}*")))
                seg["_words"] = load_words(seg.get("words_json"))
                # Load alpha frames count if present
                if seg.get("presenter_alpha"):
                    alpha_dir = Path(seg["presenter_alpha"])
                    seg["_n_alpha"] = len(list(alpha_dir.glob("*.png")))

    def _get_frame(self, seg, fidx):
        """Load a frame from segment source."""
        src = Path(seg["source"])
        pat = seg.get("source_pattern", "f_%04d.jpg")
        n = seg.get("_n_frames", 1)
        fi = min(max(1, fidx), n)
        fp = src / (pat % fi)
        if fp.exists():
            return Image.open(fp).resize((self.W, self.H), Image.LANCZOS)
        return Image.new("RGB", (self.W, self.H), (255, 255, 255))

    def _get_alpha_frame(self, seg, fidx):
        """Load a cutout (RGBA) frame."""
        alpha_dir = Path(seg["presenter_alpha"])
        pat = seg.get("alpha_pattern", "lob_%04d.png")
        n = seg.get("_n_alpha", 1)
        fi = min(max(1, fidx), n)
        fp = alpha_dir / (pat % fi)
        if fp.exists():
            return Image.open(fp).resize((self.W, self.H), Image.LANCZOS)
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
        """Apply zoom based on segment zoom config."""
        z = seg.get("zoom")
        if not z: return img

        t = local_t
        in_s, in_e = z["in_start"], z["in_end"]
        hold_e = z["hold_end"]
        out_e = z["out_end"]

        if t < in_s or t >= out_e:
            return img
        elif in_s <= t < in_e:
            p = (t - in_s) / (in_e - in_s)
            zi = True
        elif in_e <= t < hold_e:
            p = 1.0
            zi = True
        else:
            p = (t - hold_e) / (out_e - hold_e)
            zi = False

        cx = z["cx"]
        cys, cye = z["cy_start"], z["cy_end"]
        sc = z["scale"]
        s = 1 + (sc-1)*p if zi else sc - (sc-1)*p
        cy = cys + (cye-cys)*p if zi else cye

        cw = int(self.W / s)
        ch = int(cw * self.H / self.W)  # AR LOCK
        x1 = max(0, min(self.W - cw, cx - cw//2))
        y1 = max(0, min(self.H - ch, int(cy) - ch//2))

        # If letterboxed, constrain zoom to content area
        bounds = seg.get("content_bounds")
        if bounds:
            ct, cb = bounds
            content_h = cb - ct
            y_off = (self.H - content_h) // 2
            y1 = max(y_off - 20, min(y_off + content_h - ch + 20, y1))

        return img.crop((x1, y1, x1+cw, y1+ch)).resize((self.W, self.H), Image.LANCZOS)

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
        """Draw fancy pop caption."""
        if not word_text or not self.cap_cfg.get("enabled"):
            return img
        cc = self.cap_cfg
        style = cc.get("style", "pop")

        if style == "pop" and t_in_word < 0.3:
            scale = 1.0 + 0.15 * math.sin(min(t_in_word/0.3, 1.0) * math.pi)
        else:
            scale = 1.0

        text = word_text.upper()
        fs = int(cc.get("font_size", 52) * scale)
        font_path = cc.get("font")
        if font_path:
            try: f = ImageFont.truetype(font_path, max(20, fs))
            except: f = self.font
        else:
            f = _resolve_font(max(20, fs))

        d = ImageDraw.Draw(img)
        bb = d.textbbox((0, 0), text, font=f)
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
        x = (self.W - tw) // 2
        y = self.H + cc.get("position_y", -130)

        oc = tuple(cc.get("outline_color", [0,0,0]))
        tc = tuple(cc.get("color", [255,255,255]))
        ac = tuple(cc.get("accent_color", [255,200,50]))

        for dx in range(-3,4):
            for dy in range(-3,4):
                d.text((x+dx, y+dy), text, fill=oc, font=f)
        d.text((x, y), text, fill=tc, font=f)

        if style == "pop" and t_in_word > 0.2:
            lp = min(1.0, (t_in_word-0.2)/0.3)
            lw = int(tw*lp); lx = x + (tw-lw)//2
            d.rectangle([lx, y+th+4, lx+lw, y+th+8], fill=ac)

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

    def compose(self, out_dir):
        """Compose all frames to out_dir."""
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        # Build timeline: compute segment start times
        segments = self.cfg["segments"]
        gap_after = set(self.cfg.get("audio_mix", {}).get("gap_after_segments", []))
        timeline = []
        t_cursor = 0.0
        for idx, seg in enumerate(segments):
            if seg["type"] == "transition":
                # Transitions overlap — they start at the end of the previous segment minus their duration
                # Actually, transitions are their own segment with their own duration
                pass
            timeline.append({"start": t_cursor, "seg": seg, "idx": idx})
            t_cursor += seg["duration"]
            if idx in gap_after:
                t_cursor += 0.5  # gap

        total_dur = t_cursor
        total_frames = int(total_dur * self.FPS)

        print(f"Composing {total_frames} frames ({total_dur:.1f}s)...")

        for fi in range(total_frames):
            t = fi / self.FPS
            out_path = out_dir / f"f_{fi:04d}.jpg"
            if fi % 150 == 0:
                print(f"  {fi}/{total_frames} ({t:.1f}s)")

            # Find active segment
            img = Image.new("RGB", (self.W, self.H), (255, 255, 255))
            for entry in reversed(timeline):
                seg = entry["seg"]
                seg_start = entry["start"]
                seg_end = seg_start + seg["duration"]
                gap = 0.5 if entry["idx"] in gap_after else 0
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
                        img = self._render_transition(seg, segments, timeline, local_t, fi)

                    elif seg["type"] == "card":
                        img = self._render_card(seg)

                    break

            img.save(out_path, quality=92)

        print(f"Done! {total_frames} frames")
        return total_frames, total_dur

    def _render_transition(self, seg, all_segments, timeline, local_t, fi):
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
            to_img = self._get_screenrec_frame(to_seg, 0) if to_seg["type"] == "screenrec" else self._get_frame(to_seg, 1)
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
            w = active_word(from_seg.get("_words", []),
                            from_seg["duration"] - (seg["duration"] - local_t))
            if w:
                bg = self._draw_caption(bg, w["word"],
                    word_progress(w, from_seg["duration"] - (seg["duration"] - local_t)))
            return bg
        else:
            # Simple crossfade
            alpha = local_t / dur
            alpha = 0.5 - 0.5 * math.cos(alpha * math.pi)
            from_img = self._get_frame(from_seg, from_seg.get("_n_frames", 1))
            to_img = self._get_frame(to_seg, 1)
            return Image.blend(from_img, to_img, alpha)

    def _render_card(self, seg):
        """Render a title/CTA card."""
        bg_color = seg.get("background", "#FFFFFF")
        if bg_color.startswith("#"):
            r, g, b = int(bg_color[1:3],16), int(bg_color[3:5],16), int(bg_color[5:7],16)
        else:
            r, g, b = 255, 255, 255
        img = Image.new("RGB", (self.W, self.H), (r, g, b))
        text = seg.get("text", "")
        if text:
            d = ImageDraw.Draw(img)
            f = _resolve_font(64)
            bb = d.textbbox((0,0), text, font=f)
            tw, th = bb[2]-bb[0], bb[3]-bb[1]
            d.text(((self.W-tw)//2, (self.H-th)//2), text, fill=(0,0,0), font=f)
        return img


def main():
    parser = argparse.ArgumentParser(description="Screen-to-Promo Compositor")
    parser.add_argument("--config", required=True, help="Config JSON file")
    parser.add_argument("--output-frames", required=True, help="Output frames directory")
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    comp = Compositor(config)
    n_frames, duration = comp.compose(args.output_frames)
    print(f"\nTotal: {n_frames} frames, {duration:.1f}s")


if __name__ == "__main__":
    main()
