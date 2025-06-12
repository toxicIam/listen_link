import os
import tempfile
import uuid
from pydub import AudioSegment
import yt_dlp
import subprocess
import json

from shazamio import Shazam

def download_with_gallery_dl(url: str) -> str:
    temp_dir = tempfile.gettempdir()
    out_dir = os.path.join(temp_dir, f"gallery_{uuid.uuid4().hex}")
    os.makedirs(out_dir, exist_ok=True)

    try:
        subprocess.run(
            ["gallery-dl", "--dest", out_dir, url],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        for root, _, files in os.walk(out_dir):
            for file in files:
                if file.endswith(".mp3") or file.endswith(".m4a") or file.endswith(".wav"):
                    return os.path.join(root, file)

    finally:
        pass  # оставим папку, так как используем путь

    raise Exception("Не удалось извлечь аудио через gallery-dl")

def download_audio_snippet(url: str, duration_sec=15) -> str:
    try:
        temp_dir = tempfile.gettempdir()
        audio_filename = os.path.join(temp_dir, f"{uuid.uuid4()}.mp3")

        # Попытка стандартного способа через yt_dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_filename.replace('.mp3', '.%(ext)s'),
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        real_mp3_path = audio_filename
        for file in os.listdir(temp_dir):
            if file.endswith(".mp3") and file.startswith(os.path.basename(audio_filename).split('.')[0]):
                real_mp3_path = os.path.join(temp_dir, file)
                break

    except Exception:
        # Fallback через gallery-dl
        real_mp3_path = download_with_gallery_dl(url)

    # Обрезка аудио
    audio = AudioSegment.from_file(real_mp3_path)
    snippet = audio[:duration_sec * 1000]
    snippet_path = os.path.join(temp_dir, f"snippet_{uuid.uuid4().hex}.mp3")
    snippet.export(snippet_path, format="mp3")

    if os.path.exists(real_mp3_path):
        os.remove(real_mp3_path)

    return snippet_path

async def recognize_with_shazam(file_path: str) -> dict:
    shazam = Shazam()
    out = await shazam.recognize(file_path)
    return out
