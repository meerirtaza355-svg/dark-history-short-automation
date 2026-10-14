import os
import json
from pathlib import Path
from subprocess import run
from gtts import gTTS
from PIL import Image, ImageDraw

def make_video():
    OUT = Path("output").resolve()
    OUT.mkdir(exist_ok=True)

    # Load story.json
    if not os.path.exists("story.json"):
        raise FileNotFoundError("story.json file nahi mili!")
        
    with open("story.json", "r", encoding="utf-8") as f:
        story = json.load(f)

    scenes = story.get("scenes", []) if isinstance(story, dict) else story

    text_list = []
    for scene in scenes:
        if isinstance(scene, dict):
            text_list.append(scene.get("text", ""))
        else:
            text_list.append(str(scene))

    full_text = " ".join(text_list)
    if not full_text.strip():
        full_text = "Dark history short story."

    # Generate natural voice using gTTS
    print("Generating voiceover using gTTS...")
    audio_path = OUT / "voice.mp3"
    tts = gTTS(text=full_text, lang='en', slow=False)
    tts.save(str(audio_path))

    # Get audio duration using ffprobe
    print("Checking audio duration...")
    result = run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of",
        "default=noprint_wrappers=1:nokey=1", str(audio_path)
    ], capture_output=True, text=True, check=True)
    
    duration = float(result.stdout.strip())

    # Create background card images for scenes using absolute paths
    images = []
    for i, scene_text in enumerate(text_list):
        img_path = OUT / f"scene_{i:02d}.jpg"
        img = Image.new('RGB', (1080, 1920), color=(15, 15, 15))
        draw = ImageDraw.Draw(img)
        draw.text((100, 900), scene_text, fill=(255, 255, 255))
        img.save(str(img_path))
        images.append(img_path)

    # Create image list file for ffmpeg using absolute paths to avoid path errors
    concat_file = OUT / "images.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        each_duration = duration / len(images) if images else duration
        for p in images:
            f.write(f"file '{p.resolve().as_posix()}'\n")
            f.write(f"duration {each_duration:.4f}\n")
        if images:
            f.write(f"file '{images[-1].resolve().as_posix()}'\n")

    video_output = OUT / "dark_history_short.mp4"

    # Compile video with ffmpeg
    print("Compiling video with FFmpeg...")
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-i", str(audio_path), "-vf", "fps=30,format=yuv420p",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "25",
        "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart",
        str(video_output)
    ], check=True)

    if not video_output.exists():
        raise FileNotFoundError("Video file create nahi ho saki!")

    print(f"Video successfully ban gayi: {video_output} ({duration:.1f} sec)")

if __name__ == "__main__":
    make_video()
