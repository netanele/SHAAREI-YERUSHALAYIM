"""Compose the Shaarei Yerushalayim catalog video.

Usage:
  python3 compose.py 720  ../../docs/video/Shaarei_Yerushalayim_Video_WhatsApp.mp4
  python3 compose.py 1080 ../../docs/video/Shaarei_Yerushalayim_Video_HD.mp4
  python3 compose.py 720 preview        # still frames to data/video-build/preview_*.jpg

Each scene: a slow, gentle zoom on the image with the text layer fading in,
then a soft crossfade to the next scene. Motion is kept small on purpose:
less change between frames means less damage when WhatsApp re-compresses.
Run from tools/video. Images come from docs/img; text layers and output
go to data/video-build (git-ignored). Make the text layers first with render.py."""
import os, subprocess, sys
import numpy as np
from PIL import Image

RES = int(sys.argv[1]) if len(sys.argv) > 1 else 720
W, H = (720, 1280) if RES == 720 else (1080, 1920)
FPS = 30
XF = 0.7                    # crossfade seconds
OV_IN, OV_DUR = 0.3, 0.6    # text fade-in start / length within a scene
IMG_DIR = "../../docs/img"
BUILD = "../../data/video-build"

# (text layer, image, seconds, zoom_from, zoom_to, center_y_from, center_y_to)
SCENES = [
    ("cover",     "exterior",  4.6, 1.00, 1.03, 0.53, 0.55),
    ("sanctuary", "sanctuary", 4.8, 1.03, 1.00, 0.50, 0.50),
    ("dome",      "dome",      5.8, 1.00, 1.03, 0.45, 0.43),
    ("ark",       "ark-open",  4.8, 1.03, 1.00, 0.52, 0.52),
    ("kollel",    "kollel",    5.8, 1.00, 1.03, 0.50, 0.52),
    ("donors",    "donors",    4.8, 1.03, 1.00, 0.45, 0.47),
    ("contact",   None,        6.0, 1.00, 1.00, 0.50, 0.50),
]

def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)

class Scene:
    def __init__(self, ov, img, dur, z0, z1, cy0, cy1):
        self.dur, self.z0, self.z1, self.cy0, self.cy1 = dur, z0, z1, cy0, cy1
        self.ov = Image.open(f"{BUILD}/ov{W}_{ov}.png").convert("RGBA")
        self.src = Image.open(f"{IMG_DIR}/{img}.jpg").convert("RGB") if img else None
        self.card = self.ov.convert("RGB") if img is None else None

    def frame(self, t):
        if self.card is not None:          # closing card: still frame
            return self.card
        p = ease(t / self.dur)
        z = self.z0 + (self.z1 - self.z0) * p
        sw, sh = self.src.size
        bh = sh / z
        bw = bh * W / H
        cy = (self.cy0 + (self.cy1 - self.cy0) * p) * sh
        x0 = (sw - bw) / 2
        y0 = min(max(cy - bh / 2, 0), sh - bh)
        bg = self.src.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + bw, y0 + bh)).convert("RGBA")
        a = ease((t - OV_IN) / OV_DUR)
        if a > 0:
            ov = self.ov
            if a < 1:
                ov = ov.copy()
                alpha = np.asarray(ov.getchannel("A"), dtype=np.float32) * a
                ov.putalpha(Image.fromarray(alpha.astype(np.uint8)))
            bg = Image.alpha_composite(bg, ov)
        return bg.convert("RGB")

def timeline():
    scenes = [Scene(*s) for s in SCENES]
    starts, t = [], 0.0
    for s in scenes:
        starts.append(t)
        t += s.dur - XF
    return scenes, starts, t + XF

def frame_at(scenes, starts, T):
    active = [(i, T - starts[i]) for i, s in enumerate(scenes) if 0 <= T - starts[i] < s.dur]
    if len(active) == 1:
        i, lt = active[0]
        return np.asarray(scenes[i].frame(lt))
    (i, lt), (j, lt2) = active[0], active[1]
    a = ease(lt2 / XF)
    f1 = np.asarray(scenes[i].frame(lt), dtype=np.float32)
    f2 = np.asarray(scenes[j].frame(lt2), dtype=np.float32)
    return (f1 * (1 - a) + f2 * a).astype(np.uint8)

def encode(out_path):
    scenes, starts, total = timeline()
    n = int(round(total * FPS))
    if W == 720:   # near WhatsApp's own HD size, so its re-encode changes less
        v = ["-crf", "17", "-maxrate", "3500k", "-bufsize", "7000k"]
    else:
        v = ["-crf", "19", "-maxrate", "8000k", "-bufsize", "16000k"]
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
           "-map", "0:v", "-map", "1:a", "-shortest",
           "-c:v", "libx264", "-preset", "slow", *v, "-g", str(FPS * 2),
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
           "-movflags", "+faststart", "-c:a", "aac", "-b:a", "48k", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(n):
        proc.stdin.write(frame_at(scenes, starts, k / FPS).tobytes())
    proc.stdin.close()
    proc.wait()
    print(f"{out_path}: {W}x{H}, {total:.1f}s")

def preview():
    scenes, starts, total = timeline()
    ts = [st + s.dur * 0.75 for st, s in zip(starts, scenes)]
    for k, T in enumerate(ts):
        Image.fromarray(frame_at(scenes, starts, T)).save(f"{BUILD}/preview_{k:02d}.jpg", quality=90)
    print(f"preview frames: {len(ts)}, total {total:.1f}s")

if __name__ == "__main__":
    target = sys.argv[2] if len(sys.argv) > 2 else f"{BUILD}/video_{RES}.mp4"
    preview() if target == "preview" else encode(target)
