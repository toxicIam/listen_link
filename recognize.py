import os
import tempfile
import uuid
from pydub import AudioSegment
import yt_dlp
from shazamio import Shazam


def download_audio_snippet(url: str, duration_sec=15) -> str:
    temp_dir = tempfile.gettempdir()
    audio_filename = os.path.join(temp_dir, f"{uuid.uuid4()}.mp3")

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

    # Поиск и обрезка mp3
    real_mp3_path = audio_filename
    for file in os.listdir(temp_dir):
        if file.endswith(".mp3") and file.startswith(os.path.basename(audio_filename).split('.')[0]):
            real_mp3_path = os.path.join(temp_dir, file)
            break

    audio = AudioSegment.from_file(real_mp3_path)
    snippet = audio[:duration_sec * 1000]
    snippet_path = os.path.join(temp_dir, f"snippet_{uuid.uuid4().hex}.mp3")
    snippet.export(snippet_path, format="mp3")

    os.remove(real_mp3_path)

    return snippet_path


async def recognize_with_shazam(file_path: str) -> dict:
    shazam = Shazam()
    out = await shazam.recognize_song(file_path)
    return out
