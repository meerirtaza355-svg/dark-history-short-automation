import os
import json
from pathlib import Path
from subprocess import run
from gtts import gTTS
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageOps

def make_video():
    OUT = Path("output").resolve()
    OUT.mkdir(exist_ok=True)

    if not os.path.exists("story.json"):
        raise FileNotFoundError("story.json file nahi mili!")
        
    with open("story.json", "r", encoding="utf-8") as f:
        story = json.load(f)

    scenes = story.get("scenes", []) if isinstance(story, dict) else story
    text_list = [scene.get("text", "") if isinstance(scene, dict) else str(scene) for scene in scenes]
    image_urls = [scene.get("image_url", "") if isinstance(scene, dict) else "" for scene in scenes]

    full_text = " ".join(text_list)
    if not full_text.strip():
        full_text = "Dark history short story."

    print("Generating voiceover using gTTS...")
    audio_path = OUT / "voice.mp3"
    tts = gTTS(text=full_text, lang='en', slow=False)
    tts.save(str(audio_path))

    result = run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of",
        "default=noprint_wrappers=1:nokey=1", str(audio_path)
    ], capture_output=True, text=True, check=True)
    
    duration = float(result.stdout.strip())

    images = []
    for i, (scene_text, img_url) in enumerate(zip(text_list, image_urls)):
        img_path = OUT / f"scene_{i:02d}.jpg"
        try:
            if img_url:
                response = requests.get(img_url, timeout=15)
                img = Image.open(BytesIO(response.content)).convert("RGB")
            else:
                raise Exception("No URL")
        except:
            img = Image.new('RGB', (1080, 1920), color=(10, 10, 10))

        img = ImageOps.fit(img, (1080, 1920), method=Image.Resampling.LANCZOS)
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 140))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

        draw = ImageDraw.Draw(img)
        words = scene_text.split()
        lines, current_line = [], ""
        for word in words:
            if len(current_line + " " + word) <= 24:
                current_line = (current_line + " " + word).strip()
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        # Text positioning set to lower section of the screen (y = 1300 onwards)
        y = 1250 - (len(lines) * 40)
        for line in lines:
            draw.text((52, y+2), line, fill=(0, 0, 0))
            draw.text((50, y), line, fill=(255, 255, 255))
            y += 75

        img.save(str(img_path))
        images.append(img_path)

    concat_file = OUT / "images.txt"
    scene_duration = duration / len(images) if images else duration
    
    with open(concat_file, "w", encoding="utf-8") as f:
        for p in images:
            f.write(f"file '{p.resolve().as_posix()}'\n")
            f.write(f"duration {scene_duration:.4f}\n")
        if images:
            f.write(f"file '{images[-1].resolve().as_posix()}'\n")

    video_output = OUT / "dark_history_short.mp4"

    print("Compiling cinematic moving video with FFmpeg...")
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-i", str(audio_path),
        "-vf", "zoompan=z='min(zoom+0.0015,1.3)':d=125:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2),fps=30,format=yuv420p",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
        str(video_output)
    ], check=True)

    print(f"Professional Video ban gayi: {video_output}")

if __name__ == "__main__":
    make_video()
