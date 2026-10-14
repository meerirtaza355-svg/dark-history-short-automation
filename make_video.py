import os
import json
from pathlib import Path
from subprocess import run
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont

def make_video():
    OUT = Path("output")
    OUT.mkdir(exist_ok=True)

    # Load story.json
    if not os.path.exists("story.json"):
        raise FileNotFoundError("story.json file nahi mili!")
        
    with open("story.json", "r", encoding="utf-8") as f:
        story = json.load(f)

    title = story.get("title", "Dark History Short")
    scenes = story.get("scenes", [])

    # Combine text for voiceover
    full_text = " ".join([scene.get("text", "") for scene in scenes])
    
    # Generate natural voice using gTTS (Google Text-to-Speech)
    print("Generating natural voiceover using gTTS...")
    tts = gTTS(text=full_text, lang='en', slow=False)
    audio_path = OUT / "voice.mp3"
    tts.save(str(audio_path))

    # Get audio duration using ffprobe
    result = run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of",
        "default=noprint_wrappers=1:nokey=1", str(audio_path)
    ], capture_output=True, text=True)
    
    duration = float(result.stdout.strip())

    # Create simple background card images for scenes
    images = []
    for i, scene in enumerate(scenes):
        img_path = OUT / f"scene_{i:02d}.jpg"
        
        # Create a dark cinematic background image (1080x1920 for Shorts)
        img = Image.new('RGB', (1080, 1920), color=(15, 15, 15))
        draw = ImageDraw.Draw(img)
        
        text = scene.get("text", "")
        # Simple text wrapping / drawing logic
        draw.text((100, 900), text, fill=(255, 255, 255))
        
        img.save(str(img_path))
        images.append(img_path)

    # Create image list file for ffmpeg concatenation
    concat_file = OUT / "images.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        each_duration = duration / len(images)
        for p in images:
            f.write(f"file '{p.as_posix()}'\n")
            f.write(f"duration {each_duration:.4f}\n")
        f.write(f"file '{images[-1].as_posix()}'\n")

    video_output = OUT / "dark_history_short.mp4"

    # Compile video with ffmpeg using the new natural voiceover
    print("Compiling video with FFmpeg...")
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-i", str(audio_path), "-vf", "fps=30,format=yuv420p",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "25",
        "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart",
        str(video_output)
    ])

    print(f"Video successfully ban gayi: {video_output} ({duration:.1f} sec)")

if __name__ == "__main__":
    make_video()
    
