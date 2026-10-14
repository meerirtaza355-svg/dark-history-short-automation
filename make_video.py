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

    # Load story.json
    if not os.path.exists("story.json"):
        raise FileNotFoundError("story.json file nahi mili!")
        
    with open("story.json", "r", encoding="utf-8") as f:
        story = json.load(f)

    scenes = story.get("scenes", []) if isinstance(story, dict) else story
    title = story.get("title", "Dark History Short") if isinstance(story, dict) else "Dark History Short"

    text_list = []
    image_urls = []
    for scene in scenes:
        if isinstance(scene, dict):
            text_list.append(scene.get("text", ""))
            image_urls.append(scene.get("image_url", ""))
        else:
            text_list.append(str(scene))
            image_urls.append("")

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

    # Download and process cinematic background images for each scene
    images = []
    for i, (scene_text, img_url) in enumerate(zip(text_list, image_urls)):
        img_path = OUT / f"scene_{i:02d}.jpg"
        
        try:
            if img_url:
                print(f"Downloading image {i+1} from web...")
                response = requests.get(img_url, timeout=15)
                img = Image.open(BytesIO(response.content)).convert("RGB")
            else:
                raise Exception("No URL provided")
        except Exception as e:
            print(f"Image download failed ({e}), using dark cinematic fallback.")
            img = Image.new('RGB', (1080, 1920), color=(10, 10, 10))

        # Crop and resize to 9:16 vertical shorts format (1080x1920)
        img = ImageOps.fit(img, (1080, 1920), method=Image.Resampling.LANCZOS)
        
        # Add a dark gradient/tint overlay over the image for dramatic effect & text readability
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 120))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

        # Draw the caption text cleanly in the middle/lower area
        draw = ImageDraw.Draw(img)
        
        # Simple text wrapping logic for display
        words = scene_text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line + " " + word) <= 28:
                current_line = (current_line + " " + word).strip()
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        # Draw lines centered on screen
        y = 900
        for line in lines:
            # Drawing text with shadow effect for professional look
            draw.text((52, y+2), line, fill=(0, 0, 0))
            draw.text((50, y), line, fill=(255, 255, 255))
            y += 70

        img.save(str(img_path))
        images.append(img_path)

    # Create image list file for ffmpeg
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
    print("Compiling professional video with FFmpeg...")
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-i", str(audio_path), "-vf", "fps=30,format=yuv420p",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
        str(video_output)
    ], check=True)

    if not video_output.exists():
        raise FileNotFoundError("Video file create nahi ho saki!")

    print(f"Professional Video successfully ban gayi: {video_output} ({duration:.1f} sec)")

if __name__ == "__main__":
    make_video()
