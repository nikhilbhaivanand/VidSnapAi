# VidSnapAi
AI-powered reel generator: turn your photos and a text script into a vertical video with AI voiceover. Built with Flask, FFmpeg and ElevenLabs.
# VidSnapAi 🎬

VidSnapAi creates short vertical reels (1080x1920) from your photos.
Upload images, write a script, and the app adds an AI voiceover and builds the video automatically.

## Features
- Upload multiple images (JPG, PNG, WEBP)
- Text-to-speech voiceover using ElevenLabs
- Automatic reel generation with FFmpeg
- Gallery page to watch all created reels
- Works even if voiceover fails (video is made without audio)

## Tech Stack
Python, Flask, FFmpeg, ElevenLabs API, HTML/CSS

## How it works
1. User uploads images and text on the `/create` page.
2. `main.py` saves them in `user_uploads/<id>/`.
3. `generate_process.py` (background worker) creates the voice and then the video with FFmpeg.
4. The finished reel appears in `/gallery`.

## Setup
1. Install Python and [FFmpeg](https://ffmpeg.org/download.html)
2. Install dependencies:
python -m pip install -r requirements.txt

3. Set your ElevenLabs API key (PowerShell):

$env:ELEVENLABS_API_KEY="your_key_here"

4. Run the worker in one terminal:

python generate_process.py

5. Run the website in another terminal:

python main.py

6. Open http://127.0.0.1:5000

## Note
Never commit your API key. It is read from the `ELEVENLABS_API_KEY` environment variable.

## Author
Made by VANAND NIKHIL.
