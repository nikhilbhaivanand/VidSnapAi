# Looks for new folders inside user_uploads and converts them to a reel if not already converted.
import os
import re
import subprocess
import time
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

UPLOADS = "user_uploads"
REELS = os.path.join("static", "reels")
os.makedirs(UPLOADS, exist_ok=True)
os.makedirs(REELS, exist_ok=True)
for fn in ("done.txt", "failed.txt"):
    if not os.path.exists(fn):
        open(fn, "w").close()


def read_list(fn):
    with open(fn) as f:
        return {line.strip() for line in f if line.strip()}


def text_to_audio(folder):
    """Returns True if a usable audio.mp3 was created, else False (video is made without voice)."""
    audio_path = f"{UPLOADS}/{folder}/audio.mp3"
    with open(f"{UPLOADS}/{folder}/desc.txt", encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        return False
    try:
        from text_to_audio import text_to_speech_file
        text_to_speech_file(text, folder)
    except Exception as e:
        print(f"TTS failed for {folder}: {e}")
        return False
    return os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000


VF = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"


def normalize_images(folder):
    """Convert every image to a same-size JPG (ffmpeg's concat breaks when jpg/webp/png are mixed)."""
    src = f"{UPLOADS}/{folder}"
    norm = f"{src}/_norm"
    os.makedirs(norm, exist_ok=True)
    with open(f"{src}/input.txt", encoding="utf-8") as f:
        names = re.findall(r"^file '(.*)'\s*\n\s*duration", f.read(), flags=re.M)
    lines = []
    for i, name in enumerate(names):
        out = f"{norm}/{i}.jpg"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{src}/{name}",
                        "-vf", VF, "-frames:v", "1", "-q:v", "2", out], check=True)
        lines.append(f"file '{i}.jpg'\nduration 1\n")
    lines.append(f"file '{len(names) - 1}.jpg'\n")   # concat ignores the last duration
    with open(f"{norm}/list.txt", "w") as f:
        f.writelines(lines)
    return f"{norm}/list.txt"


def create_reel(folder, has_audio):
    listfile = normalize_images(folder)
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listfile]
    if has_audio:
        cmd += ["-i", f"{UPLOADS}/{folder}/audio.mp3"]
    cmd += ["-c:v", "libx264", "-r", "30", "-pix_fmt", "yuv420p"]
    if has_audio:
        cmd += ["-c:a", "aac", "-shortest"]
    cmd += [f"{REELS}/{folder}.mp4"]
    subprocess.run(cmd, check=True)
    print("CR - ", folder)


if __name__ == "__main__":
    while True:
        print("Processing queue...")
        done = read_list("done.txt") | read_list("failed.txt")
        for folder in sorted(os.listdir(UPLOADS)):
            path = os.path.join(UPLOADS, folder)
            # input.txt is written last by main.py, so its presence means the upload is complete
            if folder in done or not os.path.isdir(path) or not os.path.exists(os.path.join(path, "input.txt")):
                continue
            try:
                has_audio = text_to_audio(folder) if os.path.exists(os.path.join(path, "desc.txt")) else False
                create_reel(folder, has_audio)
                with open("done.txt", "a") as f:
                    f.write(folder + "\n")
            except Exception:
                traceback.print_exc()
                with open("failed.txt", "a") as f:   # don't retry forever; delete the line to retry
                    f.write(folder + "\n")
        time.sleep(10)
