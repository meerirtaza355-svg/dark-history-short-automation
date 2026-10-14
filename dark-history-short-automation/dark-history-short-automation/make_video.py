import json, os, subprocess, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
W, H = 1080, 1920


def run(cmd, **kwargs):
    subprocess.run(cmd, check=True, **kwargs)


def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def wrap(draw, text, f, max_width):
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            trial = f"{line} {word}".strip()
            if draw.textbbox((0, 0), trial, font=f)[2] <= max_width:
                line = trial
            else:
                if line: lines.append(line)
                line = word
        lines.append(line)
    return lines


def create_card(text, index, total, path):
    img = Image.new("RGB", (W, H), (13, 18, 28))
    d = ImageDraw.Draw(img)
    # Simple dark graphic treatment, no copyrighted stock footage.
    for y in range(H):
        shade = int(18 + 24 * y / H)
        d.line((0, y, W, y), fill=(shade // 2, shade // 1, shade))
    d.rectangle((70, 220, W-70, 225), fill=(203, 157, 83))
    d.rectangle((70, H-270, W-70, H-265), fill=(203, 157, 83))
    d.text((80, 155), "DARK HISTORY  /  CASE FILE", font=font(32, True), fill=(221, 190, 135))
    f = font(62 if len(text) < 45 else 49, True)
    lines = wrap(d, text, f, W-180)
    line_h = 1.35 * f.size
    total_h = line_h * len(lines)
    y = (H-total_h)/2
    for line in lines:
        box = d.textbbox((0, 0), line, font=f)
        x = (W - (box[2]-box[0]))/2
        d.text((x, y), line, font=f, fill=(245, 241, 231), stroke_width=1, stroke_fill=(10, 10, 12))
        y += line_h
    d.text((80, H-220), "HISTORICAL EXPLAINER  •  VERIFY SOURCES", font=font(24, True), fill=(190, 195, 204))
    d.text((W-150, H-160), f"{index+1:02d}/{total:02d}", font=font(30, True), fill=(221, 190, 135))
    img.save(path, quality=92)


def probe_duration(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ], text=True).strip()
    return float(out)


def main():
    story = json.loads((ROOT / "story.json").read_text(encoding="utf-8"))
    # Keep the narration comfortably within the Shorts 60-second target.
    wav = OUT / "narration.wav"
    run(["espeak-ng", "-v", "en-us", "-s", "145", "-w", str(wav), story["narration"]])
    duration = probe_duration(wav)
    if duration > 59:
        raise SystemExit(f"Narration is {duration:.1f}s; shorten story.json narration to under 59 seconds.")
    scenes = story["scenes"]
    images = []
    for i, scene in enumerate(scenes):
        p = OUT / f"scene_{i:02d}.jpg"
        create_card(scene, i, len(scenes), p)
        images.append(p)
    each = duration / len(images)
    concat = OUT / "images.txt"
    with concat.open("w", encoding="utf-8") as f:
        for p in images:
            f.write(f"file '{p.as_posix()}'\n")
            f.write(f"duration {each:.4f}\n")
        f.write(f"file '{images[-1].as_posix()}'\n")
    video = OUT / "dark_history_short.mp4"
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat),
        "-i", str(wav), "-vf", "fps=30,format=yuv420p",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "25",
        "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(video)
    ])
    (OUT / "metadata.json").write_text(json.dumps({"title": story["title"], "description": story["description"]}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Created {video} ({duration:.1f} sec)")

if __name__ == "__main__":
    main()
