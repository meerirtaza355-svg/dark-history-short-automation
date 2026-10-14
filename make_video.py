import os
import json
import random
from pathlib import Path
from subprocess import run
from gtts import gTTS
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageOps

# Built-in viral dark history stories bank
STORIES_BANK = [
    {
        "title": "The Terrifying Secret of the Bronze Bull 🐂 #shorts",
        "description": "Discover the dark history of the ancient Bronze Bull of Phalaris, a horrific torture device designed in ancient Greece. #history #darkhistory #shorts",
        "tags": ["Shorts", "History", "DarkHistory", "AncientGreece"],
        "scenes": [
            {
                "text": "In ancient Greece, a ruthless ruler commissioned a hollow statue made entirely of solid bronze.",
                "image_url": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=1080&auto=format&fit=crop&q=80"
            },
            {
                "text": "Criminals and enemies were locked alive inside the iron belly of the beast.",
                "image_url": "https://images.unsplash.com/photo-1514539079130-25950c84af65?w=1080&auto=format&fit=crop&q=80"
            },
            {
                "text": "A massive fire was lit underneath, slowly roasting the victims alive inside.",
                "image_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1080&auto=format&fit=crop&q=80"
            },
            {
                "text": "The statue was acoustically engineered so their screams sounded like an enraged bull's roar.",
                "image_url": "https://images.unsplash.com/photo-1513584684374-8bab748fbf90?w=1080&auto=format&fit=crop&q=80"
            },
            {
                "text": "In a twisted turn of fate, its creator was the very first person locked inside.",
                "image_url": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=1080&auto=format&fit=crop&q=80"
            }
        ]
    },
    {
        "title": "The Real Dracula: Vlad the Impaler 🧛‍♂️ #shorts",
        "description": "The true dark history of Vlad the Impaler, the ruthless ruler who inspired the legend of Dracula. #history #darkhistory #dracula #shorts",
        "tags": ["Shorts", "History", "DarkHistory", "Dracula"],
        "scenes": [
            {
                "text": "Long before Bram Stoker's fiction, Vlad III ruled Wallachia with unmatched terror.",
                "image_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1080&auto=format&fit=crop&q=80"
            },
            {
                "text": "He famously invited hundreds of corrupt nobles to a feast, only to slaughter them all.",
                "image_url": "https://images.unsplash.com/photo-1514539079130-25950c84af65?w=1080&auto=format&fit=crop&q=80"
            },
            {
                "text": "His favorite method of execution earned him the chilling nickname The Impaler.",
                "image_url": "https://images.unsplash.com/photo-1513584684374-8bab748fbf90?w=1080&auto=format&fit=crop&q=80"
            },
            {
                "text": "It is said he once dined calmly in front of a forest of thousands of impaled bodies.",
                "image_url": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=1080&auto=format&fit=crop&q=80"
            },
            {
                "text": "Even invading armies turned back in pure horror upon seeing his gruesome warning fields.",
                "image_url": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=1080&auto=format&fit=crop&q=80"
            }
        ]
    },
    {
        "title": "The Terrifying Iron Maiden Device ⛓️ #shorts",
        "description": "Inside the medieval torture device known as the Iron Maiden. The dark history of medieval punishments. #history #darkhistory #torture #shorts",
        "tags": ["Shorts", "History", "DarkHistory", "Medieval"],
        "scenes": [
            {
                "text": "During the medieval ages, inventors designed some of the most horrific devices in human history.",
                "image_url": "https://images.unsplash.com/photo-1514539079130-25950c84af65?w=1080&auto=format&fit=crop&q=80"
            },
            {
                "text": "The Iron Maiden was an upright iron cabinet lined with sharp spikes inside.",
                "image_url": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=1080&auto=format&fit=crop&q=80"
            },
            {
                "text": "When the heavy doors slowly closed, the spikes would pierce the victim without hitting vital organs.",
                "image_url": "https://images.unsplash.com/photo-1513584684374-8bab748fbf90?w=1080&auto=format&fit=crop&q=80"
            },
            {
                "text": "This ensured that the agonizing torture lasted for hours in absolute darkness.",
                "image_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1080&auto=format&fit=crop&q=80"
            },
            {
                "text": "It remains one of the darkest symbols of medieval cruelty and paranoia.",
                "image_url": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=1080&auto=format&fit=crop&q=80"
            }
        ]
    }
]

def make_video():
    OUT = Path("output").resolve()
    OUT.mkdir(exist_ok=True)

    # Pick a dynamic story automatically
    story = random.choice(STORIES_BANK)

    # Save active story for upload_youtube.py
    with open("story.json", "w", encoding="utf-8") as f:
        json.dump(story, f, indent=2)

    scenes = story.get("scenes", [])
    text_list = [scene.get("text", "") for scene in scenes]
    image_urls = [scene.get("image_url", "") for scene in scenes]

    full_text = " ".join(text_list)
    print(f"Generating video for topic: {story.get('title')}")

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

        # Bottom positioned captions
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

    print(f"Video created successfully: {video_output}")

if __name__ == "__main__":
    make_video()
